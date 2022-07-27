#!/usr/bin/env python3
''' Command line wrapper for smax-data processing tools



'''
import sys
import time
import argparse ## https://docs.python.org/3/library/argparse.html
from smax_calc import SmaxData

CURRENT_VERSION = 0.2

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

cli_input = vars(parser.parse_args())


def format_output(data, key_name=False, use_conc=True):
    ''' Format dictionary-based data in column format suitable for conventional csv output
        Defaults to data sorted by time where concentration is calculated

        Args:
            data: data set in form SmaxData container

        Raise:
            KeyError: if user selects sorting on name and time or neither

        Returns:
            output_str: string suitable for writing csv file
    '''

    all_samples = list(data.data)
    col_set =["t_" * (not key_name), "name" * key_name, \
                "abs_", "abs_sd_", \
                "dil_", "c_" * use_conc]

    # Header line
    output = '\t'.join([f"{sample}\t".join(x for x in col_set if x!="")+sample \
                            for sample in all_samples ]) \
                + '\n'

    avg_data = data.abs_time_sequence()
    conc_data = data.conc_time_sequence()
    time_data = {x: sorted(z for z in y) for x,y in avg_data.items() }

    combined_data = {x: [(y,)+avg_data[x][y]+(conc_data[x][y],) \
                    for y in time_data[x]] for x in time_data}

    max_len = max([len(x) for x in data.conc_time_sequence().values()]) * (not key_name) + \
                max([len(x) for x in data.conc_name_list().values()]) * (key_name)

    for i in range(max_len):
        line_data = [combined_data[x][i] for x in all_samples]
        line_strs = [str(y) for x in line_data for y in x]
        output += '\t'.join(line_strs) + '\n'

    return output

def write_data(output, filename, overwrite=False):
    '''  Generic function to write output to selected filename
        Will not overwrite existing file unless specified
    '''
    io = 'x'*(not overwrite) + 'w'*(overwrite)      #pylint: disable=C0103
    try:
        with open(filename, io, encoding='utf-8') as f:     #pylint: disable=C0103
            f.write(output)
    except FileExistsError:        # pylint: disable=C0103
        print(f'``{filename}`` already exists! '
                'To overwrite, pass `overwrite=True` to `write_data()`.', file=sys.stderr)
        raise

'''
    output_str = '\n'.join(lines)
    return output_str
'''


def format_log(data):
    """ generate log file with relevant processing details """

    return  ('############ smax-cli.py v" + str(CURRENT_VERSION) + " #############\n'
            f'Calculations completed {time.strftime("%d %b %Y %H:%M:%S", time.localtime())}\n'
            '\n----- Standard Curve Linear Regression ----\n'
            f'   R^2 = {data.fit_result.rvalue**2: 0.5f}\n'
            f'  {data.omit_lower: 1d} data points excluded from lower end\n'
            f'  {data.omit_upper: 1d} data points excluded from upper end\n')

    '''
    ## Generate table with Device names, and number of points, maybe actual days
    # any additional logging of value here

        if cli_input['verbose']:
            f.write("############### Data Check ################\n")
            f.write("The following are within %1.2f of the lower\n\
                end of the standard curve:\n\n" % check_lower)
            for device in bad_data:
                f.write(f"  {device} at data points " + ", ".join(bad_data[device]) + "\n")
    '''

'''
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
'''


'''
def verbose_output():
    """ provides additional results to STDOUT """
    print("\n################### Data Check ####################")
    print("The following are within %1.2f of the lower end of the standard curve:\n" % check_lower)
    for device in bad_data:
        print(f"{device} at data points " + ', '.join(bad_data[device]))
    print()
'''


if __name__ == '__main__':
    data_set = SmaxData("/home/dab68/Sync/UCSF/Data"
                    "/220701 - ABS - TAc240 MF248 - TAc and MF elution"
                    "/20220701 - TAc240 - TAC1-4 TAc11-14 release")
    data_file = format_output(data_set)
    write_data(data_file, '/tmp/output.csv', overwrite=True)
    print(format_log(data_set))

