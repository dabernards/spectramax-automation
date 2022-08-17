#!/bin/env python3
''' Container for fitting functions '''

import scipy.stats
import scipy.optimize


class LinearFit:
    ''' Base fitting class is a conventional linear fit. Uses
        scipy.stats.linregress sicne it includes some linear-fit specific
        results in fit_result
    '''

    def __init__(self):
        self.params=[]
        self.fit_result = []

    def fit_func(self, x, intercept, slope):    #pylint: disable=C0103,W0221,R0201
        ''' Default function is linear fit '''
        return intercept + slope*x

    def inv_func(self, y, intercept, slope):    #pylint: disable=C0103,R0201
        ''' Fit function with swapped dependent/independent variables '''
        return (y - intercept) / slope

    def fit_method(self, xdata, ydata):
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


class CurveFit(LinearFit):
    ''' CurveFit provides the alternate fit method using scipy.optimize.curve_fit
        Can be used by all other fit functions
    '''
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


class PowerFit(CurveFit):
    ''' Power function for it
    '''
    def fit_func(self, x, intercept, multip, power):    # pylint: disable=W0221
        ''' Most generic power-law function includes intercept '''
        return intercept + multip*x**power

    def inv_func(self, y, intercept, multip, power):    # pylint: disable=W0221
        return ( (y - intercept) / multip )**(1/power)


class LogisticFit(CurveFit):
    ''' Conventional 4-parameter logistic used for fitting ELISA data
    '''
    def fit_func(self, x, a, b, c, d):    # pylint: disable=W0221,R0913
        ''' 4-parameter logistic function '''
        return d + (a - d) / (1 + (x/c)**b )

    def inv_func(self, y, a, b, c, d):    # pylint: disable=W0221,R0913
        return c * ( (a - y) / (y - d) )**(1/b)


if __name__ =='__main__':
    pass
