''' Basic manipulation tools for SpectraMax Data
    Currently in a major restructuring to be more amenable to cli and in-script use
    Better adaptation for use in 'data-as-code' methodology '''

#import os
import re
import yaml
import numpy as np
import scipy.stats


def load_plate(filename, trim_junk=True, return_locations=False):
    ''' Open the .txt file to load the data
        Spectramax encodes the degree symbol as \ufffd for some reason, which can't be
        parsed properly, so errors are handled with 'replace'
        By default, '' data in plate is removed, 
          if trim_junk is set to False, 8x12 array will be returned and data not coverted to float
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
            if trim_junk:
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


def load_spec(filename, delimiter='\t', trim_junk=True):
    ''' Open the .spec file to load specifications for the plate
        By default, delimiter for these files is a tab
        By default 'jnk' entries are removed unless trim_junk is set to False
        Since right/left & top/bottom data will be trimmed from plate_data,
        .spec should begin with upper left corner of data range.
    '''

    #Check filename is .spec
    if filename[-5:] != '.spec':
        filename = f"{filename}.spec"

    # Open the .spec file to load the plate formatting
    try:
        with open(filename, encoding='utf-8', errors="replace", mode="r") as handle:
            plate_format = [line.strip().split(delimiter) for line in handle if line.strip() != '']
        if trim_junk:
            plate_format = [ [ fcol for fcol in frow if not fcol.startswith('jnk')] \
                                    for frow in plate_format ]
    except FileNotFoundError:
        print(f"!!! Could not locate {filename}.spec -> FAIL !!!")

    return plate_format


def check_format(plate_data, plate_format):
    ''' check formatting of plate_data and plate_format match '''
    _is_format = [[ col != 'jnk' for col in row_format] for row_format in plate_format ]
    _is_data = [[ col != '' for col in row_data] for row_data in plate_data ]

    if len(_is_format) != len(_is_data) & len(*_is_format) != len(*_is_data):
        print("Data and format size mismatch")
        _is_matched=False
    else:
        # More rigorous analysis might be necessary
        _is_matched = True

    return _is_matched

def generate_blank(plate_data, plate_format):
    ''' generate array of blank absorbance values from plate

        The generator code to make a 1D array from a 2D source is a bit convoluted to read,
        but returning (name,data) will confirm it is functional
    '''

    _blk_data = [ data for frow,drow in zip(plate_format, plate_data) \
                    for name, data in zip(frow, drow) if name.startswith('blk')]

    return _blk_data

def generate_stds(plate_data, plate_format):
    ''' generate hash of std concentrations and absorbance data '''

    # Generate list of standard concentrations first
    _std_concs = { name.split('-')[1] for frow in plate_format \
                        for name in frow if name.startswith('std-') }

    # Then assemble array of all matching absorbance values
    _std_data = { float(_conc): [] for _conc in _std_concs}
    for _conc in _std_concs:
        _std_data[float(_conc)] = [ data for frow, drow in zip(plate_format, plate_data) \
                                for name, data in zip(frow, drow) if name==f'std-{_conc}' ]

    return _std_data

def generate_dataset(plate_data, plate_format):
    ''' generate hash of data names and absorbance
        data sets are composed on sample names
        each sample name can have subname (a time sequence, sample # or none)
        each sample name can have a dilution (assumed 1 if not)
        generated data set is therefor of format
        { name1: [(time, dilution), (subname, dilution),...],
          name2: [(subname, dilution), ...],
          name3: [(no-name, dilution), ...] }

     '''

    # Generate tuples containing full dataset as (name, time/subname/dilution, and abs data)
    _datalist = [ (*name.split('-'), data) for frow, drow in zip(plate_format, plate_data) \
                    for name, data in zip(frow,drow) if not name.startswith(('std', 'blk', 'jnk')) ]

    # Generate list of data names
    #_datanames = [ name for name, details, data in _datalist ]

    # For each primary data name, generate set of subnames
    #for dataname in _datanames:
    #    _dataset[dataname]['subnames'] = { tuple(details.split('_').sort()) for name, details, data in _datalist if name==dataname }


    return _datalist #_datanames, _dataset



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

