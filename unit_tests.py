#!/bin/env python3
''' units tests currently validate loading generic Spectramax plate reader data
'''

import unittest
import os

from fileops import data_load, spec_load


class SmaxFileTests(unittest.TestCase):
    ''' unit tests for file parsing
        Will want to incorporate the following plate layouts
        full (8x12)
        missing left, right, top, and/or bottom rows
        multiple plates (as in multi-wavelength)


    '''


    def setUp(self):
        ''' Load basic plate layout for use '''

        self.txtfilename = "generic_plate.txt"
        # Reference txt (plate) data
        with open(self.txtfilename, 'w', encoding='utf-8') as txt_file:
            txt_file.write('##BLOCKS= 1          \n'
                    'Plate:\tPlate#1\t1.3\tPlateFormat\tEndpoint\tAbsorbance\tRaw\tFALSE\t1\t\t\t\t\t\t1\t240\t3\t10\t96\t1\t8\tNone\t\n' # pylint: disable=C0301
                    '\tTemperature(C)\t1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11\t12\t\t\n'
                    '\t23.40\t\t\t0.8041\t0.8463\t0.7422\t0.6931\t0.1506\t0.1498\t0.1373\t0.1389\t0.8982\t0.8929\t\t\n'
                    '\t\t\t\t0.8208\t0.7707\t0.6203\t0.5545\t0.1446\t0.1443\t0.137\t0.1365\t0.4985\t0.4928\t\t\n'
                    '\t\t\t\t0.711\t0.5566\t0.5614\t0.5908\t0.154\t0.1543\t0.1467\t0.1471\t0.2949\t0.2933\t\t\n'
                    '\t\t\t\t0.63\t0.6565\t0.513\t0.4744\t0.1658\t0.1667\t0.1507\t0.1502\t0.1898\t0.1916\t\t\n'
                    '\t\t\t\t0.6383\t0.6244\t0.111\t0.0997\t0.1298\t0.1275\t0.1451\t0.1451\t0.1584\t0.1414\t\t\n'
                    '\t\t\t\t0.5997\t0.5052\t0.0936\t0.0941\t0.1364\t0.1361\t0.1491\t0.1323\t0.1292\t0.1162\t\t\n'
                    '\t\t\t\t0.5202\t0.4435\t0.0904\t0.0915\t0.1292\t0.1236\t0.1372\t0.1369\t0.1052\t0.1042\t\t\n'
                    '\t\t\t\t0.4566\t0.3973\t0.0901\t0.0896\t0.1272\t0.1264\t0.1369\t0.134\t0.0984\t0.0976\t\t\n'
                    '\t\t\n'
                    '~End\n'
                    'Original Filename: generic_plate.pda   Date Last Saved: 6/17/2022\n'
                    '')
        # Reference spec (specification) data
        self.specfilename = "generic_plate.spec"
        with open(self.specfilename, 'w', encoding='utf-8') as spec_file:
            spec_file.write(''
                'TAc1-d64.13\tTAc1-d64.13\tTAc1-d76.92\tTAc1-d76.92\tTAc11-d18.98\tTAc11-d18.98\tTAc11-d27.9\tTAc11-d27.9\tstd-50\tstd-50\n' # pylint: disable=C0301
                'TAc2-d64.13\tTAc2-d64.13\tTAc2-d76.92\tTAc2-d76.92\tTAc12-d18.98\tTAc12-d18.98\tTAc12-d27.9\tTAc12-d27.9\tstd-25\tstd-25\n'
                'TAc3-d64.13\tTAc3-d64.13\tTAc3-d76.92\tTAc3-d76.92\tTAc13-d18.98\tTAc13-d18.98\tTAc13-d27.9\tTAc13-d27.9\tstd-12.5\tstd-12.5\n'
                'TAc4-d64.13\tTAc4-d64.13\tTAc4-d76.92\tTAc4-d76.92\tTAc14-d18.98\tTAc14-d18.98\tTAc14-d27.9\tTAc14-d27.9\tstd-6.25\tstd-6.25\n'
                'TAc1-d70.04\tTAc1-d70.04\tblk\tblk\tTAc11-d21.8\tTAc11-d21.8\tTAc11-d33.86\tTAc11-d33.86\tstd-3.125\tstd-3.125\n'
                'TAc2-d70.04\tTAc2-d70.04\tblk\tblk\tTAc12-d21.8\tTAc12-d21.8\tTAc12-d33.86\tTAc12-d33.86\tstd-1.5625\tstd-1.5625\n'
                'TAc3-d70.04\tTAc3-d70.04\tblk\tblk\tTAc13-d21.8\tTAc13-d21.8\tTAc13-d33.86\tTAc13-d33.86\tstd-0.78125\tstd-0.78125\n'
                'TAc4-d70.04\tTAc4-d70.04\tblk\tblk\tTAc14-d21.8\tTAc14-d21.8\tTAc14-d33.86\tTAc14-d33.86\tstd-0.390625\tstd-0.390625\n'
                '')

    def tearDown(self):
        ''' remove test files '''
        try:
            os.remove(self.txtfilename)
            os.remove(self.specfilename)
        except OSError:
            pass


    def test_data_load_type(self):
        ''' Confirm plate_data is a list '''
        plate_data = data_load(self.txtfilename)
        self.assertTrue(isinstance(plate_data, list))

    def test_data_load_rows(self):
        ''' Confirm plate_data has 0<row<9 '''
        plate_data = data_load(self.txtfilename)
        self.assertTrue(len(plate_data) in list(range(1,9)))

    def test_data_load_cols(self):
        ''' Confirm plate_data has 0<columns<13 and all rows have same column # '''
        plate_data = data_load(self.txtfilename)
        cols = { len(row) for row in plate_data }
        self.assertTrue(len(cols)==1 and list(cols)[0] in range(1,13))

    def test_data_load_allfloat(self):
        ''' confirm all plate data is type float '''
        pass


    def test_spec_load_type(self):
        ''' Confirm plate_format is a list '''
        plate_format = spec_load(self.specfilename)
        self.assertTrue(isinstance(plate_format, list))

    def test_spec_load_rows(self):
        ''' Confirm plate_format has 0<row<9 '''
        plate_format = spec_load(self.specfilename)
        self.assertTrue(len(plate_format) in list(range(1,9)))

    def test_spec_load_cols(self):
        ''' Confirm plate_format has 0<columns<13 and all rows have same column # '''
        plate_format = spec_load(self.specfilename)
        cols = { len(row) for row in plate_format }
        self.assertTrue(len(cols)==1 and list(cols)[0] in range(1,13))




if __name__ == '__main__':
    unittest.main()
