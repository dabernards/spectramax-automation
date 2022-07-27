#!/bin/env python3
''' File operations for handling SpectraMax data


'''

import sys
import re
import os
import yaml

def pair_files(filename):
    ''' check if filename has a txt and spec file pair for analysis
        Does not provide funcitionality to strip file extension

        Args:
            filename: The name of the root filename for SpectraMax and specification files

        Raises:
            ?

        Returns: True if both file types exist for given root filename
    '''
    try:
        return os.path.exists(f'{filename}.txt') and os.path.exists(f'{filename}.spec')
    except:
        print('Something went wrong')
        raise

def load_data(filename):
    ''' Load data from txt export from Spectramax software
        Ignoring errors required as first bit of Spectramax txt exports have issues

        Args:
            filename: The name of the file containing SpectraMax generated data.

        Raises:
            IOError: If ``filename`` does not exist or can't be read.

        Returns: 2 dimensional list corresponding to plate reader data
    '''
    try:

        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:   # pylint: disable=C0103
            raw_data = [line.split('\t') for line in f \
                if re.match('\t[1-9|\t]', line[0:2]) and line.strip() != '']
        plate_data = [ y[2:-2] for y in raw_data ]
        plate_data = [ [float(x) for x in y if x!=""] for y in plate_data if y!=['']*12 ]

        return plate_data

    except (ValueError, TypeError):     # pylint: disable=C0103
        print('Corruption in SpectraMax file suspected.'
             f' Non-numerical data in `{filename}`', file=sys.stderr)
        raise
    except IOError:        # pylint: disable=C0103
        print(f'Error reading file `{filename}`', file=sys.stderr)
        raise

def load_spec(filename):
    ''' Load data from spec file, which specifies layout of samples on plate
        Ignoring errors left for convenience in case user does something funny generating
        their spec file; shouldn't be necessary

        Args:
            filename: The name of the file containing plate layout specification.

        Raises:
            IOError: If ``filename`` does not exist or can't be read.

        Returns: 2 dimensional list corresponding to specification of plate layout
    '''
    try:
        with open(filename, encoding='utf-8', errors="ignore", mode='r') as f:    # pylint: disable=C0103
            plate_format = [line.strip().split('\t') for line in f if line.strip() != '']


        # Raise exception in any item contains more than 3 items
        if False in [ len(x.split('-'))<=2 for y in plate_format for x in y]:
            raise SpecFileError("Entry with incorrect formatting", plate_format)
        #print(test)

        return plate_format
    except IOError:        # pylint: disable=C0103
        print(f'Error reading file `{filename}`', file=sys.stderr)
        raise

def default_settings():
    ''' Generate a default settings dictionary

        Returns: Dictionary containing settings
    '''

    settings = {
        'delimiter': '\t',
        'omit_lower': 0, 'omit_upper': 1,
        'std_units': "\u03bcg/ml",
        'check_lower': 0.8, 'check_upper': 1.2,
        'file_list': [name[:-4] for name in os.listdir() \
            if name[-3:] == 'txt' and name[:-3]+'spec' in os.listdir()]
        }
    return settings

def generate_settings(filename='settings.yml'):
    ''' Generate a default settings file populated with relevant fields, return properties as dict.

        Args:
            filename: The name of the settings file to generate (settings.yml by default)

        Raises:
            FileExistsError: If specified settings file already exists

        Returns: Dictionary containing settings
    '''

    try:
        settings = default_settings()
        with open(filename, 'x', encoding='utf-8') as f:    # pylint: disable=C0103
            yaml.dump(settings, f)
        return settings

    except FileExistsError:        # pylint: disable=C0103
        print(f'`{filename}` already exists! Fresh `{filename}` not generated', file=sys.stderr)
        raise

def load_settings(filename='settings.yml', defaults_if_empty=False):
    """ Load settings from yaml file (defaulting to settings.yml)
        Generate a default settings file populated with relevant fields, return properties as dict.

        Args:
            filename: The name of the settings file to read (settings.yml by default)
            defaults_if_empty: when True return defaults if provided filename doesn't contain 
                               any settings

        Raises:
            IOError: Something went wrong reading file

        Returns: Dictionary containing settings, or raises exception
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:        # pylint: disable=C0103
            settings = yaml.load(f, Loader=yaml.Loader)

        if settings is None and defaults_if_empty:
            settings = default_settings()
        return settings
    except IOError:
        print('Something went wrong reading file', file=sys.stderr)
        raise

class SpecFileError(Exception):
    ''' Error is thrown if there are issues w/ specification file provided
    '''
    def __init__(self, text, plate_format):
        super().__init__(text)
        self._plate_format = plate_format

    @property
    def plate_format(self):
        return self._plate_format

    def _find_errors(self):
        ''' Provides user-readable row,column location if entry contains more than
            one ``-``
        '''
        error_locs = [(row+1,col+1) for row, y in enumerate(self._plate_format) \
                             for col, x in enumerate(y) if len(x.split('-'))>2]
        return error_locs

    def __str__(self):
        return (f"{self.args[0]}.\n\n"
                "Spec file has issues at following locations (row, colum):"
                "\n"+"\n".join([str(x) for x in self._find_errors()])
                )

    def __repr__(self):
        return f"SpecFileError({self.args[0]}, {self._plate_format}"

if __name__ == '__main__':
#    load_spec('good.spec')
    load_spec('bad.spec')

