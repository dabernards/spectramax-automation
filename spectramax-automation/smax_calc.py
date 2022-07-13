#!/usr/bin/env python3
''' Processes SpectraMax data and associated user-generate plate specification




'''
from fileops import data_load, spec_load

import sys
#import os
#import time
#import re
#import json
#import argparse ## https://docs.python.org/3/library/argparse.html
#import yaml
#import matplotlib.pyplot as plt
import numpy as np
import scipy.stats


class SmaxData:
    ''' Basic functions for a plate reader data set '''

    def __init__(self, filename):
        self._plate_data = data_load(filename)
        self._plate_spec = spec_load(filename)

        self.conc_std, self.abs_std, self.abs_blk = self._load_stds()
        self.std_avg, self.blk_avg = self._average_abs()
        self.data = self._load_data()

    def _load_stds(self):
        ''' Function pulls all concentration-standard data from data set

            Returns:
                Sorted concentration and absorbance lists
        '''

        # Creates list of tuples w/ format and absorbance
        combined_data = [x for y,z in zip(self._plate_spec ,self._plate_data) for x in zip(y,z)]

        conc_std = sorted({float(x[4:]) for x, _ in combined_data if x.startswith("std-")})

        abs_std = [ [ ab for fmt, ab in combined_data if \
                        fmt.startswith('std-') and float(fmt[4:])==conc ]\
                        for conc in conc_std ]

        abs_blk = [ ab for fmt, ab in combined_data if fmt=='blk']

        return conc_std, abs_std, abs_blk

    def _load_data(self):
        ''' Function pulls all concentration-standard data from data set
            INCOMPLETE
            Returns:
                Sorted concentration and absorbance lists
        '''

        # Creates list of tuples w/ format and absorbance
        combined_data = [x for y,z in zip(self._plate_spec ,self._plate_data) for x in zip(y,z)]

        sample_list = {x.split('-')[0] for x, _ in combined_data \
                            if x[:3] not in ('jnk', 'blk', 'std')}

        sample_abs = { sample: [ ab for fmt, ab in combined_data if sample.split('-') ] \
                        for sample in sample_list }

        return sample_abs


    def _truncate_stds(self, omit_lower, omit_upper):
        ''' Truncates standard curve on low/high end to provide better fit
        
            Args:
                -omit_lower, omit_upper: number of data points on upper and lower end of
                                    standard curve to omit
            Returns:
                conc_std, avg_std:  returns tuple of concentration and absorbance values
                                    omitting the input upper and lower limits
        '''

        return self.conc_std[omit_lower:len(self.conc_std)-omit_upper], \
                self.std_avg[omit_lower:len(self.conc_std)-omit_upper]

    def _average_abs(self):
        ''' Calcuate averages for absorbance and blanks '''

        return [np.mean(x) for x in self.abs_std], np.mean(self.abs_blk)


    def fit_linear(self, omit_lower=0, omit_upper=0):
        ''' Collect and organize standards for fit """

            Args:
                - omit_lower, omit_upper: optionally truncate data

            Returns:
                intercept, slope
        '''

        ydata, xdata = self._truncate_stds(omit_lower, omit_upper)
        fit_results = scipy.stats.linregress(xdata - self.blk_avg, ydata)

        return fit_results.intercept, fit_results.slope




        ''' Collect and organize standards for fit """
            
            Args:
                - std_data: dictionary of standards and absorbance data
                - abs_blk: list of absorbance values for blank wells
                - plot_data: boolean on whether to plot data using matplotlib

        '''
        # Pass in raw standard data and averaged blk values from checkBlank()
        # [FUTURE FEATURE] omit_outlier gives option to find outliers (will need to define)
        # and omit from fitting
        # Average all abs_in data
        #conc_std = [key for key in raw_std]

        '''
        conc_std = list(raw_std.keys())
        abs_std = [(np.mean(raw_std[key]) - abs_blk) for key in raw_std]
        abs_std_sd = [(np.std(raw_std[key])) for key in raw_std]

        # Sort, keyed on conc_std -- probably a cleaner way to do this...
        sorted_list = np.argsort(conc_std)
        abs_std = [abs_std[x] for x in sorted_list]
        # abs_std_sd currently is not in use
        _ = [abs_std[x] for x in sorted_list]
        conc_std = [conc_std[x] for x in sorted_list]

        # Will want to add some fit options here, check out :
        # https://scipy-cookbook.readthedocs.io/items/FittingData.html
        # Adding in finding outliers will be tricky, this might require user input
        # or something more advanced
        fit_results = scipy.stats.linregress(abs_std[omit_lower:len(abs_std)-omit_upper], \
            conc_std[omit_lower:len(abs_std)-omit_upper])

        if not cli_input['no_fit']:
            writeFitData(file, conc_std, abs_std, fit_results.slope, fit_results.intercept)
        if plot_data:
            _ = plt.plot(abs_std, conc_std, 'o', label='Original data', markersize=10)
            _ = plt.plot(abs_std, [fit_results.slope * x + fit_results.intercept for x in abs_std], \
                'r', label='Fitted line')
            _ = plt.legend()
            _ = plt.loglog()
            plt.show()
        '''



def process_data(plate_data, plate_format):
    """ process data into blanks, standards, and raw data"""
    loc_blk = []
    loc_std = {}
    loc_data = {}
    # Iterate through data in .spec to bucket standards, blanks, and data
    for row, _ in enumerate(plate_format):
        for col, plate_item in enumerate(plate_format[row]):
            data_type = plate_item[0:3]

            # blanket failsafe -- if entry is blank or user goes out of the way to enter 'jnk',
            # ignore it.
            if data_type in ("", "jnk"):
                continue

            # blk locations go into loc_blk
            if data_type == "blk":
                loc_blk.append([row, col])

            # std locations go into loc_std -- since concentrations can be anything,
            # a dictionary is used. If a key exists in the dictionary already --
            # just append it to the existing array, otherwise an array with the
            # first entry is required.
            elif data_type == "std":
                if float(plate_item[4:]) not in loc_std:
                    loc_std[float(plate_item[4:])] = []
                loc_std[float(plate_item[4:])].append([row, col])

            # all other items are considered data and go into loc_data
            else:
                data_dilution = 1
                [data_name, params] = plate_item.split('-')
                data_name = data_name.strip()
                for item in params.split('_'):
                    if item[0] == "d":
                        data_time = float(item[1:].strip())
                    elif item[0] == "x":
                        data_dilution = float(item[1:].strip())
                    elif item[0] == "n":
                        data_time = item[1:].strip()
                    else: pass #for now we just use these two parameters
                if data_name not in loc_data:
                    loc_data[data_name] = {}
                if data_time not in loc_data[data_name]:
                    loc_data[data_name][data_time] = []
                loc_data[data_name][data_time].append((row, col, data_dilution))

    raw_blk = [float(plate_data[row][col]) for [row, col] in loc_blk]

    ## FUTURE FEATURE -- checkBlank -- this should get integrated into checkBlank behavior

    # Put standards into raw_std dictionary
    raw_std = {}
    for key in loc_std:
        raw_std[key] = [float(plate_data[row][col]) for [row, col] in loc_std[key]]

    raw_data = {}
    dilution_data = {}
    for device_key in loc_data:
        raw_data[device_key] = {}
        dilution_data[device_key] = {}
        for time_key in loc_data[device_key]:
            raw_data[device_key][time_key] = \
                [float(plate_data[row][col]) \
                for (row, col, dilution) in loc_data[device_key][time_key]]
            dilution_data[device_key][time_key] = \
                [dilution for (row, col, dilution) in loc_data[device_key][time_key]]
    print(dilution_data)
  # Inelegant way, just want to flatten dilution data -- risky for unaware users
    for device_key in loc_data:
        for time_key in loc_data[device_key]:
            dilution_data[device_key][time_key] = np.mean(dilution_data[device_key][time_key])



    return raw_blk, raw_std, raw_data, dilution_data


def dataQC(json_data):
    """ perform quality analysis on data """
    bad_data = {}
    for device in json_data.keys():
        for item in json_data[device]:
            if item[1] <= check_lower * abs_std[0+omit_lower]:
                if device not in bad_data:
                    bad_data[device] = []
                bad_data[device].append(str(item[0]))
    return bad_data
