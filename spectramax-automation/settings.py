#!/bin/env python3
''' Operations related to settings


'''
import sys
import os
import yaml

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

if __name__ == '__main__':
    default_settings()
    