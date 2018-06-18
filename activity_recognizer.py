#!/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

# this code is adapted to wiimote_node.py from Raphael Wimmer


from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import math
import wiimote
import wiimote_node
import time
import sys
from wiimote_node import BufferNode
from pylab import *
from scipy import fft
from sklearn import svm



class FftNode(CtrlNode):

    nodeName = "Fft"
    uiTemplate = [
        ('size',  'spin', {'value': 32.0, 'step': 1.0, 'bounds': [0.0, 128.0]}),
    ]

    def __init__(self, name):
        terminals = {
            'XdataIn': dict(io='in'),
            'YdataIn': dict(io='in'),
            'ZdataIn': dict(io='in'),
            'XdataOut': dict(io='out'),
            'YdataOut': dict(io='out'),
            'ZdataOut':dict(io='out'),

        }
        self._bufferX = np.array([])
        self._bufferY = np.array([])
        self._bufferZ = np.array([])
        self._avg = np.array([])
        self._xcut = np.array([])
        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        size = int(self.ctrls['size'].value())
        self._bufferX = np.append(self._bufferX, kwds['XdataIn'])
        self._bufferX = self._bufferX[-size:]
        self._bufferY = np.append(self._bufferY, kwds['YdataIn'])
        self._bufferY = self._bufferY[-size:]
        self._bufferZ = np.append(self._bufferZ, kwds['ZdataIn'])
        self._bufferZ = self._bufferZ[-size:]

    # das was hier auskommentiert ist würde auch funktionieren und entspricht größtenteils dem Code aus dem Kurs am Dienstag
    # mit dem Code sind die Amplituden auch nicht so groß, wie es jetzt der Fall ist, aber ich weiß nicht, ab der aktuelle
    # Code ausreicht, oder ob wir das so machen müssen, wie bei dem auskommentierten Teil
     #   x = linspace(0, 10, len(self._bufferX)) # 101 samples from 0 to 10

     #   Fs = 10.0  # sampling rate of x
     #   y = self._bufferX
      #  n = len(y) # length of the signal
     #   k = arange(n)
      #  T = n / Fs
     #   frq = k / T # two sides frequency range
     #   frq = frq[0:int(n/2)] # one side frequency range


      #  Y = fft(y) / n # fft computing and normalization
     #   Y = Y[0:int(n/2)] # use only first half as the function is mirrored
     #   print(Y)



        x = fft(self._bufferX)
        xfft = abs(x)
        y = fft(self._bufferY)
        yfft = abs(y)
        z = fft(self._bufferZ)
        zfft = abs(z)

        return {'XdataOut':  xfft, 'YdataOut': yfft, 'ZdataOut': zfft}

fclib.registerNodeType(FftNode, [('Data',)])

class SvmNode(Node):

    nodeName = "Svm"

    def __init__(self, name):
        terminals = {
            'XdataIn': dict(io='in'),
            'YdataIn': dict(io='in'),
            'ZdataIn': dict(io='in'),
            'XdataOut': dict(io='out'),
            'YdataOut': dict(io='out'),
            'ZdataOut':dict(io='out'),

        }

        self._bufferX = np.array([])
        self._bufferY = np.array([])
        self._bufferZ = np.array([])
        self._avg = np.array([])
        self._xcut = np.array([])

        self.ui = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()

        activityLabel = QtGui.QLabel("Choose your activity")
        self.layout.addWidget(activityLabel)

        self.activity = QtGui.QComboBox()
        self.activity.addItem("Jumping")
        self.activity.addItem("Walking")
        self.activity.addItem("Sitting")
        self.mode.activated.connect(self.getTextFromActivity)
        self.layout.addWidget(self.activity)

        modeLabel = QtGui.QLabel("Choose the mode")
        self.layout.addWidget(modeLabel)

        self.mode = QtGui.QComboBox()
        self.mode.addItem("Training")
        self.mode.addItem("Prediction")
        self.mode.addItem("Inactive")
        self.mode.activated.connect(self.getTextFromMode)
        self.layout.addWidget(self.mode)

        self.ui.setLayout(self.layout)


        Node.__init__(self, name, terminals=terminals)

    def ctrlWidget(self):
        return self.ui

    def getTextFromMode(self):
        self.modeText = self.mode.currentText()

    def getTextFromActivity(self):
        self.activityText = self.mode.currentText()


    def process(self, **kwds):
        size = int(self.ctrls['size'].value())
        self._bufferX = np.append(self._bufferX, kwds['XdataIn'])
        self._bufferX = self._bufferX[-size:]
        self._bufferY = np.append(self._bufferY, kwds['YdataIn'])
        self._bufferY = self._bufferY[-size:]
        self._bufferZ = np.append(self._bufferZ, kwds['ZdataIn'])
        self._bufferZ = self._bufferZ[-size:]


        x = fft(self._bufferX)
        xfft = abs(x)
        y = fft(self._bufferY)
        yfft = abs(y)
        z = fft(self._bufferZ)
        zfft = abs(z)

        return {'XdataOut':  xfft, 'YdataOut': yfft, 'ZdataOut': zfft}

fclib.registerNodeType(SvmNode, [('Sensor',)])


if __name__ == '__main__':
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('WiimoteNode demo')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    # Create an empty flowchart with a single input and output
    fc = Flowchart(terminals={
    })
    w = fc.widget()

    layout.addWidget(fc.widget(), 0, 0, 2, 1)
    pw1 = pg.PlotWidget()
    layout.addWidget(pw1, 0, 1)
    pw1.setYRange(0, 1024)

    pw1Node = fc.createNode('PlotWidget', pos=(350, -150))
    pw1Node.setPlot(pw1)

    pw2 = pg.PlotWidget()
    layout.addWidget(pw2, 0, 2)
    pw2.setYRange(0, 1024)

    pw2Node = fc.createNode('PlotWidget', pos=(350, 0))
    pw2Node.setPlot(pw2)

    pw3 = pg.PlotWidget()
    layout.addWidget(pw3, 1, 1)
    pw3.setYRange(0, 1024)

    pw3Node = fc.createNode('PlotWidget', pos=(350, 150))
    pw3Node.setPlot(pw3)

    pw4 = pg.PlotWidget()
    layout.addWidget(pw4, 1, 2)
    pw4.setYRange(0, 1024)

    pw4Node = fc.createNode('PlotWidget', pos=(750, -150))
    pw4Node.setPlot(pw4)

    pw5 = pg.PlotWidget()
    layout.addWidget(pw5, 2, 1)
    pw5.setYRange(0, 1024)

    pw5Node = fc.createNode('PlotWidget', pos=(750, 0))
    pw5Node.setPlot(pw5)

    pw6 = pg.PlotWidget()
    layout.addWidget(pw6, 2, 2)
    pw6.setYRange(0, 1024)

    pw6Node = fc.createNode('PlotWidget', pos=(750, 150))
    pw6Node.setPlot(pw6)


    wiimoteNode = fc.createNode('Wiimote', pos=(0, 0),)
    buffer1Node = fc.createNode('Buffer', pos=(150, -150))
    buffer2Node = fc.createNode('Buffer', pos=(150, 0))
    buffer3Node = fc.createNode('Buffer', pos=(150, 150))
    fftNode = fc.createNode('Fft', pos=(550, 0))
    svmNode = fc.createNode('Svm', pos=(550, 120))
    #normalVectorNode = fc.createNode('NormalVector', pos=(150, 300))
    #plotCurve = fc.createNode('PlotCurve', pos=(200, 100))
    #logNode = fc.createNode('LogNode', pos=(250, 100))

    fc.connectTerminals(wiimoteNode['accelX'], buffer1Node['dataIn'])
    fc.connectTerminals(wiimoteNode['accelY'], buffer2Node['dataIn'])
    fc.connectTerminals(wiimoteNode['accelZ'], buffer3Node['dataIn'])
    fc.connectTerminals(buffer1Node['dataOut'], pw1Node['In'])
    fc.connectTerminals(buffer2Node['dataOut'], pw2Node['In'])
    fc.connectTerminals(buffer3Node['dataOut'], pw3Node['In'])
    fc.connectTerminals(buffer1Node['dataOut'], fftNode['XdataIn'])
    fc.connectTerminals(buffer2Node['dataOut'], fftNode['YdataIn'])
    fc.connectTerminals(buffer3Node['dataOut'], fftNode['ZdataIn'])
    fc.connectTerminals(fftNode['XdataOut'], pw4Node['In'])
    fc.connectTerminals(fftNode['YdataOut'], pw5Node['In'])
    fc.connectTerminals(fftNode['ZdataOut'], pw6Node['In'])

    #fc.connectTerminals(logNode['XOut'], pw1Node['In'])
    ##fc.connectTerminals(logNode['YOut'], pw2Node['In'])
    #fc.connectTerminals(logNode['ZOut'], pw3Node['In'])
    #fc.connectTerminals(buffer1Node['dataOut'], normalVectorNode['XdataIn'])
   # fc.connectTerminals(buffer3Node['dataOut'], normalVectorNode['ZdataIn'])
   # fc.connectTerminals(normalVectorNode['XdataOut'], plotCurve['x'])
   # fc.connectTerminals(normalVectorNode['YdataOut'], plotCurve['y'])
   # fc.connectTerminals(plotCurve['plot'], pwNormalveNode['In'])

    win.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
