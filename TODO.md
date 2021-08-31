# TODO.md

## Features to add/improve

- [ ] Module to address how day zero is treated -- use/ignore d0 conc data, make zero=0, generate d0 if does not exist
- [ ] Improve data flow and functions -- functions only for data that needs solid outputs?
- [ ] Update functional organization toward function/modules rather than bulk file
- [ ] Additional module to calculate mass, cumulative mass, and release rate
- [ ] Add capacity for non-linear fit (initial priority of power law fit y = y_o + A x^b)
- [ ] Add method to output only select set of device/sample names (probably requires function to generate list of device/sample IDs and an entry in settings.yml for output file names and corresponding lists of devices)
- [x] Additional module to generate the html for the data file list (integrate however is fastest for now)
- [x] Reorganize .spec file to allow for environment variables including elution volume, upper/lower curve omission, etc (yaml formatted file). Have assumed values for missing items (1 ml, no omitted standard curve points, etc)
- [x] Allow days to be decimal
~~- [ ] Add method to offset day, maybe a .offset file with a date followed by time - use dates to calculate d1, 3, ..., and use times to calculate specific offsets~~
