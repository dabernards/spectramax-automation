#!/usr/bin/env python3
""" Automated processing of spectramax plate-reader data """
import sys
import os
import time
import re
import json
import argparse ## https://docs.python.org/3/library/argparse.html
import yaml
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats

DEBUG = False
# latest github version tag
CURRENT_VERSION = 1.1

VERBOSE_LOGS = True
parser = argparse.ArgumentParser(
    prog="automate.py",
    description='''
    !!!!!!!!!!!!!!!!! CLI Parameters partially implemented !!!!!!!!!!!!!!!
    Automated processing of SpectraMax .txt data files.
    By default, outputs standard curve fit, json formatted data, and log. 
    ''')
#to implement later
parser.add_argument('-i', '--input', metavar='file1 file2 ...', nargs='?', \
        help='Input files to process (overrides default/settings file list)')
parser.add_argument('-f', '--file-list', metavar='file', help='List of files to process')
# will need to change this default
parser.add_argument('-o', '--output', nargs='?', metavar='file', \
    help='Output data in table format (normally generated from json files with combine.py)')
parser.add_argument('-s', '--settings', nargs=1, metavar='file', default='settings.yml', \
    help='File to use in place of settings.yml')
parser.add_argument('--omit-lower', metavar='#', \
    help='Number of high concentration data points to omit from fit')
parser.add_argument('--omit-upper', metavar='#', \
    help='Number of low concentration data points to omit from fit')
parser.add_argument('--no-fit', action='store_true', \
    help='Do not generate standard curve output file')
parser.add_argument('--no-logs', action='store_true', \
    help='Do not generate logs')
parser.add_argument('-v', '--verbose', action='count', \
    help='Provide verbose output and logs')
parser.add_argument('-c', '--combine', action='store_true', \
    help='Combine all data into a single output file')
parser.add_argument('-p', '--plot', action='store_true', \
    help='Show plot of standard curve')
parser.add_argument('-d', '--no-data', action='store_true', \
    help='Only generate standard curve and do not process data')
parser.add_argument('--html', action='store_true', \
    help='Output list of files in HTML format')
parser.add_argument('--generate-settings', action='store_true', \
    help='Generate a generic settings.yml file')
parser.add_argument('--local-settings', action='store_true', \
    help='For each data file, use settings.yml in data directory')
parser.add_argument('--omit-local', action='store_true', \
    help='Do not generate output files for each file')
parser.add_argument('--check-lower', metavar='x', type=float, \
    help='In verbose mode, flag data that is within \
    factor of x of lowest standard curve data point')
parser.add_argument('--check-upper', metavar='x', type=float, \
    help='(not implemented) In verbose mode, flag data that is within \
    factor of x of highest standard curve data point')
parser.add_argument('--fit-only', action='store_true', \
    help='Do not generate output files for each file')
parser.add_argument('--dict', action='store_true', \
    help='Output combined data in json format')

cli_input = vars(parser.parse_args())
if False:
    print(cli_input)

def loadSettings(settings_file):
    """ Default settings provided here; settings.yml is loaded, for all variables
     loaded that appear in default settings will be loaded as global variables."""
    default_settings = {
        'delimiter': '\t',
        'omit_lower': 0, 'omit_upper': 1,
        'elution_volume': 0.5, 'std_units': "\u03bcg/ml",
        'check_lower': 0.8, 'check_upper': 1.2,
        'file_list': [name[:-4] for name in os.listdir() \
            if name[-3:] == 'txt' and name[:-3]+'spec' in os.listdir()]
        }
    try:
        yaml_in = yaml.load(open(settings_file), Loader=yaml.Loader)
        if yaml_in is None: raise Exception()
    except:
        yaml_in = default_settings
    try:
        with open(cli_input['file_list'], 'r') as f:
            yaml_in['file_list'] = [line.strip() for line in f if line.strip() != '']
    except:
        pass

  #CLI inputs take precident, won't be happy if omit_lower or upper is non-int
    for var in ['omit_lower', 'omit_upper']:
        if cli_input[var] is not None:
            yaml_in[var] = int(cli_input[var])
    for var in ['check_lower', 'check_upper']:
        if cli_input[var] is not None:
            yaml_in[var] = float(cli_input[var])

    for var in default_settings.keys():
        if var in yaml_in:
            globals()[var] = yaml_in[var]
        else:
            globals()[var] = default_settings[var]
        if DEBUG:
            print(var, globals()[var])

def generateSettings():
    """ Generate settings.yml file"""
    default_settings = {
        'delimiter': '\t',
        'omit_lower': 0, 'omit_upper': 1,
        'elution_volume': 0.5, 'std_units': "\u03bcg/ml",
        'check_lower': 0.8, 'check_upper': 1.2,
        'file_list': [name[:-4] for name in os.listdir() \
            if name[-3:] == 'txt' and name[:-3]+'spec' in os.listdir()]
        }
  ##should fail if this will overwrite settings

    try:
        with open('settings.yml', 'x') as f:
            yaml.dump(default_settings, f)
    except:
        print("Settings file already exists in this directory -- settings.yml not generated.")


def loadFiles(file):
    """ Load plate format and data for analysis"""
    # First bit of these text files is pesky, so ignore that initial error.
    # Unclear if this gets replicated in windows or mac. Open read only.
    # Matches against lines with double tab or tab and digit
    # (that's the start of the temperature); ignores empty lines,
    # strips whitespace and splits the by tab
    with open(f"{file}.txt", 'r', encoding='utf-8', errors='replace') as handle:
        raw_data = [line.split('\t') for line in handle \
            if re.match('\t[1-9|\t]', line[0:2]) and line.strip() != '']
    plate_data = [ y[2:-2] for y in raw_data ]
    plate_data = [ [float(x) for x in y if x!=""] for y in plate_data if y!=['']*12 ]

    # Read in comma delimited descriptor file
    with open(file + '.spec', errors="ignore", mode="r") as f:
        plate_format = [line.strip().split(delimiter) for line in f if line.strip() != '']
    # processing error if data doesn't start in column 1

    return plate_data, plate_format


def writeFitData(file, conc_std, abs_std, fit_slope, fit_int):
    """ Output fit results to file """
    with open(file + '.fit', 'w') as f:

        f.write("#Slope	#Intercept\n")
        f.write(str(fit_slope) + "\t" + str(fit_int) + "\n")
        f.write("#Conc	#Absorbance (blank substracted)\n")
        data_out = [[str(conc_std[x]), str(abs_std[x])] for x in range(len(conc_std))]
        for line in data_out:
            f.write("\t".join(line) + "\n")


def checkBlank(raw_blk, tolerance=1):
    """ Calculates average background absorbance """
    # FUTURE FEATURE -- can add some checks for outliers in the blanks
    # -- will need to trouble shoot a bit
    # tolerance is how many standard deviations away from the mean should be discarded
    if raw_blk != []:
        abs_blk = np.mean(raw_blk)
    else:
        abs_blk = float(0)


    return abs_blk


def fitStandards(raw_std, abs_blk, omit_lower, omit_upper, plot_data):
    """ Collect and organize standards for fit """
    # Pass in raw standard data and averaged blk values from checkBlank()
    # [FUTURE FEATURE] omit_outlier gives option to find outliers (will need to define)
    # and omit from fitting
    # Average all abs_in data
    #conc_std = [key for key in raw_std]
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

    return fit_results, conc_std, abs_std

def processData(plate_data, plate_format):
    """ process data into blanks, standards, and raw data"""
    print(plate_data)
    print(plate_format)
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

    raw_blk = [float(plate_data[row][col]) for row, col in loc_blk]

    ## FUTURE FEATURE -- checkBlank -- this should get integrated into checkBlank behavior

    # Put standards into raw_std dictionary
    raw_std = {}
    for key in loc_std:
        raw_std[key] = [float(plate_data[row][col]) for row, col in loc_std[key]]

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
  # Inelegant way, just want to flatten dilution data -- risky for unaware users
    for device_key in loc_data:
        for time_key in loc_data[device_key]:
            dilution_data[device_key][time_key] = np.mean(dilution_data[device_key][time_key])



    return raw_blk, raw_std, raw_data, dilution_data

def formatOutput(json_data, file, write_data=True):
    """ Format data in columned format from json """
    all_data = {}
    for device_key in json_data:
        time_in = []
        abs_in = []
        abs_sd_in = []
        conc_in = []
        dilution_in = []
        for i in range(len(json_data[device_key])):
            time_in.append(json_data[device_key][i][0])
            abs_in.append(json_data[device_key][i][1])
            abs_sd_in.append(json_data[device_key][i][2])
            conc_in.append(json_data[device_key][i][3])
            dilution_in.append(json_data[device_key][i][4])

        sorted_list = np.argsort(time_in)
        abs_in = [abs_in[x] for x in sorted_list]
        abs_in_sd = [abs_sd_in[x] for x in sorted_list]
        dilution_in = [dilution_in[x] for x in sorted_list]
        conc_in = [conc_in[x] for x in sorted_list]
        time_in = [time_in[x] for x in sorted_list]
        all_data[device_key] = [time_in, abs_in, abs_in_sd, conc_in, dilution_in]

    # Gives element of all_data with max size
    row_output = len(all_data[max(all_data, key=lambda k: len(all_data[k][0]))][0])
    data_out = [[] for x in range(row_output+1)]

    col_labels = ["day_", "abs_", "abs_sd_", "conc_", "dil_"]
    device_list = list(all_data.keys())
    device_list.sort()
    for device in device_list:
        data_out[0].extend([col_labels[x] + device for x in range(5)])

    for i in range(row_output):
        for device in device_list:
            if i >= len(all_data[device][0]):
                data_out[i+1].extend("" for i in range(5))
                continue
            data_out[i+1].extend(str(all_data[device][j][i]) for j in range(5))
    if write_data:
        with open(file + '.out', 'w') as f:
            for line in data_out:
                f.write("\t".join(line) + "\n")

    return data_out

def writeDictionary(raw_data, dilution_data, abs_blk, fit_results):
    """ output data in json format """
    # This is quick and dirty to enable combine.py processing. Can improve elegance here later.
    json_data = {}
    for device_key in raw_data:
        json_data[device_key] = []
        for time_key in raw_data[device_key]:
            time_in = time_key

            abs_in = np.mean(raw_data[device_key][time_key]) - abs_blk
            abs_sd_in = np.std(raw_data[device_key][time_key])
            dilution_in = dilution_data[device_key][time_key]
            conc_in = (fit_results.slope * abs_in + fit_results.intercept) \
                * dilution_data[device_key][time_key]
            json_data[device_key].append([time_in, abs_in, abs_sd_in, conc_in, dilution_in])
    with open(file + '.dict', 'w') as f:
        json.dump(json_data, f)

    return json_data

def generateLog():
    """ generate log file with relevant processing details """

    with open(file + '.log', 'w') as f:
    #date
    #script version
    #fit r^2
        f.write("############ automate.py v" + str(CURRENT_VERSION) + " #############\n")
        f.write("Calculations completed " \
            + time.strftime("%d %b %Y %H:%M:%S", time.localtime()) + "\n")
        f.write("\n----- Standard Curve Linear Regression ----\n")
        f.write("  R^2 = %0.5f\n" % fit_results.rvalue**2)
        f.write("  %1d data points excluded from lower end\n" % omit_lower)
        f.write("  %1d data points excluded from upper end\n" % omit_upper)
        f.write("\n  Units are ["+ std_units + "]\n\n")


    ## Generate table with Device names, and number of points, maybe actual days
    # any additional logging of value here

        if cli_input['verbose']:
            f.write("############### Data Check ################\n")
            f.write("The following are within %1.2f of the lower\n\
                end of the standard curve:\n\n" % check_lower)
            for device in bad_data:
                f.write(f"  {device} at data points " + ", ".join(bad_data[device]) + "\n")

def htmlOutput():
    """ generate list of files as html links """
    short_date = os.getcwd().split('/').pop(-1).split(' ').pop(0)
    year = '20' + short_date[0:2]
    month = short_date[2:4]

    output = []
    for file in os.listdir():
        if file.split('.').pop(-1) != 'xlsx':
            output.append(f'<a href="/wp-content/uploads/{year}/{month}/{file}">' \
                + file.split('.').pop(-1) + '</a>')
        else:
            output.append(f'<a href="/wp-content/uploads/{year}/{month}/{file}">excel</a>')
    print('(' + ', '.join(output)+')')

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

def verbose_output():
    """ provides additional results to STDOUT """
    print("\n################### Data Check ####################")
    print("The following are within %1.2f of the lower end of the standard curve:\n" % check_lower)
    for device in bad_data:
        print(f"{device} at data points " + ', '.join(bad_data[device]))
    print()

###################
if cli_input['generate_settings']:
    generateSettings()
    sys.exit()

if not cli_input['local_settings']:
    loadSettings(cli_input['settings'])
else:
    try:
        with open(cli_input['file_list'], 'r') as f:
            file_list = [line.strip() for line in f if line.strip() != '']
    except:
        pass

multi_data = {}

if cli_input['html']:
    htmlOutput()
    sys.exit()

for file in file_list:
    if cli_input['local_settings']:
        loadSettings(os.path.dirname(os.path.realpath(file))+"/settings.yml")

    plate_data, plate_format = loadFiles(file)
    raw_blk, raw_std, raw_data, dilution_data = processData(plate_data, plate_format)

    abs_blk = checkBlank(raw_blk)
    [fit_results, conc_std, abs_std] = \
        fitStandards(raw_std, abs_blk, omit_lower, omit_upper, cli_input['plot'])
    if cli_input['fit_only']:
        sys.exit()

    file_data = writeDictionary(raw_data, dilution_data, abs_blk, fit_results)

    if cli_input['combine']:
        for key in file_data:
            if key not in multi_data:
                multi_data[key] = []
            multi_data[key].extend(file_data[key])

    bad_data = dataQC(file_data)
    formatOutput(file_data, file)
    if cli_input['verbose'] and bad_data != {}:
        verbose_output()
    if not cli_input['no_logs']:
        generateLog()

if cli_input['combine']:
    for key in multi_data:
        multi_data[key].sort()
    formatOutput(multi_data, "all_data")
    if cli_input['dict']:
        with open('all_data.dict', 'w') as f:
            json.dump(multi_data, f)
