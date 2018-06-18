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
            'fftdataOut': dict(io='out'),

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


        for i in range(len(self._bufferX)):
            xValue = self._bufferX[i]
            yValue = self._bufferY[i]
            zValue = self._bufferZ[i]
            avgValue =((xValue + yValue + zValue) /3)
            self._avg = np.append(self._avg, avgValue)
            self._avg = self._avg[-size:]

        avg = np.fft.fft(self._avg / len(self._avg))
        avgfft = abs(avg)


        return {'fftdataOut':  avgfft}

fclib.registerNodeType(FftNode, [('Data',)])

class SvmNode(Node):

    nodeName = "Svm"


    def __init__(self, name):
        terminals = {
            'In': dict(io='in'),
            'Out': dict(io='out'),
        }

        self._buffer = np.array([])

        self.JUMP = 0
        self.WALK = 1
        self.SIT = 2

        self.modeText = "Inactive"
        self.activityText = "Jumping"

        self.jump = np.array([])
        self.sit = np.array([])
        self.walk = np.array([])
        self.inputData = np.array([])

        self.ui = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()

        activityLabel = QtGui.QLabel("Choose your activity")
        self.layout.addWidget(activityLabel)

        self.activity = QtGui.QComboBox()
        self.activity.addItem("Jumping")
        self.activity.addItem("Walking")
        self.activity.addItem("Sitting")
        self.activity.activated.connect(self.getTextFromActivity)
        self.layout.addWidget(self.activity)

        modeLabel = QtGui.QLabel("Choose the mode")
        self.layout.addWidget(modeLabel)

        self.mode = QtGui.QComboBox()
        self.mode.addItem("Inactive")
        self.mode.addItem("Training")
        self.mode.addItem("Prediction")
        self.mode.activated.connect(self.getTextFromMode)
        self.layout.addWidget(self.mode)

        self.ui.setLayout(self.layout)

        self.c = svm.SVC()

        Node.__init__(self, name, terminals=terminals)

    def ctrlWidget(self):
        return self.ui

    def getTextFromMode(self):
        self.modeText = self.mode.currentText()

    def getTextFromActivity(self):
        self.activityText = self.mode.currentText()


    def process(self, **kwds):
        self.inputData = np.append(self.inputData, kwds['In'])
        categories = [self.JUMP] * 3 + [self.SIT] * 3 + [self.WALK] * 3
        print("Model: ", self.modeText)
        predicted = 0
        if self.modeText == "Training":
            training_data = self.jump[1:] + self.walk[1:] + self.sit[1:]
            if self.activityText == "Jumping":
                self.jump = np.append(self.jump, self.inputData)
                self.c.fit(training_data,categories)
                print("Training Jumping")
            elif self.activityText == "Walking":
                self.walk = np.append(self.walk, self.inputData)
                self.c.fit(training_data,categories)
                print("Training Walking")
            elif self.activityText == "Sitting":
                self.sit = np.append(self.sit, self.inputData)
                self.c.fit(training_data,categories)
                print("Training Sitting")
        elif self.modeText == "Prediction":
            predicted = self.c.predict(self.inputData)
            print(predicted)

        return {'Out': predicted}

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



    wiimoteNode = fc.createNode('Wiimote', pos=(0, 0),)
    buffer1Node = fc.createNode('Buffer', pos=(150, -150))
    buffer2Node = fc.createNode('Buffer', pos=(150, 0))
    buffer3Node = fc.createNode('Buffer', pos=(150, 150))
    fftNode = fc.createNode('Fft', pos=(550, 0))
    svmNode = fc.createNode('Svm', pos=(550, 120))


    fc.connectTerminals(wiimoteNode['accelX'], buffer1Node['dataIn'])
    fc.connectTerminals(wiimoteNode['accelY'], buffer2Node['dataIn'])
    fc.connectTerminals(wiimoteNode['accelZ'], buffer3Node['dataIn'])
    fc.connectTerminals(buffer1Node['dataOut'], pw1Node['In'])
    fc.connectTerminals(buffer2Node['dataOut'], pw2Node['In'])
    fc.connectTerminals(buffer3Node['dataOut'], pw3Node['In'])
    fc.connectTerminals(buffer1Node['dataOut'], fftNode['XdataIn'])
    fc.connectTerminals(buffer2Node['dataOut'], fftNode['YdataIn'])
    fc.connectTerminals(buffer3Node['dataOut'], fftNode['ZdataIn'])
    fc.connectTerminals(fftNode['fftdataOut'], pw4Node['In'])
    fc.connectTerminals(fftNode['fftdataOut'], svmNode['In'])


    win.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
