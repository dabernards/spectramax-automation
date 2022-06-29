#!/bin/env python3
''' General functions to load plate and specification files

'''


import re
from os.path import exists

def pair_files(filename):
    ''' check if filename has a txt and spec file pair for analysis
        Does not provide funcitionality to strip file extension
    '''

    return exists(f'{filename}.txt') and exists(f'{filename}.spec')


def data_load(filename):
    ''' Load data from txt export from Spectramax software
        Ignoring errors required as first bit of Spectramax txt exports have issues
    '''

    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:   # pylint: disable=C0103
        raw_data = [line.split('\t') for line in f \
            if re.match('\t[1-9|\t]', line[0:2]) and line.strip() != '']
    plate_data = [ y[2:-2] for y in raw_data ]
    plate_data = [ [float(x) for x in y if x!=""] for y in plate_data if y!=['']*12 ]
    return plate_data

def spec_load(filename):
    ''' Load data from spec file, which specifies layout of samples on plate
        Ignoring errors left for convenience in case user does something funny generating
        their spec file; shouldn't be necessary
    '''
    with open(filename, encoding='utf-8', errors="ignore", mode='r') as f:    # pylint: disable=C0103
        plate_format = [line.strip().split('\t') for line in f if line.strip() != '']

    return plate_format

if __name__ == '__main__':
    pass
