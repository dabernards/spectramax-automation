#!/usr/bin/env python3
''' welcome '''

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

def linear(x, a, b):
    ''' linear fit function'''
    return a + b * (x)
def power(x, a, b, c):
    ''' placeholder fit function, maybe a user has to pass this '''
    return a + b * x**c
def elisa(x, a, b, c, d):
    ''' placeholder fit function, maybe a user has to pass this '''
    return d + (a - d) / ( 1 + (x/c)**b )




def plot_standards(abs_std, conc_std, fit_func=linear, omit_lower=0, omit_upper=0):
    '''standard curve w/ user selected function, defaulting to internally defined linear fit'''

    fit_results, _ = curve_fit(fit_func, \
            abs_std[omit_lower:len(abs_std)-omit_upper], \
            conc_std[omit_lower:len(abs_std)-omit_upper])

    _ = plt.plot(abs_std, conc_std, 'o', label='Data', markersize=10)
    _ = plt.plot(abs_std, fit_func(np.array(abs_std), *fit_results), 'r', label='Fit')
    _ = plt.legend()
    _ = plt.loglog()
    plt.show()
    return fit_results
