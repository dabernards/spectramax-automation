''' Overarching description '''
import os
import re
import yaml
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt

class DataSettings:
    ''' Structure to deal with settings and cli parameters '''
    def __init__(self):
        self.settings = {
            'delimiter': '\t',
            'omit_lower': 0, 'omit_upper': 1,
            'elution_volume': 0.5, 'std_units': "\u03bcg/ml",
            'check_lower': 0.8, 'check_upper': 1.2,
            'file_list': [name[:-4] for name in os.listdir() \
                if name[-3:] == 'txt' and name[:-3]+'spec' in os.listdir()]
            }
        self.setting_file = "settings.yml"
        self.load_settings()

    def load_settings(self):
        """ Default settings provided here; settings.yml is loaded, for all variables
        loaded that appear in default settings will be loaded as global variables."""
        try:
            with open(self.setting_file, encoding="utf-8") as handle:
                _yaml_in = yaml.load(handle, Loader=yaml.Loader)
            if _yaml_in is None:
                raise NameError('EmptyFile')
            for item in _yaml_in:
                self.settings[item] = _yaml_in[item]
        except NameError:
            print("Settings file is empty -> default settings used.")
        except FileNotFoundError:
            print("Settings file not found -> default settings used.")

    def parse_cli(self):
        """ placeholder """
        print(self.settings)


class SpectraMaxData:
    ''' SpectraMax plate reader data processing architecture '''
    def __init__(self, filename):
        self.filename = filename
        self.plate_data = self.read_data()
        self.plate_format = self.read_format()
        self.raw_blk, self.abs_blk = self.obtain_blank()
        self.raw_std, self.abs_std = self.obtain_standards()
        self.omit_upper = 1
        self.omit_lower = 0
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

        conc_std, abs_std = self.sorted_standards()

        fit_results = scipy.stats.linregress(\
            abs_std[self.omit_lower:len(abs_std)-self.omit_upper], \
            conc_std[self.omit_lower:len(abs_std)-self.omit_upper])
        '''
        if not cli_input['no_fit']:
            writeFitData(file, conc_std, abs_std, fit_results.slope, fit_results.intercept)
        '''

        return fit_results



    def sorted_standards(self):
        ''' sort list '''
        # Sort, keyed on conc_std -- probably a cleaner way to do this...
        sorted_list = sorted(zip(self.abs_std.keys(), self.abs_std.values()))
        conc_std, abs_std = zip(*sorted_list)

        return conc_std, abs_std

    def plot_standards(self):
        '''plot things '''

        conc_std, abs_std = self.sorted_standards()

        _ = plt.plot(abs_std, conc_std, 'o', label='Original data', markersize=10)
        _ = plt.plot(abs_std, [self.fit_results.slope * conc + self.fit_results.intercept for conc in abs_std], \
            'r', label='Fitted line')
        _ = plt.legend()
        _ = plt.loglog()
        plt.show()
        return True
