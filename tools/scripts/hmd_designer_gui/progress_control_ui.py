# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'progress_control_ui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ProgressDisplay(object):
    def setupUi(self, ProgressDisplay):
        ProgressDisplay.setObjectName(_fromUtf8("ProgressDisplay"))
        ProgressDisplay.resize(731, 74)
        self.gridLayout = QtGui.QGridLayout(ProgressDisplay)
        self.gridLayout.setContentsMargins(13, 0, 13, 0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblPermutation = QtGui.QLabel(ProgressDisplay)
        self.lblPermutation.setObjectName(_fromUtf8("lblPermutation"))
        self.gridLayout.addWidget(self.lblPermutation, 0, 0, 1, 1)
        self.progressSimulate = QtGui.QProgressBar(ProgressDisplay)
        self.progressSimulate.setProperty("value", 0)
        self.progressSimulate.setTextVisible(False)
        self.progressSimulate.setObjectName(_fromUtf8("progressSimulate"))
        self.gridLayout.addWidget(self.progressSimulate, 0, 1, 1, 1)
        self.lblQuality = QtGui.QLabel(ProgressDisplay)
        self.lblQuality.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblQuality.setObjectName(_fromUtf8("lblQuality"))
        self.gridLayout.addWidget(self.lblQuality, 0, 2, 1, 1)
        self.buttonViewResults = QtGui.QPushButton(ProgressDisplay)
        self.buttonViewResults.setEnabled(True)
        self.buttonViewResults.setObjectName(_fromUtf8("buttonViewResults"))
        self.gridLayout.addWidget(self.buttonViewResults, 0, 3, 1, 1)
        self.buttonArchive = QtGui.QPushButton(ProgressDisplay)
        self.buttonArchive.setEnabled(True)
        self.buttonArchive.setObjectName(_fromUtf8("buttonArchive"))
        self.gridLayout.addWidget(self.buttonArchive, 0, 4, 1, 1)
        self.gridLayout.setColumnMinimumWidth(0, 25)
        self.gridLayout.setColumnMinimumWidth(2, 50)

        self.retranslateUi(ProgressDisplay)
        QtCore.QMetaObject.connectSlotsByName(ProgressDisplay)

    def retranslateUi(self, ProgressDisplay):
        ProgressDisplay.setWindowTitle(_translate("ProgressDisplay", "Form", None))
        self.lblPermutation.setText(_translate("ProgressDisplay", "0", None))
        self.lblQuality.setText(_translate("ProgressDisplay", "1000", None))
        self.buttonViewResults.setText(_translate("ProgressDisplay", "View", None))
        self.buttonArchive.setText(_translate("ProgressDisplay", "Archive", None))

