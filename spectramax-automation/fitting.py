#!/bin/env python3
''' Container for fitting functions '''

import scipy.stats
import scipy.optimize


class GenericFit:
    ''' For fitting, this provides a generic class to work with
        By default this is a linear fit optimized by scipy.optimize.curve_fit
    '''

    def __init__(self):
        self.params=[]
        self.fit_result = []

    def fit_func(self, x, a):    #pylint: disable=C0103,R0201
        ''' Default function is addition '''
        return a+x

    def fit_method(self, xdata, ydata):
        ''' Default fit approach used scipy.optimize.curve_fit
            Result of fitting sets self.params as determined by fit and keeps
            the full result of the optimization method as self.fit_result

            Args:
                -xdata: list of x data points
                -ydata: list of y data points

            Returns:
                - params: set of fitting parameters for defined function
                - fit_result: complete result from fitting function
        '''

        popt, pcov = scipy.optimize.curve_fit(self.fit_func, xdata, ydata)     # pylint: disable=W0632
        self.params = popt
        self.fit_result = popt, pcov

        return popt, [popt, pcov]


class LinearFit(GenericFit):
    ''' Even though linear function is default in genericFit incorporate here
        to use scipy.stats.linregress instead since it includes a bit more
        linear-fit specific details for fit_result
    '''

    def fit_func(self, x, intercept, slope):    #pylint: disable=C0103,W0221
        ''' Default function is linear '''
        return intercept + slope*x

    def curve_fit(self, xdata, ydata):
        ''' For linear fit, use scipy.stats.linregress

            Args:
                -xdata: list of x data points
                -ydata: list of y data points

            Returns:
                - params: set of fitting parameters for defined function
                - fit_result: LinregressResult containing full detail of fit
        '''
        fit_result = scipy.stats.linregress(xdata, ydata)
        self.params = fit_result.intercept, fit_result.slope
        return (fit_result.intercept, fit_result.slope), fit_result

class PowerFit(GenericFit):
    ''' Power function for it
    '''
    def fit_func(self, x, intercept, multip, power):    # pylint: disable=W0221
        ''' Most generic power-law function includes intercept '''
        return intercept + multip*x**power



if __name__ =='__main__':
    pass
