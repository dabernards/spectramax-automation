# TODO.md

## Active Items
- [ ] CLI 
- [ ] function integration
- [ ] transfer actionable items in package-org into active TODOs
- [ ] review deprecated items and confirm they are out of date or incorporated into active
- [ ] expect data from a Tecan plate reader -- will require adding module for data loading
- [ ] ProcessedData class that ingests SmaxData and provides the name-based/time-based data formats
- [ ] docs on refactored code
- [ ] Refactor SmaxData class into subclasses so attribute sets are more manageable (classes for absb, spec, conc data?)
- [ ] Use or lose pair_files in fileops.py

## Completed Items
- [x] Make linear fit default w/ linregress; add CurveFit class with curve_fit solver; all others extend CurveFit
- [x] Add standard ELISA fit method
- [x] Put error handling for incorrectly formatted `spec` at file loading stage
- [x] Move SmaxData fitting and calcs to use any function from fitting.py. Rename to more generically to `fit_data` and `calc_data`

## Longer-term Items
- [ ] Tool to assist user in generating spec (maybe requires gui)
- [ ] Debug module to collect lesser used functions and clear up code as is possible


## DEPRECATED Features to add/improve
- [x] ~Move away from overly complex constructers to simple constructers and necessary loops as a matter of code aesthetics~ these for loops look horrific
- [ ] Spectramax txt data that has leading/tailing columns w/o data see to cause all sort of issues. Work around is including 'jnk' entries or omitting leading columns to account for extra/missing columns.
- [ ] Module to address how day zero is treated -- use/ignore d0 conc data, make zero=0, generate d0 if does not exist
- [ ] Improve data flow and functions -- functions only for data that needs solid outputs?
- [ ] Update functional organization toward function/modules rather than bulk file
- [ ] Additional module to calculate mass, cumulative mass, and release rate
- [ ] Add capacity for non-linear fit (initial priority of power law fit y = y_o + A x^b)
- [ ] Add method to output only select set of device/sample names (probably requires function to generate list of device/sample IDs and an entry in settings.yml for output file names and corresponding lists of devices)
