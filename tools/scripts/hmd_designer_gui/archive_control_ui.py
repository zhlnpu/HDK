# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'archive_control_ui.ui'
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

class Ui_ArchiveControl(object):
    def setupUi(self, ArchiveControl):
        ArchiveControl.setObjectName(_fromUtf8("ArchiveControl"))
        ArchiveControl.resize(619, 79)
        self.gridLayout = QtGui.QGridLayout(ArchiveControl)
        self.gridLayout.setContentsMargins(13, 0, 13, 0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblArchiveName = QtGui.QLabel(ArchiveControl)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblArchiveName.sizePolicy().hasHeightForWidth())
        self.lblArchiveName.setSizePolicy(sizePolicy)
        self.lblArchiveName.setObjectName(_fromUtf8("lblArchiveName"))
        self.gridLayout.addWidget(self.lblArchiveName, 0, 0, 1, 1)
        self.lblQuality = QtGui.QLabel(ArchiveControl)
        self.lblQuality.setMaximumSize(QtCore.QSize(75, 16777215))
        self.lblQuality.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblQuality.setObjectName(_fromUtf8("lblQuality"))
        self.gridLayout.addWidget(self.lblQuality, 0, 1, 1, 1)
        self.buttonViewArchive = QtGui.QPushButton(ArchiveControl)
        self.buttonViewArchive.setEnabled(True)
        self.buttonViewArchive.setObjectName(_fromUtf8("buttonViewArchive"))
        self.gridLayout.addWidget(self.buttonViewArchive, 0, 2, 1, 1)
        self.buttonDeleteArchive = QtGui.QPushButton(ArchiveControl)
        self.buttonDeleteArchive.setEnabled(True)
        self.buttonDeleteArchive.setObjectName(_fromUtf8("buttonDeleteArchive"))
        self.gridLayout.addWidget(self.buttonDeleteArchive, 0, 3, 1, 1)

        self.retranslateUi(ArchiveControl)
        QtCore.QMetaObject.connectSlotsByName(ArchiveControl)

    def retranslateUi(self, ArchiveControl):
        ArchiveControl.setWindowTitle(_translate("ArchiveControl", "Form", None))
        self.lblArchiveName.setText(_translate("ArchiveControl", "Archive Name", None))
        self.lblQuality.setText(_translate("ArchiveControl", "1000", None))
        self.buttonViewArchive.setText(_translate("ArchiveControl", "View", None))
        self.buttonDeleteArchive.setText(_translate("ArchiveControl", "Delete", None))

