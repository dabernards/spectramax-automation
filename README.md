Goal is to have a python script to easily process absorbance data generated from spectrophotometer.

[Data Flow]
Find pairs of .txt and .spec files -- these will be processed
Collect data into dictionaries
  - collect blanks into one array -- generate average to subtract background
  - collect standards into a dictionary with concentrations as keys and absorbance as values
  - overall dictionary contains device ID key and dictionary data (where keys are timepoint and value is absorbance)
Generate standard curve from blank and standards
Convert absorbance to concentration
Calculate average and standard deviations for all time points
Output dictionaries with each line being a device ID --> do this for absorbance and concentration
Combine output dictionaries to generate concentration data over multiple plates
  - collect all output files for aggregation
  - convert from dictionary style to tab delimited output


Add output of conc and standard file w/ fit and intercept

[Input File (.txt)]
Data appears as a text file with headers. Can have multiple plates per .txt.
Initially process single plate, but should be extendable to multiple.
One function should pass in file location and return array with AxB array based on plate size

[Specification File (.spec)]
For each well of plate, should have sample ID, type (elution, standard, others?), relevant data

For standards, header can specify concentration units of relevant detail
For elution, time unit is specified by rightmost character of relevant detail
For unused, use it can be empty (i.e. '') or 'jnk'
May add other data processing types as needed.

Dilutions will have to added as a later improvement, possibly as an additional file.

