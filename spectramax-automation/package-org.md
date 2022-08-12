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

#### default_settings(): dict of settings
- Generate a default settings dictionary
- [ ] does this belong here?

#### generate_settings(filename='settings.yml'): dict of settings written to file
Generate a default settings file populated with relevant fields

#### load_settings(filename='settings.yml', defaults_if_empty=False): dict of settings
Load settings from yaml file (defaulting to settings.yml)


## smax_calc.py
Contains the SmaxData class for bulk of data handling

### class SmaxData:
Basic functions for a plate reader data set

#### SmaxData.flat_data
Combines specification and data into single 1-D array
- [ ] where all is this used? should it be here?

#### SmaxData.\_load_blk
Constructs list from all blank wells
- [ ] Should something like this be in a debug module? by default just report avg and std?

#### SmaxData.\_load_stds
Constructs pair of lists with concentration-standard data (sorted on concentration)

#### SmaxData.\_load_data
Constructions dictionary containing all sample data
- [ ] refactor away from complicated constructor to more readable loops?

#### SmaxData.\_extract_spec(spec)
Process non-sample ID part of spec file to return sub-sample name, time point and dilution
- [ ] handling of both name and time point
- [ ] is this tuple to best approach to managing this? consider a class for this data type

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

#### SmaxData.fit_linear
Perform a generic linear fit from fitting.py
- [ ] seems like these fit better fulling in a fitting module

#### SmaxData.calc_linear
Returns calculated concentrations based on absorbance for linear fit (for plotting)
- [ ] cosndier moving to fitting modules
- [ ] this constructor is confusing as all, better to reproduce as a readable conventional for loop

#### SmaxData.conc_time_sequence
Returns condensed conc_data referenced by time, removing name data and dilution (dilutions already applied)

#### SmaxData.conc_name_list
Returns condensed conc_data referenced by name, removing time data and dilution (dilutions already applied)

#### SmaxData.abs_time_sequence(self):
Returns condensed abs_data referenced by time, removing name data, tuple of calc'd avg & std absb and dilution

#### SmaxData.abs_name_list(self):
Returns condensed abs_data referenced by name, removing time data, tuple of calc'd avg & std absb and dilution

## fitting.py
Provides versitility in fitting options -- extends abilities beyond boring linear fit

### class GenericFit:
Generic class to provide basic elements required from a fitting function
- [ ] add inverse function as required/expected function?

#### GenericFit.fit_func(x, a):    #pylint: disable=C0103,R0201
Default function is just addition, did this since including a linear fit to distinguish
- [ ] Consider replacing w/ LinearFit as the core module that everything extends, allowing it to be the default

#### GenericFit.fit_method(xdata, ydata):
Default fit method for a set of x and y data is scipy.optimize.curve_fit

#### LinearFit(GenericFit)
Extends the generic fit class, using linregress rather than curve_fit

#### LinearFit.fit_func(self, x, intercept, slope):    #pylint: disable=C0103,W0221

#### LinearFit.curve_fit(self, xdata, ydata):
For linear fit, use scipy.stats.linregress

#### PowerFit(GenericFit):
Power function fitting, can reuse generic fit method
- [ ] Each fit would need to incorporate the curve_fit method if LinearFit used as base class
- [ ] Alternatively could have NonLinFit extend LinFit with curve_fit method and all other extend NonLinFit w/ their fit function
    '''
    def fit_func(self, x, intercept, multip, power):    # pylint: disable=W0221
        ''' Most generic power-law function includes intercept '''
        return intercept + multip*x**power



if __name__ =='__main__':
    pass
