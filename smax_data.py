''' Overarching description '''
import os
import re
import yaml
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt

def load_settings(settings_file="settings.yml"):
    ''' Structure to deal with settings and cli parameters
    Default settings provided here; settings.yml is loaded, for all variables
    loaded that appear in default settings will be loaded as global variables.'''
    settings = {
            'delimiter': '\t',
            'omit_lower': 0, 'omit_upper': 1,
            'elution_volume': 0.5, 'std_units': "\u03bcg/ml",
            'check_lower': 0.8, 'check_upper': 1.2,
            'file_list': [name[:-4] for name in os.listdir() \
                if name[-3:] == 'txt' and name[:-3]+'spec' in os.listdir()]
            }
    try:
        with open(settings_file, encoding="utf-8") as handle:
            _yaml_in = yaml.load(handle, Loader=yaml.Loader)
        if _yaml_in is None:
            raise NameError('EmptyFile')
        for item in _yaml_in:
            settings[item] = _yaml_in[item]
    except NameError:
        print("Settings file is empty -> default settings used.")
    except FileNotFoundError:
        print("Settings file not found -> default settings used.")
    return settings

def load_rawdata(filename):
    ''' Open the .txt file to load the data '''
    with open(filename + '.txt', encoding='utf-8', errors='ignore', mode='r') as handle:
        plate_data = [line.strip().split('\t') for line in handle \
            if re.match('\t[1-9|\t]', line[0:2]) and line.strip() != '']
    # Temperature does not have use in current implimentation and is dropped here
    _ = plate_data[0].pop(0)

    # Open the .spec file to load the plate formatting
    with open(filename + '.spec', encoding='utf-8', errors="ignore", mode="r") as handle:
        plate_format = [line.strip().split('\t') for line in handle if line.strip() != '']

    data_pairs = [ (name.strip(), float(data)) for name, data in \
        zip(np.array(plate_format).flatten(),np.array(plate_data).flatten()) ]

    # Raw data should contain blank wells, standards, and raw data
    raw_data = {'blank': [], 'standard': {}, 'data': {}}

    # Collecting blank wells is easy enough
    raw_data['blank'] = [ data for name, data in data_pairs if name.startswith('blk')]

    # First collect the standard concentrations the assemble the data
    std_concs = { name.split('-')[1] for name, data in data_pairs if name.startswith('std') }
    for conc in std_concs:
        raw_data['standard'][float(conc)] = \
            [ data for name, data in data_pairs if name.endswith('-' + conc) ]

    # Generate a set of tuples with samples and timepoints (deduplicate with a set)
    sample_set = {tuple(name.split('-')) for name, data in data_pairs \
                            if not name.startswith(('blk', 'std')) }
    raw_data['data'] = { sample: {} for sample, _ in sample_set}
    for sample, timepoint in sample_set:
        raw_data['data'][sample][float(timepoint.lstrip('d'))] = \
            [ data for name, data in data_pairs \
            if name.startswith(sample) and name.endswith('d' + timepoint)]

    return raw_data



class SpectraMaxData:
    ''' SpectraMax plate reader data processing architecture '''
    def __init__(self, filename):
        self.filename = filename
        self.plate_data = self.read_data()
        self.plate_format = self.read_format()
        self.raw_blk, self.abs_blk = self.obtain_blank()
        self.raw_std, self.abs_std = self.obtain_standards()
        self.omit_upper = 1 # from settings eventually
        self.omit_lower = 0 # from settings eventually
        self.fit_results = self.fit_standards()

    def read_data(self):
        ''' Open the .txt file to load the data '''
        with open(self.filename + '.txt', encoding='utf-8', errors='ignore', mode='r') as handle:
            _plate_data = [line.strip().split('\t') for line in handle \
                if re.match('\t[1-9|\t]', line[0:2]) and line.strip() != '']
        # Temperature does not have use in current implimentation and is dropped here
        _ = _plate_data[0].pop(0)
        return _plate_data


    def read_format(self):
        ''' Open the .spec file to load the plate formatting '''
        with open(self.filename + '.spec', encoding='utf-8', errors="ignore", mode="r") as handle:
            _plate_format = [line.strip().split('\t') for line in handle if line.strip() != '']
        return _plate_format


    def obtain_blank(self):
        ''' Generates array of blank well absorbance values '''
        _int_array = np.array(self.plate_format)

        _raw_blk = [float(self.plate_data[_row][_col]) \
            for (_row, _col), _item_format in np.ndenumerate(_int_array) \
            if _item_format == "blk"]
        try:
            _abs_blk = np.mean(_raw_blk)
        except RuntimeWarning:
            _abs_blk = 0
        return _raw_blk, _abs_blk


    def obtain_standards(self):
        ''' Generates array of blank well absorbance values '''
        _int_array = np.array(self.plate_format)
        _loc_std = {(_row, _col) \
            for (_row, _col), _item_format in np.ndenumerate(_int_array) \
            if _item_format[0:3] == "std"}
        _raw_std = {float(self.plate_format[_row][_col][4:]): [] for (_row, _col) in _loc_std}
        for _row, _col in _loc_std:
            _conc = float(self.plate_format[_row][_col][4:])
            _raw_std[_conc].append(float(self.plate_data[_row][_col]))
        try:
            _abs_std = {_conc: np.mean(_raw_std[_conc] - self.abs_blk) for _conc in _raw_std.keys()}
        except RuntimeWarning:
            print("No standards defined! Unable to process data without standards")
        return _raw_std, _abs_std



    def fit_standards(self):
        """ Collect and organize standards for fit """
        # Will want to add some fit options here, check out :
        # https://scipy-cookbook.readthedocs.io/items/FittingData.html
        # Adding in finding outliers will be tricky, this might require user input
        # or something more advanced

        sorted_list = sorted(zip(self.abs_std.keys(), self.abs_std.values()))
        conc_std, abs_std = zip(*sorted_list)

        fit_results = scipy.stats.linregress(\
            abs_std[self.omit_lower:len(abs_std)-self.omit_upper], \
            conc_std[self.omit_lower:len(abs_std)-self.omit_upper])

        return fit_results



    def sorted_standards(self):
        ''' sort list '''
        # Sort, keyed on conc_std -- probably a cleaner way to do this...
        sorted_list = sorted(zip(self.abs_std.keys(), self.abs_std.values()))
        conc_std, abs_std = zip(*sorted_list)

        return conc_std, abs_std

