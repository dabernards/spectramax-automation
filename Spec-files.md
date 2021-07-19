# Specification Files (*.spec*)

Specification files are used to define how the raw data in Spectramax *.txt* files is treated. By default these are tab-delimited files, where each entry begins with a sample/device ID followed by additional detail separated by a dash (*-*). For example:

```
std-10	Sample1-d1		Sample1-d1	Sample1-d3		Sample1-d3
std-5	Sample2-d1		Sample2-d3	jnk				blk
std-2	Sample4-nC_x10	Sample4-nA	Sample4-nB_x10	blk
```


**Note**: Both dash (-) and underscore (\_) are special characters in the *.spec* file. They are used in specific ways described below.

## Anatomy of *.spec* Files

For each entry in the *.spec* file, there are two parts referred to as *ID* and *properties* (except for in *blk* and *jnk* entries), which are separated by a dash as in *ID-properties*. 

From this list, it will parse out several different sample types/properties:

- Blank Wells (blk)
- Standards (std)
- Time-based samples
- Sub-named samples
- Samples with dilutions
- Junk or empty wells

## Blank Wells

Blank or background wells are defined by 'blk' and by definition do not have associated *properties*. Values are collected, averaged, and the average is subtracted from all standards to calculate the standard curve and from sample wells to determine sample concentrations. The average and standard deviation of blank wells is reported in the *log* file.[^a future feature will attempt to identify outliers and optionally remove them from the background wells]

## Standards

Standard wells are defined by 'std' and are specified with a single numerical *property*, which is the associated concentration for the standard curve. Decimal numbers are ok, but if text is passed in the properties an error will occur. Since it makes subsequent plotting or other analysis more complicated, units to do not transfer to calculated data files. Units for the standard curve default to *ug/ml* or can specified in the *settings.yml* file, which will be recorded in the *log* file for each data set. Curve is fit with a linear regression, where data points at the top or bottom end of the standard curve can be omitted if they are known to be outliers.[^a future feature will provide the option of showing a plot of the standard curve to confirm fit quality] Data points omitted are noted in the *log* file along with the R^2 for the fit.[^a future feature should include the absorbance and concentration range for the standard curve in the log]

## Sample Data

Sample wells are defined by an arbitrary 'samplename' and a number of possible 'samplesproperties' are described below. Extensive testing has not been performed on restrictions for samples name, but general text should work fine. For *sampleproperties* the following are currently implemented.

- **d#** -- date

Date in a time sequence, where the '#' is the number of the day (can be decimal).

- **x#** -- dilution

Often samples will be diluted to accurately assay. To automatically adjust calculated concentrations by a dilution factor, this is included with an **x** *property*. The **x** *property* is followed by a numerical value (can be decimal) that the calculated concentration is multiplied by prior to generating the data table. For example, *Sample1-d1_x10* will associate that well with *Sample1* at *day 1* and will adjust the concentration by a factor of 10.

- **n\*** -- sub-name

Non-time sequenced name. If you are not assaying a time sequence, you may want to have samples with a common grouping with sub-samples. Because each *samplename* will generate its own column of data, using this *sub-name* parameter will group this data set in a single column with each *sub-name* occupying one row. At present, the *sub-name* property is ignored if the *date* property is used.
*eg.* when trying to find an appropriate dilution that falls with the standard curve, you may have samples *A*, *B*, *C* with different dilutions -- if a sub-name is not specified, all dilutions would be averaged back together to generate a single concentration.

## Junk

Often a plate will have some wells with nonsense data. In this case, they can be left blank (just tab to the next field) or *jnk* can be explicitly typed if it helps visualize the data fields.
