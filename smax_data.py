''' Overarching description '''
import re
import numpy as np

class SpectraMaxData:
    ''' SpectraMax plate reader data processing architecture '''
    def __init__(self, filename):
        self.filename = filename
        self.raw_blk = []
        self.abs_blk = 0
        self.read_data()
        self.obtain_blank()

    def read_data(self):
        ''' Open the .txt and .spec files to load the data and plate formatting '''
        with open(self.filename + '.txt', encoding='utf-8', errors='ignore', mode='r') as handle:
            self.plate_data = [line.strip().split('\t') for line in handle \
                if re.match('\t[1-9|\t]', line[0:2]) and line.strip() != '']
        # Temperature does not have use in current implimentation and is dropped here
        _ = self.plate_data[0].pop(0)

        with open(self.filename + '.spec', encoding='utf-8', errors="ignore", mode="r") as handle:
            self.plate_format = [line.strip().split('\t') for line in handle if line.strip() != '']


    def obtain_blank(self):
        ''' Generates array of blank well absorbance values '''
        _int_array = np.array(self.plate_format)

        self.raw_blk = [float(self.plate_data[_row][_col]) \
            for (_row, _col), _item_format in np.ndenumerate(_int_array) \
            if _item_format == "blk"]
        try:
            self.abs_blk = np.mean(self.raw_blk)
        except RuntimeWarning:
            self.abs_blk = 0
