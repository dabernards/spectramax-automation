# smax-data Organizational structure



## fileops.py
Collection of all file-system facing activities
- [ ] missing write tab/comma delimited output of analysis

#### pair_files(filename): boolean
Check if filename has a txt and spec file pair for analysis
- [ ] check if this is in use anywhere

#### load_data(filename): 2D array fo plate reader data
Load data from txt export of Spectramax software

#### load_spec(filename): 2D array of plate specifications
Load data from user-generated spec file
- [ ] any tools to help facilitate this?


## settings.py

#### default_settings(): dict of settings
- Generate a default settings dictionary

#### generate_settings(filename='settings.yml'): dict of settings written to file
- Generate a default settings file populated with relevant fields

#### load_settings(filename='settings.yml', defaults_if_empty=False): dict of settings
- Load settings from yaml file (defaulting to settings.yml)


## smax_calc.py
Contains the SmaxData class for bulk of data handling

### class SmaxData:
Basic functions for a plate reader data set

#### SmaxData.flat_data
Combines specification and data into single 1-D array
- [ ] where all is this used? should it be here? -- part of refactoring current SMaxData into subclasses

#### SmaxData.\_load_blk
Constructs list from all blank wells
- [ ] Should something like this be in a debug module? by default just report avg and std?

#### SmaxData.\_load_stds
Constructs pair of lists with concentration-standard data (sorted on concentration)

#### SmaxData.\_load_data
Constructions dictionary containing all sample data
~- [ ] refactor away from complicated constructor to more readable loops?~

#### SmaxData.\_extract_spec(spec)
Process non-sample ID part of spec file to return sub-sample name, time point and dilution
- [ ] handling of both name and time point
- [ ] is this tuple to best approach to managing this? consider a class for this data type --> yes refactoring

#### SmaxData.\_truncate_stds
Truncates standard curve on low/high end for use in fitting
- [ ] should be re-evaluated for how this integrates
- [ ] consider raw-standards and fit-standards to incorporate truncating fit range or outlier points

#### SmaxData.set_limits(omit_lower=0, omit_upper=0)
Adjust limits for lower and upper points to omit - property used by internal \_truncate_stds function

#### SmaxData.func_linear(params, x)
Basic linear function for calculations
- [ ] Does this need to be here? Can all fitting modules be better accomodated in fitting.py?

#### SmaxData.avg_blk
Returns average blank-well absorbance
- [ ] related to \_load_blk issue
- [ ] consider this avg blk as default data for class and debug toolset to handle more detail 

#### SmaxData.fit_data
Perform a fit using function from fitting.py
- [ ] seems like these fit better fulling in a fitting module

#### SmaxData.calc_data
Returns calculated concentrations based on fit function from fitting.py
~- [ ] this constructor is confusing as all, better to reproduce as a readable conventional for loop~ even worse w/ for loops

### format_data.py (?)
- [ ] Should have these functions in a data formatting module

#### SmaxData.conc_time_sequence
Returns condensed conc_data referenced by time, removing name data and dilution (dilutions already applied)

#### SmaxData.conc_name_list
Returns condensed conc_data referenced by name, removing time data and dilution (dilutions already applied)

#### SmaxData.abs_time_sequence(self):
Returns condensed abs_data referenced by time, removing name data, tuple of calc'd avg & std absb and dilution

#### SmaxData.abs_name_list(self):
Returns condensed abs_data referenced by name, removing time data, tuple of calc'd avg & std absb and dilution


## fitting.py
Provides versitility in fitting options -- extends abilities beyond basic linear fit

#### LinearFit
Base fitting class using linregress, contains
- fit_func: y = f(x)
- inv_func: x = g(y)
- fit_method: how to determine best fit (scipy.stats.linregress)

#### CurveFit(LinearFit)
Extends LinearFit, employing the more generic scipy.optimize.curve_fit

#### PowerFit(CurveFit)
Power function fitting, extends CurveFit class

#### LogisticFit(CurveFit)
Four-parameter logistic function fitting used commonly for ELISA data, extends CurveFit class
