__author__ = 'douglasbr'
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from archive_control_ui import Ui_ArchiveControl

class ArchiveControl(QtGui.QWidget):
    def __init__(self, parent=None, name='default name', cbViewArchive=None, cbDeleteArchive=None, quality=1000):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_ArchiveControl()
        self.ui.setupUi(self)

        self.setName(name)
        self.setQuality(quality)
        self.cbViewArchive = cbViewArchive
        self.cbDeleteArchive = cbDeleteArchive

        QtCore.QObject.connect(self.ui.buttonViewArchive,QtCore.SIGNAL("clicked()"), self.slot_buttonViewArchiveClicked)
        QtCore.QObject.connect(self.ui.buttonDeleteArchive,QtCore.SIGNAL("clicked()"), self.slot_buttonDeleteArchiveClicked)

    def setQuality(self, value):
        self.quality = value
        if value >= 0:
            self.ui.lblQuality.setText(str(value))
        else:
            self.ui.lblQuality.setText('  ')

    def setName(self, name):
        self.name = name
        self.ui.lblArchiveName.setText(name)

    def slot_buttonViewArchiveClicked(self):
        self.cbViewArchive(self.name)

    def slot_buttonDeleteArchiveClicked(self):
        self.cbDeleteArchive(self.name)
