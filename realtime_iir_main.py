import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from iirfilter import IIR_filter
import scipy.signal as sig
from pyfirmata2 import Arduino
import time

PORT = Arduino.AUTODETECT

# create a global QT application object
app = QtGui.QApplication(sys.argv)

# signals to all threads in endless loops that we'd like to run these
running = True


class QtPanningPlot:

    def __init__(self, title):
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle(title)
        self.plt = self.win.addPlot()
        self.plt.setYRange(-1, 1)
        self.plt.setXRange(0, 500)
        self.curve = self.plt.plot()
        self.data = []
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
        self.layout = QtGui.QGridLayout()
        self.win.setLayout(self.layout)
        self.win.show()

    def update(self):
        self.data = self.data[-500:]
        if self.data:
            self.curve.setData(np.hstack(self.data))

    def addData(self, d):
        self.data.append(d)


# Let's create four instances of plot windows
qtPanningPlot1 = QtPanningPlot("Echo Signal")
qtPanningPlot2 = QtPanningPlot("Unfiltered Trigger Signal")
qtPanningPlot3 = QtPanningPlot("Filtered Trigger Signal")
qtPanningPlot4 = QtPanningPlot("Normalized Instantaneous Sampling Rate")

# sampling rate
samplingRate = 100

# DC line filter to eliminate the offset
fc = 2  # cutoff frequency
sosDC = sig.butter(6, fc / samplingRate * 2, btype='high', output='sos')

# elimiating the high frequency noise
fc = 8  # cutoff frequency
sosLP = sig.cheby2(6, 40, fc / samplingRate * 2, btype='low', output='sos')

# instantiate the 2nd order chain class
filterDC = IIR_filter(sosDC)
filterLP = IIR_filter(sosLP)


# called for every new sample which has arrived from the Arduino
class callbacks:
    def __init__(self):
        self.samplingRate = 100
        self.timestamp = 0
        self.start_time = 0
        self.current_time = 0
        self.current_sr = 0
        self.delta_t = 0
        self.t2 = 0
        self.t1 = 0
        self.previous = np.zeros(5)

    def initial(self, board):
        # Set the sampling rate in the Arduino
        board.samplingOn(1000 / self.samplingRate)

        # Register the callback which adds the data to the animatedplot
        board.analog[0].register_callback(self.callBack1)
        board.analog[1].register_callback(self.callBack2)

        # Enable the callback
        board.analog[0].enable_reporting()
        board.analog[1].enable_reporting()
        self.start_time = time.time()

    def callBack1(self, data):
        # send the sample to the plot window
        # filtering the data

        self.current_time = time.time() - self.start_time
        self.t2 = time.time()               # t2 is the start time of the execution time
        self.delta_t = self.t2 - self.t1    # calculation of the execution time
        if self.timestamp != 0:
            self.current_sr = self.current_time / (call_backs.timestamp / call_backs.samplingRate)
        print('The instantaneous sampling rate', self.current_sr)
        self.t1 = self.t2                   # t1 is the end time of the execution time

        # Detection
        for i in range(len(self.previous)):
            self.previous[len(self.previous) - i - 1] = self.previous[len(self.previous) - i - 2]
            self.previous[0] = data

        if np.sum(self.previous) < 0.001:
            board.digital[8].write(True)
        else:
            board.digital[8].write(False)

        qtPanningPlot4.addData(self.current_sr / self.samplingRate)
        qtPanningPlot1.addData(data)

        # keep a count of the number of samples arriving
        self.timestamp += 1 / self.samplingRate

    def callBack2(self, data):
        # send the sample to the plot window
        # filtering the data

        output = filterDC.filter(data)
        output = filterLP.filter(output)

        # Plot unfiltered input data and filtered output
        qtPanningPlot2.addData(data)
        qtPanningPlot3.addData(output)


# Get the Arduino board.
board = Arduino(PORT)

# Declare callbacks class as call_backs
call_backs = callbacks()
# Start the Initial function from the class initial which run the true callback inside the class
call_backs.initial(board)

# showing all the windows
app.exec_()
finish_time = time.time()

# needs to be called to close the serial port
board.exit()

Execution_time = finish_time - call_backs.start_time
Actual_sampling_rate = Execution_time / (call_backs.timestamp / call_backs.samplingRate)

print('Execution Time:', Execution_time)
print('Actual Sampling Rate:', Actual_sampling_rate)
print("finished")

