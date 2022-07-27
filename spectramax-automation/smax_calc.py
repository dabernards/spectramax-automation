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

from fileops import load_data, load_spec
from fitting import LinearFit


class SmaxData:
    ''' Basic functions for a plate reader data set '''

    def __init__(self, filename):
        self.fit_result = []
        self.omit_lower = 0
        self.omit_upper = 0
        self._plate_data = load_data(f'{filename}.txt')
        self._plate_spec = load_spec(f'{filename}.spec')

        self.abs_blk = self._load_blk()
        self.conc_std, self.abs_std = self._load_stds()
        self.data = self._load_data()

    def flat_data(self):
        ''' Combines specification and data into single 1-D array

            Returns:
                List of tuples with specification and absorbance for each well
        '''
        return [x for y,z in zip(self._plate_spec ,self._plate_data) for x in zip(y,z)]

    def _load_blk(self):
        ''' Constructs list from all blank wells

            Returns:
                abs_blk: List of absorbance values for blank wells
        '''
        abs_blk = [ ab for fmt, ab in self.flat_data() if fmt=='blk']

        return abs_blk

    def _load_stds(self):
        ''' Constructs pair of list with concentration-standard data from
            data set, sorted based on concentration

            Returns:
                conc_std : Sorted list of concentration values
                abs_std: List of absorbance values to corresponding concentration
        '''

        conc_std = sorted({float(x[4:]) for x, _ in self.flat_data() if x.startswith("std-")})

        abs_std = [ np.mean([ ab for fmt, ab in self.flat_data() if \
                        fmt.startswith('std-') and float(fmt[4:])==conc ])\
                        for conc in conc_std ]

        return conc_std, abs_std

    def _load_data(self):
        ''' Constructions dictionary containing all sample data

            Returns:
                Sorted concentration and absorbance lists
        '''

        # Will fail if more than one '-' used in a spec entry, error handling should be in load_spec()
        simplified_data = [(*fmt.split('-'), ab) for fmt, ab in self.flat_data() \
                            if fmt[:3] not in ('jnk', 'blk', 'std')]

        sample_set = {sample: {y for x, y , _ in simplified_data if x==sample} \
                            for sample, _, _ in simplified_data}

        # This looks a bit convoluted, but does the job
        sample_data = { name: { self._extract_spec(z): \
                        [c for a,b, c in simplified_data if a==name and b==z] \
                            for z in y}  \
                            for name in list(sample_set) \
                            for x,y in sample_set.items() if x==name}

        return sample_data

    def _extract_spec(self, spec):
        ''' Process sample ID from spec file

            Args:
                - name: string from specification file to reduce

            Returns:
                - dilution: a dilution factor to be used, by default 1
                - number: float associated data point
                - name: name associated with data point
        '''
        name, number, dilution = None, None, 1

        try:
            ids = {x[0]: x[1:] for x in spec.split('_')}
            if 'x' in ids:
                dilution = float(ids['x'])
            if 'd' in ids:
                number = float(ids['d'])
            if 'n' in ids:
                name = ids['n']

        except IndexError:
            print("WARNING: No identifying information provided for sample.", sys.stderr)

        return name, number, dilution

    def _truncate_stds(self):
        ''' Truncates standard curve on low/high end to provide better fit

            Args:
                -omit_lower, omit_upper: number of data points on upper and lower end of
                                    standard curve to omit
            Returns:
                conc_std, avg_std:  returns tuple of concentration and absorbance values
                                    omitting the input upper and lower limits
        '''
        conc, absb = self._load_stds()
        return conc[self.omit_lower:len(conc)-self.omit_upper], \
                absb[self.omit_lower:len(absb)-self.omit_upper]
    """
    def _average_abs(self):
        ''' Calcuate averages for absorbance and blanks '''

        return [np.mean(x) for x in self.abs_std], np.mean(self.abs_blk)
    """

    def set_limits(self, omit_lower=0, omit_upper=0):
        ''' Adjust limits for lower and upper points to omit 
            Args:
                -omit_lower, omit_upper
            Returns:
                - None
        '''
        self.omit_lower = omit_lower
        self.omit_upper = omit_upper
        return None

    def func_linear(self, params, x):
        ''' Linear function for calculations '''
        return params[1]*x + params[0]


    def avg_blk(self):
        ''' Returns average blank-well absorbance '''
        return np.mean(self.abs_blk)

    def fit_linear(self):
        ''' Collect and organize standards for fit """

            Args:
                - omit_lower, omit_upper: optionally truncate data

            Returns:
                intercept, slope
        '''

        ydata, xdata = self._truncate_stds()
        #fit_result = scipy.stats.linregress(xdata - self.avg_blk(), ydata)
        params, self.fit_result = LinearFit().curve_fit(xdata, ydata)
        
        return params

    def calc_linear(self):
        ''' Performs calculations for linear regression of standard curve

            Args:
                - omit_lower, omit_upper: optionally truncate data

            Returns:
                conc_data: concentration data
        '''

        params = self.fit_linear()

        conc_data = { name: {tuple(t): n*self.func_linear(params, np.mean(b)-self.avg_blk()) for (*t,n),b in y.items()} \
                            for name in list(self.data) \
                            for x,y in self.data.items() if x==name}
        return conc_data



    def conc_time_sequence(self):
        ''' Returns condensed conc_data referenced as time sequence

        '''
        conc_data = self.calc_linear()
        time_data = { name: {x[1]: y for x,y in data.items()} \
                        for name, data in conc_data.items()}
        return time_data

    def conc_name_list(self):
        ''' Returns condensed conc_data referenced as time sequence

        '''
        conc_data = self.calc_linear()
        time_data = { name: {x[0]: y for x,y in data.items()} \
                        for name, data in conc_data.items()}
        return time_data

    def abs_time_sequence(self):
        ''' Returns condensed abs_data referenced as time sequence
            
            within a sample. each entry is time as a key with a tuple (abs, abs_sd, dil)
        '''
        abs_data = { name: {x[1]: (np.mean(y) - self.avg_blk(), np.std(y), x[2]) \
                        for x,y in data.items()} \
                        for name, data in self.data.items()}
        return abs_data
    def abs_name_list(self):
        ''' Returns condensed abs_data referenced as time sequence
            where each sample has an averaged absorbance

            will need to update to organizational standard of abs_time_seq
        '''
        abs_data = { name: {(a,c): \
                    np.mean([y for (d,e,f),y in self.data[name].items() if (a,c)==(d,f)]) \
                    for (a,b,c),y in self.data[name].items() } \
                    for name, data in self.data.items()}

        return abs_data


if __name__ == '__main__':
    data = SmaxData("/home/dab68/Sync/UCSF/Data"
                    "/220701 - ABS - TAc240 MF248 - TAc and MF elution"
                    "/20220701 - TAc240 - TAC1-4 TAc11-14 release")

#    print(data.data)
#    print(data.abs_name_list())
#    print(data.conc_name_list())
#    print(data.conc_time_sequence())
#    print(data.abs_name_list2())
#    print(data._load_stds())
    data.fit_linear()
    print(data.fit_result)

