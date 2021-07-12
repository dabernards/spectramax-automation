Goal is to have a python script to easily process absorbance data generated from spectrophotometer.

## Data Flow
1. Find pairs of .txt and .spec files -- these will be processed
1. Collect data into dictionaries
  - collect blanks into one array -- generate average to subtract background
  - collect standards into a dictionary with concentrations as keys and absorbance as values
  - overall dictionary contains device ID key and dictionary data (where keys are timepoint and value is absorbance)
3. Generate standard curve from blank and standards
1. Convert absorbance to concentration
1. Calculate average and standard deviations for all time points
1. Output dictionaries with each line being a device ID --> do this for absorbance and concentration
1. Combine output dictionaries to generate concentration data over multiple plates
  - collect all output files for aggregation
  - convert from dictionary style to tab delimited output

Add output of conc and standard file w/ fit and intercept

## Input File (.txt)
Exported SoftMax Pro data appears as a text file with headers. Can have multiple plates per .txt.
Currently only built process single plate, but should be extendable to multiple.
One function should pass in file location and return array with AxB array based on plate size

## Specification File (.spec)
For each well of plate, the well should have a sample ID, type (elution timepoint, standard, blank, junk, possibly others?).
This gets parsed in and used to part out the data from the Input file.

For wells that are unused, these can be left empty (i.e. '') or be populated with 'jnk'
[ ] Dilutions will have to added as a later improvement, possibly as an additional file.
[ ] Additional calculations will be added as a later improvement, such as mass, cumulative mass, rate, etc.

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
[ ] Need to add error handling if file.list does not exist
