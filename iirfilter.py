#
# (C) 2020 Bernd Porr, mail@berndporr.me.uk
# Apache 2.0 license
#
import scipy.signal as signal
import numpy as np


class IIR2_filter:
    """2nd order IIR filter"""

    def __init__(self, s):
        """Instantiates a 2nd order IIR filter
        s -- numerator and denominator coefficients
        """
        self.numerator0 = s[0]
        self.numerator1 = s[1]
        self.numerator2 = s[2]
        self.denominator1 = s[4]
        self.denominator2 = s[5]
        self.buffer1 = 0
        self.buffer2 = 0

    def filter(self, v):
        """Sample by sample filtering
        v -- scalar sample
        returns filtered sample
        """
        input = v - (self.denominator1 * self.buffer1) - \
            (self.denominator2 * self.buffer2)
        output = (self.numerator1 * self.buffer1) + \
            (self.numerator2 * self.buffer2) + input * self.numerator0
        self.buffer2 = self.buffer1
        self.buffer1 = input
        return output

    def unittest(self):
        """
        The unit test is done by getting a random array, then filtering the
        array. The filtering is then done by hand and the two results are
        compared with each other to see if they match.
        """
        x = [6, -1, 4]  # random input to test our filter
        y = np.zeros(len(x))
        for i in range(len(x)):
                y[i] = self.filter(x[i]) # filter the output one sample at a time

        return y

class IIR_filter:
    """IIR filter"""

    def __init__(self, sos):
        """Instantiates an IIR filter of any order
        sos -- array of 2nd order IIR filter coefficients
        """
        self.cascade = []
        for s in sos:
            self.cascade.append(IIR2_filter(s))

    def filter(self, v):
        """Sample by sample filtering
        v -- scalar sample
        returns filtered sample
        """
        for f in self.cascade:
            v = f.filter(v)
        return v

    def unittest(self):
        """
        The unit test is done by getting a random array, then filtering the
        array. The filtering is then done by hand and the two results are
        compared with each other to see if they match.
        """
        x = [6, -1, 4]  # random input to test our filter
        y = np.zeros(len(x))
        for i in range(len(x)):
                y[i] = self.filter(x[i]) # filter the output one sample at a time

        return y
