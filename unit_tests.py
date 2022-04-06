#!/bin/env python3
''' units tests currently validate loading generic Spectramax plate reader data
'''


import smax_data

files = ["bottom6x9.txt", "left8x9.txt", "leftright8x8.txt", "left-right-bottom-top5x6.txt",\
         "right8x9.txt", "top6x9.txt"]

for file in files:
    try:
        data = smax_data.load_plate(f"unit-tests/{file}")
        print(len(data), len(data[0]))
        # need to check size of array and match; need to make sure data checks out
    except:
        pass


