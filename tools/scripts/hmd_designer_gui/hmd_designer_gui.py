__author__ = 'Douglas Bruey: Synapse Product Development'

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot
from hmd_designer_gui_ui import Ui_MainWindow
import hmd_designer_gui_core
from progress_control import *
from archive_control import *
import os

class ProgressUpdate(QObject):
    updated = pyqtSignal(int,bool,int)
    def __init__(self):
        # Initialize the PunchingBag as a QObject
        QObject.__init__(self)
    def updateProgress(self,index, running, quality):
        self.updated.emit(index, running, quality)

def SimQualityFromText(qualityText):
    parts = str(qualityText).replace("(", " ").replace(")", " ").strip().split()
    try:
        return float(parts[-1])
    except:
        return None

def equalWithAbsError(x1, x2, e = 1e-5):
    return bool( abs(x1 - x2) <= e )

class StartQT4(QtGui.QMainWindow):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.PAGE_PROJECTS = 0
        self.PAGE_PROJECT_FORM = 1
        self.PAGE_PREFERENCES = 2

        self.previousPage = 0

        try:
            self.appCore = hmd_designer_gui_core.hmd_designer_gui_core()
        except RuntimeError:
            print 'Error Initializing Core'
            raise

        self.appCore.registerProgress(self.cbSimProgress)
        self.appCore.registerUpdatedModelFiles(self.updateModelFiles)
        self.appCore.registerUpdatedSolidFiles(self.updateSolidFiles)
        self.appCore.registerUpdatedProjectFiles(self.updateProjectFiles)
        self.appCore.registerUpdatedArchiveList(self.cbArchiveListChanged)
        self.appCore.registerSimulationComplete(self.cbSimulationComplete)
        self.appCore.registerErrorMessage(self.cbErrorMessage)

        self.updatingLists = True
        self.progressWidgets = []

        self.progressUpdater = ProgressUpdate()

        ## Connect signals with our slots
        QtCore.QObject.connect(self.ui.buttonNewProjectCreate,QtCore.SIGNAL("clicked()"), self.slot_buttonNewProjectCreateClicked)
        QtCore.QObject.connect(self.ui.buttonOpenProject,QtCore.SIGNAL("clicked()"), self.slot_buttonOpenProjectClicked)
        QtCore.QObject.connect(self.ui.listboxProjects,QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.slot_buttonOpenProjectClicked)

        QtCore.QObject.connect(self.ui.buttonDeleteProject,QtCore.SIGNAL("clicked()"), self.slot_buttonDeleteProjectClicked)
        QtCore.QObject.connect(self.ui.buttonPrefSave,QtCore.SIGNAL("clicked()"), self.slot_buttonPrefSaveClicked)
        QtCore.QObject.connect(self.ui.buttonPrefCancel,QtCore.SIGNAL("clicked()"), self.slot_buttonPrefCancelClicked)

        QtCore.QObject.connect(self.ui.buttonSimulate,QtCore.SIGNAL("clicked()"), self.slot_buttonSimulateClicked)
        QtCore.QObject.connect(self.ui.buttonEchoCommand,QtCore.SIGNAL("clicked()"), self.slot_buttonEchoCommandClicked)

        QtCore.QObject.connect(self.ui.buttonVisualizeModel,QtCore.SIGNAL("clicked()"), self.appCore.visualizeModel)

        QtCore.QObject.connect(self.ui.buttonBrowseForInputFile,QtCore.SIGNAL("clicked()"), self.slot_buttonBrowseForInputFileClicked)

        QtCore.QObject.connect(self.ui.actionPreferences,QtCore.SIGNAL("triggered()"), self.slot_actionPreferencesTriggered)
        QtCore.QObject.connect(self.ui.actionNewProject,QtCore.SIGNAL("triggered()"), self.slot_actionNewProjectTriggered)
        QtCore.QObject.connect(self.ui.actionSaveProject,QtCore.SIGNAL("triggered()"), self.appCore.saveProjectFile)

        QtCore.QObject.connect(self.ui.listboxObstacles,QtCore.SIGNAL("itemChanged(QListWidgetItem *)"), self.slot_listboxObstaclesItemChanged)
        QtCore.QObject.connect(self.ui.listboxObstacles,QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.slot_listboxObstaclesItemChanged)

        QtCore.QObject.connect(self.ui.comboModelFiles,QtCore.SIGNAL("currentIndexChanged(int)"), self.slot_comboModelFilesCurrentIndexChanged)
        QtCore.QObject.connect(self.ui.comboSensorsFile,QtCore.SIGNAL("currentIndexChanged(int)"), self.slot_comboSensorsFileCurrentIndexChanged)
        QtCore.QObject.connect(self.ui.comboBoxSimulationQuality,QtCore.SIGNAL("currentIndexChanged(const QString &)"), self.slot_simulationQualityChanged)

        QtCore.QObject.connect(self.ui.checkOverridePath,QtCore.SIGNAL("stateChanged(int)"), self.slot_checkOverridePathStateChanged)
        QtCore.QObject.connect(self.ui.checkPersistence,QtCore.SIGNAL("stateChanged(int)"), self.slot_checkPersistenceStateChanged)
        QtCore.QObject.connect(self.ui.checkView2d,QtCore.SIGNAL("stateChanged(int)"), self.slot_checkView2dStateChanged)
        QtCore.QObject.connect(self.ui.checkView3d,QtCore.SIGNAL("stateChanged(int)"), self.slot_checkView3dStateChanged)
        QtCore.QObject.connect(self.ui.checkViewOutputScad,QtCore.SIGNAL("stateChanged(int)"), self.slot_checkViewOutputScadStateChanged)

        QtCore.QObject.connect(self.ui.spinNumSensors,QtCore.SIGNAL("valueChanged(int)"), self.appCore.setNsensors)
        QtCore.QObject.connect(self.ui.spinPermutations,QtCore.SIGNAL("valueChanged(int)"), self.appCore.setPermutations)
        QtCore.QObject.connect(self.ui.spinBoxMaxNormalShift,QtCore.SIGNAL("valueChanged(double)"), self.appCore.setMaxSurfaceAngle)

        QtCore.QObject.connect(self.progressUpdater,QtCore.SIGNAL("updated(int,bool,int)"), self.slot_UpdateProgress)

        ##Initiaize Project Lists
        self.updateProjectFiles()

        ##Initialize the Preferences
        self.initializePreferences()

        ## Set the form to the projects page
        self.ui.actionSaveProject.setEnabled(False)
        self.ui.stackedPages.setCurrentIndex(self.PAGE_PROJECTS)

    ## Define UI Slots
    ## Menu Bar Slots
    def slot_actionPreferencesTriggered(self):
        if self.ui.stackedPages.currentIndex() != self.PAGE_PREFERENCES:
            self.previousPage = self.ui.stackedPages.currentIndex()
        self.ui.stackedPages.setCurrentIndex(self.PAGE_PREFERENCES)

    def slot_actionNewProjectTriggered(self):
        self.ui.stackedPages.setCurrentIndex(self.PAGE_PROJECTS)

    ## Projects Page Slots
    def slot_buttonNewProjectCreateClicked(self):
        self.appCore.createNewProject(str(self.ui.textNewProjectName.text()))
        self.initializeProjectForm()
        self.ui.stackedPages.setCurrentIndex(self.PAGE_PROJECT_FORM)
        self.ui.actionSaveProject.setEnabled(True)

    def slot_buttonOpenProjectClicked(self):
        ## Open the new project
        self.appCore.openProject(str(self.ui.listboxProjects.currentItem().text()))
        self.initializeProjectForm()
        self.ui.stackedPages.setCurrentIndex(self.PAGE_PROJECT_FORM)
        self.ui.actionSaveProject.setEnabled(True)

    def slot_buttonDeleteProjectClicked(self):
        ##Display the confirmation dialog
        projectName = str(self.ui.listboxProjects.currentItem().text())
        reply = QtGui.QMessageBox.question(self, 'Delete Project',
            "Are you sure you want to delete " + projectName + "?", QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.appCore.deleteProject(str(self.ui.listboxProjects.currentItem().text()))

    ## Preferences Page Slots
    def slot_buttonPrefSaveClicked(self):
        self.appCore.setpref_OpenScad(str(self.ui.textOpenScad.text()))
        self.appCore.setpref_ProjectsPath(str(self.ui.textProjectPath.text()))
        if self.appCore.savePreferences():
            self.ui.stackedPages.setCurrentIndex(self.PAGE_PROJECTS)

    def slot_buttonPrefCancelClicked(self):
        self.ui.stackedPages.setCurrentIndex(self.previousPage)
        #Reset to the values in the core
        self.initializePreferences()

    def slot_checkPersistenceStateChanged(self):
        self.appCore.setpref_Persistence(self.ui.checkPersistence.isChecked())
        # print 'slot_checkPersistenceStateChanged'

    def slot_checkOverridePathStateChanged(self):
        self.appCore.setpref_OverrideProjectsPath(self.ui.checkOverridePath.isChecked())
        self.ui.textProjectPath.setEnabled(self.appCore.getpref_OverrideProjectsPath())

    ##Project Form Slots
    def slot_buttonBrowseForInputFileClicked(self):
        #Browse path
        browsePath = self.appCore.getBrowseFolder()

        filters = "Models (*.scad *.stl *.json)"
        selected_filter = "Models (*.scad *.stl *.json)"
        fileObj = QFileDialog.getOpenFileName(self, "Add Input File", browsePath, filters, selected_filter)
        ##Pass the path to the core to copy the file and add it to the project
        if str(fileObj) != '':
            self.appCore.addInputFile(str(fileObj))

    def slot_checkView2dStateChanged(self):
        self.appCore.setView2D(self.ui.checkView2d.isChecked())
        #print 'slot_checkView2dStateChanged'

    def slot_checkView3dStateChanged(self):
        self.appCore.setView3D(self.ui.checkView3d.isChecked())
        #print 'slot_checkView3dStateChanged'

    def slot_checkViewOutputScadStateChanged(self):
        self.appCore.setViewSCAD(self.ui.checkViewOutputScad.isChecked())
        #print 'slot_checkViewOutputScadStateChanged'

    def slot_buttonSimulateClicked(self):
        #Disable the simulate button until the simulation is complete
        self.ui.buttonSimulate.setEnabled(False)

        ##Verify that the user wants to overwrite old simulation data
        if len(self.progressWidgets) > 0:
            reply = QtGui.QMessageBox.question(self, 'Start Simulation',
                "Delete existing simulation outputs and proceed?", QtGui.QMessageBox.Yes |
                QtGui.QMessageBox.No, QtGui.QMessageBox.No)

            if reply == QtGui.QMessageBox.No:
                self.ui.buttonSimulate.setEnabled(True)
                return

        #Clear the progress controls before starting the simulation
        self.clearProgressControls()

        #Add the progress controls
        for index in range(self.appCore.getNumSimsToRun()):
            self.progressWidgets.append(SimProgress(None,index,self.cbViewResults,self.cbArchive,self.cbCancelSimulation,1000))
            self.ui.vertProgressLayout.addWidget(self.progressWidgets[index])

        if not (self.appCore.simulate(self.appCore.getNumSimsToRun())):
            # Clear the progress controls if simulation failed to run
            self.clearProgressControls()
            # Enable the simulation button to try again
            self.ui.buttonSimulate.setEnabled(True)

    def slot_buttonEchoCommandClicked(self):
        self.appCore.echoSimText(self.appCore.getNumSimsToRun())

    def slot_comboModelFilesCurrentIndexChanged(self, index):
        if self.updatingLists == False:
            if index == 0:
                self.appCore.setGenerate(True)
                self.appCore.setModelFile('')
            else:
                self.appCore.setGenerate(False)
                self.appCore.setModelFile(str(self.ui.comboModelFiles.currentText()))
            #print 'slot_comboModelFilesCurrentIndexChanged'
        self.enableNumSensors()
        self.enableSimulateButton()

    def slot_comboSensorsFileCurrentIndexChanged(self, index):
        if self.updatingLists == False:
            self.appCore.setSensorsFile(str(self.ui.comboSensorsFile.currentText()))
            self.enableSimulateButton()

    def slot_listboxObstaclesItemChanged(self, item):
        if item.checkState():
            self.appCore.addObstacleFile(str(item.text()))
        else:
            self.appCore.removeObstacleFile(str(item.text()))
        #print self.appCore.getObstacleFiles()
        #print 'slot_listboxObstaclesItemChanged'

    def slot_simulationQualityChanged( self, newQuality ):
        value = SimQualityFromText(newQuality)
        if value is not None:
            self.appCore.setCoolingRate( value )

    def slot_UpdateProgress(self, index, running, quality):
        #find the widget by index
        currentWidget = None
        for progressWidget in self.progressWidgets:
            if progressWidget.index == index:
                currentWidget = progressWidget
        if currentWidget != None:
            if bool(running):
                currentWidget.incProgress()
                currentWidget.setQuality(int(quality))
            else:
                currentWidget.completeProgress()

    ## Functions
    def enableNumSensors(self):
        self.ui.spinNumSensors.setEnabled(self.appCore.getGenerate())
        self.ui.spinPermutations.setEnabled(self.appCore.getGenerate())
        self.ui.buttonVisualizeModel.setEnabled(not(self.appCore.getGenerate()))

    def enableSimulateButton(self):
        if (self.appCore.getSensorsName() != ''):
            self.ui.buttonSimulate.setEnabled(True)
        else:
            self.ui.buttonSimulate.setEnabled(False)

    def initializeProjectForm(self):
        self.updatingLists = True
        self.ui.comboSensorsFile.clear()
        self.ui.comboModelFiles.clear()
        self.ui.listboxObstacles.clear()
        self.updatingLists = False

        ##Initialize the project form from the core
        self.ui.groupProject.setTitle('Project - ' + self.appCore.getProjectName())

        self.updateModelFiles()
        self.updateSensorFiles()
        self.updateObstacleFiles()

        self.ui.checkView2d.setChecked(self.appCore.getView2D())
        self.ui.checkView3d.setChecked(self.appCore.getView3D())
        self.ui.checkViewOutputScad.setChecked(self.appCore.getViewSCAD())
        self.ui.spinNumSensors.setValue(self.appCore.getNsensors())
        self.ui.spinPermutations.setValue(self.appCore.getPermutations())
        self.ui.spinBoxMaxNormalShift.setValue(self.appCore.getMaxSurfaceAngle())

        for i in xrange(self.ui.comboBoxSimulationQuality.count()):
            value = SimQualityFromText(self.ui.comboBoxSimulationQuality.itemText(i))
            if value is not None and equalWithAbsError( self.appCore.getCoolingRate(), value):
                self.ui.comboBoxSimulationQuality.setCurrentIndex(i)
                break
        
        self.enableNumSensors()

        #Clear current progress widgets
        for i in reversed(range(self.ui.vertProgressLayout.count())):
                simWidget = self.ui.vertProgressLayout.itemAt(i).widget()
                simWidget.setParent(None)
                simWidget.deleteLater()
                self.progressWidgets = []
        #Add existing simulations
        index = 0
        for sim in self.appCore.listSims:
            self.progressWidgets.append(SimProgress(None,sim[0],self.cbViewResults,self.cbArchive,self.cbCancelSimulation,sim[1]))
            self.ui.vertProgressLayout.addWidget(self.progressWidgets[index])
            self.progressWidgets[index].completeProgress()
            index += 1

        #Clear current archive widgets
        for i in reversed(range(self.ui.vertArchiveLayout.count())):
                self.ui.vertArchiveLayout.itemAt(i).widget().setParent(None)
        #Add existing archives
        index = 0
        for archive in self.appCore.listArchives:
            self.addArchiveWidget(archive[0], archive[1])
            index += 1

        #Set the Simulations tab to the active tab
        self.ui.tabSims.setCurrentIndex(0)

        #Enable simulation button
        self.enableSimulateButton()

    def updateProjectFiles(self):
        self.updatingLists = True
        #Remove orphaned projects in the list
        for i in reversed(range(self.ui.listboxProjects.count())):
            #print self.ui.listboxProjects.item(i).text()
            if self.ui.listboxProjects.item(i).text() not in self.appCore.listProjects:
                self.ui.listboxProjects.takeItem(i)

        #Add missing projects
        for filename in self.appCore.listProjects:
            matchingItems = self.ui.listboxProjects.findItems(filename,QtCore.Qt.MatchExactly)
            if len(matchingItems) == 0:
                self.ui.listboxProjects.addItem(filename)
        self.ui.textNewProjectName.setText(self.appCore.getNextNewProject())
        self.updatingLists = False


        if (len(self.appCore.listProjects) != 0):
            #Select the first project by default
            self.ui.listboxProjects.setCurrentRow(0)
            #Enable the state of the open button
            self.ui.buttonOpenProject.setEnabled(True)
        else:
            self.ui.buttonOpenProject.setEnabled(False)

    def updateModelFiles(self):
        self.updatingLists = True
        ##Add new model files
        for modelFile in self.appCore.listModelFiles:
            index = self.ui.comboModelFiles.findText(modelFile, QtCore.Qt.MatchFixedString)
            if index < 0:
                self.ui.comboModelFiles.addItem(modelFile)

        ##Set the current model file for the project
        modelFile = self.appCore.getModelFile()
        index = self.ui.comboModelFiles.findText(modelFile, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.ui.comboModelFiles.setCurrentIndex(index)
        else:
            self.ui.comboModelFiles.setCurrentIndex(0)
        self.updatingLists = False

    def updateSensorFiles(self):
        self.updatingLists = True
        ##Add new sensor files
        for filename in self.appCore.listSolidFiles:
            index = self.ui.comboSensorsFile.findText(filename, QtCore.Qt.MatchFixedString)
            if index < 0:
                self.ui.comboSensorsFile.addItem(filename)

        ##Set the current sensors file for the project
        sensorsFile = self.appCore.getSensorsFile()
        index = self.ui.comboSensorsFile.findText(sensorsFile, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.ui.comboSensorsFile.setCurrentIndex(index)
        else:
            self.ui.comboSensorsFile.setCurrentIndex(-1)
        self.updatingLists = False

    def updateObstacleFiles(self):
        for filename in self.appCore.listSolidFiles:
            if (filename != ''):
                matchingItems = self.ui.listboxObstacles.findItems(filename,QtCore.Qt.MatchExactly)
                if len(matchingItems) == 0:
                    item = QtGui.QListWidgetItem()
                    item.setText(filename)
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    item.setCheckState(QtCore.Qt.Unchecked)
                    if filename in self.appCore.getObstacleFiles():
                        item.setCheckState(QtCore.Qt.Checked)
                    self.ui.listboxObstacles.addItem(item)

    def updateSolidFiles(self):
        self.updateSensorFiles()
        self.updateObstacleFiles()

    def verifyFileName(self, filename):
        chars = set('\/:*?"<>|')
        for c in filename:
            if str(c) in chars:
                return False
        return True

    def initializePreferences(self):
        ##Initialize the Preferences
        self.ui.checkOverridePath.setChecked(self.appCore.getpref_OverrideProjectsPath())
        self.ui.textOpenScad.setText(self.appCore.getpref_OpenScad())
        self.ui.textProjectPath.setText(self.appCore.getpref_ProjectsPath())
        self.ui.checkPersistence.setChecked(self.appCore.getpref_Persistence())
        self.ui.textProjectPath.setEnabled(self.appCore.getpref_OverrideProjectsPath())

    def clearProgressControls(self):
        ##Clear any old progress controls
        self.progressWidgets = []
        for i in reversed(range(self.ui.vertProgressLayout.count())):
            self.ui.vertProgressLayout.itemAt(i).widget().setParent(None)

    ## Callbacks

    def cbSimProgress(self,index,running,quality):
        self.progressUpdater.updateProgress(index,running,quality)

    def cbViewResults(self,index):
        self.appCore.viewSimulation(index)

    def cbArchive(self,index):
        #get the name for the archive folder
        archiveName, ok = QtGui.QInputDialog.getText(self, "Archive Simulation", "Enter a name for the archive.",QLineEdit.Normal, self.appCore.getNextArchive())

        if ok:
            #guarantee no reserved characters were used
            while (not self.verifyFileName(archiveName)) and ok:
                archiveName, ok = QtGui.QInputDialog.getText(self, "Archive Simulation", "Enter a name for the archive. '\\ / : * ? \" < > |' are invalid. ",QLineEdit.Normal, str(archiveName))
            if ok:
                for archive in self.appCore.listArchives:
                    if str(archive[0]) == str(archiveName):
                        reply = QtGui.QMessageBox.question(self, 'Save Archive',
                            "An archive named " + str(archiveName) + " already exists. Overwrite?", QtGui.QMessageBox.Yes |
                            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
                        if reply == QtGui.QMessageBox.No:
                            return
            else:
                return
        else:
            return

        #archive the simulation
        self.appCore.archive(index, archiveName)

    def cbCancelSimulation(self,index):
        self.appCore.cancelSimulation(index)

    def cbViewArchive(self,name):
        self.appCore.viewArchive(name)
        print 'View Archive'

    def cbDeleteArchive(self,name):
        reply = QtGui.QMessageBox.question(self, 'Delete Archive',
            "Delete " + str(name) + "?", QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.No:
            return

        #delete the archive
        self.appCore.deleteArchive(name)

    def cbArchiveListChanged(self):

        #update or add any new archive controls in the gui
        for archive in self.appCore.listArchives:
            found = False
            for i in range(self.ui.vertArchiveLayout.count()):
                archiveWidget = self.ui.vertArchiveLayout.itemAt(i).widget()
                if archive[0] == archiveWidget.name:
                    #update the control in the list if it exists
                    archiveWidget.setQuality(archive[1])
                    found = True
            if not found:
                #add the control if it does not
                self.addArchiveWidget(archive[0], archive[1])

        #delete any old archive controls in the gui
        #Search for widgets in the current core list
        for i in reversed(range(self.ui.vertArchiveLayout.count())):
            archiveWidget = self.ui.vertArchiveLayout.itemAt(i).widget()
            found = False
            for archive in self.appCore.listArchives:
                coreArchiveName = archive[0]
                if archiveWidget.name == coreArchiveName:
                    found = True
            #delete the widget if it is no longer in the core list
            if not found:
                self.ui.vertArchiveLayout.itemAt(i).widget().setParent(None)

    def cbSimulationComplete(self):
        #Enable simulation button
        self.ui.buttonSimulate.setEnabled(True)

    def cbErrorMessage(self, name, description):
        reply = QtGui.QMessageBox.question(self, name, description, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

    def addArchiveWidget(self, name, quality):
        newArchiveWidget = ArchiveControl(None, name, self.cbViewArchive, self.cbDeleteArchive, quality)
        self.ui.vertArchiveLayout.addWidget(newArchiveWidget)

    def closeEvent(self, event):

        #self.appCore.cancelSimulation(0)
        self.appCore.cancelAllSimulations()

        #ready to exit
        can_exit = True
        if can_exit:
            event.accept()  # let the window close
        else:
            event.ignore()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())


