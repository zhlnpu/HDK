__author__ = 'Douglas Bruey: Synapse Product Development'

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from progress_control_ui import Ui_ProgressDisplay

class SimProgress(QtGui.QWidget):
    def __init__(self, parent=None, index=0, cbView=None, cbArchive=None, cbCancelSimulation=None, quality=1000):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_ProgressDisplay()
        self.ui.setupUi(self)

        self.setIndex(index)
        self.cbView = cbView
        self.cbArchive = cbArchive
        self.cbCancelSimulation = cbCancelSimulation
        self.setQuality(quality)
        self.running = False

        QtCore.QObject.connect(self.ui.buttonViewResults,QtCore.SIGNAL("clicked()"), self.slot_buttonViewResultsClicked)
        QtCore.QObject.connect(self.ui.buttonArchive,QtCore.SIGNAL("clicked()"), self.slot_buttonArchiveClicked)

    def incProgress(self):
        self.running = True
        progressValue = self.ui.progressSimulate.value() + 1
        if progressValue > 100:
            progressValue = 0
        self.ui.progressSimulate.setTextVisible(False)
        self.ui.progressSimulate.setValue(progressValue)
        self.ui.buttonViewResults.setEnabled(False)

        self.ui.buttonArchive.setEnabled(True)
        self.ui.buttonArchive.setText('Cancel')

    def setQuality(self, value):
        self.quality = value
        if value >= 0:
            self.ui.lblQuality.setText(str(value))
        else:
            self.ui.lblQuality.setText('  ')

    def setIndex(self, value):
        self.index = value
        self.ui.lblPermutation.setText(str(value))

    def completeProgress(self):
        self.ui.progressSimulate.setValue(100)
        self.ui.buttonViewResults.setEnabled(True)

        self.ui.buttonArchive.setEnabled(True)
        self.ui.buttonArchive.setText('Archive')
        self.running = False

    def slot_buttonViewResultsClicked(self):
        self.cbView(self.index)

    def slot_buttonArchiveClicked(self):
        if self.running:
            self.cbCancelSimulation(self.index)
            self.setParent(None)
        else:
            self.cbArchive(self.index)


