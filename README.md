# README.md

This set of python code is used to quickly process SpectraMax txt data files. It is primarily designed with time-sequence data where each time point has one or more replicates. A Specification file is used to identify the sample in each well and data is output to a key-value JSON-type dictionary for ease of data aggregation across multiple plates and measurement dates.

## Dependencies

Code was developed using Python 3.8, so your mileage may vary if using an earlier Python version. Ensure the following are installed:

- python3 (3.8 or greater ideally). 
Installation information can be found at [python.org](https://www.python.org/downloads/)
- python packages numpy, scipy, pyyaml[^1].
Install packages using `python3 pip3 install numpy scipy pyyaml`

[^1]: pip is installed in python 3.4 or greater (check at command line with 'python3 -m pip --version')

## Data Processing Flow
1. Find pairs of .txt and .spec files in current directory -- these will be processed
1. Collect data into dictionaries
  - collect blanks into an array -- this average background is subtracted from all other wells
  - collect standards into a dictionary -- concentration and plate measurement are used for standard curve calculation
  - collect data into a dictionary -- for each device ID key a dictionary is generated, within this dictionary timepoints (or *names* for non-time sequence data) are populated with an array of raw measurements.
3. Average the standards at each concentration, subtract the background reading, and generate the standard curve
1. Average the raw measures from the data set, subtract the background reading, and convert plate measurement to concentration
1. Output a JSON dictionary containing the data set with device IDs and associated timepoints (or *names* for non-time sequence data)
1. Process JSON data in current directory or across multiple directories to generate concentration data over multiple plates
  - collect all output files for aggregation
  - convert from dictionary style to tab delimited output

Add output of conc and standard file w/ fit and intercept

## Input File (.txt)
Exported SoftMax Pro data appears as a text file with headers. Can have multiple plates per .txt.
Currently only built process single plate, but should be extendable to multiple.
One function should pass in file location and return array with AxB array based on plate size

## Specification File (.spec)
For each well of plate, the well should have a sample ID, type (elution timepoint, standard, blank, junk, possibly others?).
This gets parsed in and used to part out the data from the Input file. A detailed description of properly generating these files can be found in [Spec-files.md](Spec-files.md)



For wells that are unused, these can be left empty (i.e. '') or be populated with 'jnk'
- [ ] Dilutions will have to added as a later improvement, possibly as an additional file.
- [ ] Additional calculations will be added as a later improvement, such as mass, cumulative mass, rate, etc.

## settings.yml
Settings can be provided in a *settings.yml* file. Currently these include
- delimiter
  defaults to tab, can be any number of characters
- omit_lower
  number of data points to ignore when calculating the standard curve (starting from lowest concentration, excluding blank)
- omit_upper
  number of data points to ignore when calculating the standard curve (starting from highest concentration)
- elution_volume
  not currently implemented, but future feature will use this to calculate mass eluted
- file_list
  a list of files (without extension). When provided only the listed files will be processed. If a file list is not provided, a list of files with pairs of *.txt* and *.spec* files will automatically be populated.

## Combining elution data across many time points
Combining outputs is done in a folder with a file.list, which lists each file in relative path to combine.
- [ ] Need to add error handling if file.list does not exist
