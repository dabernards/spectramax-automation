# TODO.md

## Active Items
- [ ] CLI 
- [ ] function integration
- [ ] docs on refactored code
- [ ] transfer actionable items in package-org into active TODOs
- [ ] review deprecated items and confirm they are out of date or incorporated into active







## DEPRECATED Features to add/improve
- [ ] Spectramax txt data that has leading/tailing columns w/o data see to cause all sort of issues. Work around is including 'jnk' entries or omitting leading columns to account for extra/missing columns.
- [ ] Module to address how day zero is treated -- use/ignore d0 conc data, make zero=0, generate d0 if does not exist
- [ ] Improve data flow and functions -- functions only for data that needs solid outputs?
- [ ] Update functional organization toward function/modules rather than bulk file
- [ ] Additional module to calculate mass, cumulative mass, and release rate
- [ ] Add capacity for non-linear fit (initial priority of power law fit y = y_o + A x^b)
- [ ] Add method to output only select set of device/sample names (probably requires function to generate list of device/sample IDs and an entry in settings.yml for output file names and corresponding lists of devices)
