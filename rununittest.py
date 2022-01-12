import iirfilter
import scipy.signal as signal

samplingRate = 100

# 6th order DC line filter to run the unit test
fc = 2  # cutoff frequency
coefficients = signal.butter(
    6, fc / samplingRate * 2, btype='high', output='sos')
print('DC coefficients:', coefficients)

# perform unit test on 2 outputs
y = iirfilter.IIR_filter(coefficients).unittest() # 6th order IIR filter
y2 = iirfilter.IIR2_filter(coefficients[0]).unittest() # 2nd order IIR filter
# the second filter takes a 2nd order IIR filter as an argument, so we
# put the first filter in the chain of IIR filters as argument

print('2nd order filter coefficients:', y)
print('6th order filter coefficients:', y2)
