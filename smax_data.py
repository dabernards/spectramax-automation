''' Basic manipulation tools for SpectraMax Data
    Currently in a major restructuring to be more amenable to cli and in-script use
    Better adaptation for use in 'data-as-code' methodology '''

#import os
import re
import yaml
import numpy as np
import scipy.stats


def load_plate(filename, return_locations=False):
    ''' Open the .txt file to load the data
        Spectramax encodes the degree symbol as \ufffd for some reason, which can't be
        parsed properly, so errors are handled with 'replace'
        When return_locations is True, function returns 8x12 array with locations where
        data can be found.
        Function will return a larger array if txt file contains multiple plates
    '''

    # Confirms filename ends as .txt file and corrects extension if not
    if filename[-4:] != '.txt':
        filename = f"{filename}.txt"

    # Regular expression here matches lines that start w/ two tabs or a tab followed by number
    try:
        with open(filename, 'r', encoding='utf-8', errors='replace') as handle:
            _raw_data = [line.split('\t') for line in handle \
                if re.match('\t[1-9|\t]', line[0:2]) and line.strip() != '']

        # Plates will always include two leading columns and a tailing new-line character
        # By default, non-blank data is converted to a float
        if not return_locations:
            plate_data = [ y[2:-2] for y in _raw_data ]
            plate_data = [ [float(x) for x in y if x!=""] for y in plate_data if y!=['']*12 ]
        else:
            plate_data = [ [ x!="" for x in y[2:-2] ] for y in _raw_data ]

    except FileNotFoundError:
        print(f"!!! Could not locate {filename}.txt -- specify a file that exists !!!")
        plate_data = []

    return plate_data


def load_settings(settings_file="settings.yml"):
    ''' Settings to process data can be loaded from file
        Otherwise default settings are reverted to here
        Generating a file list should go elsewhere
            'file_list': [name[:-4] for name in os.listdir() \
        if name[-3:] == 'txt' and name[:-3]+'spec' in os.listdir()]
        '''
    settings = {
            'delimiter': '\t',
            'omit_lower': 0, 'omit_upper': 1,
            'check_lower': 0.8, 'check_upper': 1.2,
            'elution_volume': 0.5, 'std_units': "\u03bcg/ml"
            }

    try:
        with open(settings_file, encoding="utf-8") as handle:
            _yaml_in = yaml.load(handle, Loader=yaml.Loader)
        if _yaml_in is None:
            raise NameError('EmptyFile')
        for item in _yaml_in:
            settings[item] = _yaml_in[item]

    except NameError:
        print(f"!!! No settings in {settings_file} -> default settings used !!!")
    except FileNotFoundError:
        print(f"!!! Could not locate {settings_file} -> default settings used !!!")

    return settings


def load_spec(filename, delimiter='\t'):
    ''' Open the .spec file to load specifications for the plate
        By default, delimiter for these files is a tab
        Since right/left & top/bottom data will be trimmed from plate_data,
        .spec should begin with upper left corner of data range.
    '''

    # Open the .spec file to load the plate formatting
    with open(filename + '.spec', encoding='utf-8', errors="replace", mode="r") as handle:
        plate_format = [line.strip().split('\t') for line in handle if line.strip() != '']

    # Should add error checking on format of .spec items

    return plate_format



def load_rawdata(plate_data, plate_format):
    ''' from plate data and formatting, extract blank, standard, and data

    '''

    _data_pairs = [ (name.strip(), float(data)) for name, data in \
        zip(np.array(plate_format).flatten(),np.array(plate_data).flatten()) ]

    # Raw data should contain blank wells, standards, and raw data
    raw_data = {'blank': [], 'standard': {}, 'data': {}}

    # Collecting blank wells is easy enough
    raw_data['blank'] = [ data for name, data in _data_pairs if name.startswith('blk')]

    # First collect the standard concentrations the assemble the data
    _std_concs = { name.split('-')[1] for name, data in _data_pairs if name.startswith('std') }
    for conc in std_concs:
        raw_data['standard'][float(conc)] = \
            [ data for name, data in _data_pairs if name.endswith(f'-{conc}') ]

    # This version only handles time sequence info, should be more generic
    # Generate a set of tuples with samples and timepoints (deduplicate with a set)
    _sample_set = {tuple(name.split('-')) for name, data in _data_pairs \
                            if not name.startswith(('blk', 'std')) }
    raw_data['data'] = { sample: {} for sample, _ in _sample_set}
    for sample, timepoint in _sample_set:
        raw_data['data'][sample][float(timepoint.lstrip('d'))] = \
            [ data for name, data in _data_pairs \
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

