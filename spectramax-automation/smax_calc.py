#!/usr/bin/env python3
''' Processes SpectraMax data and associated user-generate plate specification




'''
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

from fileops import data_load, spec_load



class SmaxData:
    ''' Basic functions for a plate reader data set '''

    def __init__(self, filename):
        self._plate_data = data_load(f'{filename}.txt')
        self._plate_spec = spec_load(f'{filename}.spec')

        self.abs_blk = self._load_blk()
        self.conc_std, self.abs_std = self._load_stds()
        self.std_avg, self.blk_avg = self._average_abs()
        self.data = self._load_data()

    def flat_data(self):
        ''' Combines specification and data into single 1-D array

            Returns:
                List of tuples with specification and absorbance for each well
        '''
        return [x for y,z in zip(self._plate_spec ,self._plate_data) for x in zip(y,z)]


    def _load_blk(self):
        ''' Function pulls all blank wells

            Returns:
                List of absorbance values for blank wells
        '''
        abs_blk = [ ab for fmt, ab in self.flat_data() if fmt=='blk']

        return abs_blk

    def _load_stds(self):
        ''' Function pulls all concentration-standard data from data set

            Returns:
                Sorted concentration and absorbance lists
        '''

        conc_std = sorted({float(x[4:]) for x, _ in self.flat_data() if x.startswith("std-")})

        abs_std = [ [ ab for fmt, ab in self.flat_data() if \
                        fmt.startswith('std-') and float(fmt[4:])==conc ]\
                        for conc in conc_std ]

        return conc_std, abs_std

    def _load_data(self):
        ''' Function pulls all concentration-standard data from data set
            INCOMPLETE
            Returns:
                Sorted concentration and absorbance lists
        '''

        # Creates list of tuples w/ format and absorbance
        combined_data = [x for y,z in zip(self._plate_spec ,self._plate_data) for x in zip(y,z)]

        simplified_data = [(*fmt.split('-'), ab) for fmt, ab in combined_data \
                            if fmt[:3] not in ('jnk', 'blk', 'std')]

        sample_set = {sample: {y for x, y , _ in simplified_data if x==sample} \
                            for sample, _, _ in simplified_data}

        # This looks a bit convoluted, but does the job
        sample_data = { name: { z: \
                        [c for a,b, c in simplified_data if a==name and b==z] \
                            for z in y}  \
                            for name in list(sample_set) \
                            for x,y in sample_set.items() if x==name}

        return sample_data

        def _process_name(self, name):
            ''' Process sample ID from spec file '''

            ids = name.split('_')

            return ids

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

    def calc_linear(self, omit_lower=0, omit_upper=0):
        ''' Performs calculations for linear regression of standard curve

            Args:
                - omit_lower, omit_upper: optionally truncate data

            Returns:
                conc_data: concentration data
        '''

        intercept, slope = self.fit_linear()

        conc_data = { name: {a: intercept + slope*np.mean(b) for a,b in y.items()} \
                            for name in list(self.data) \
                            for x,y in self.data.items() if x==name}

        return conc_data



'''

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
'''


if __name__ == '__main__':
    data = SmaxData("/home/dab68/Sync/UCSF/Data"
                    "/220701 - ABS - TAc240 MF248 - TAc and MF elution"
                    "/20220701 - TAc240 - TAC1-4 TAc11-14 release")
    print(data.calc_linear(0,0))
