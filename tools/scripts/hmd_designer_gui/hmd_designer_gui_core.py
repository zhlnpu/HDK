__author__ = 'Douglas Bruey: Synapse Product Development'

import os
import stat
import json
import shutil
import subprocess
from threading import Thread
import sys
from model_visualizer import model_visualizer
from PIL import Image
from path_factory import *
import update_scripts as us
import copy
import math

class hmd_designer_gui_core():
    constDictDefaultProject = {'projectName':'DefaultName',
                        '/coolingrate' : 0.9,
                        '/maxsurfaceangle' : 0.0,
                        '/generate':True,
                        '/model':"",
                        '/nsensors':32,
                        '/sensors':"",
                        '/obstacles':[],
                        'permutations':1,
                        'view2D':True,
                        'view3D':True,
                        'viewSCAD':True,
                        'browseFolder' : './projects'
                        }
    constDictDefaultPrefs = {'ScadEditor':str(os.path.join('C:\\','Program Files (x86)','Notepad++','notepad++.exe')),
                        'OpenScad':str(os.path.join('C:\\','Program Files','OpenSCAD','openscad.exe')),
                        'Persistence':True,
                        'OverrideProjectsPath':False,
                        'ProjectsPath': str(os.path.join('C:\\'))
                        }
    def __init__(self):

        #Callbacks
        self.cbProgress = None
        self.cbUpdatedModelFiles = None
        self.cbUpdatedSolidFiles = None
        self.cbUpdatedProjectFiles = None
        self.cbUpdatedArchiveList = None
        self.cbSimulationComplete = None
        self.cbErrorMessage = None

        # clean up the Scripts directory
        us.update_scripts()

        #Load preferences
        self.dictPreferences = copy.deepcopy(self.constDictDefaultPrefs)
        self.pf = path_factory()
        self._loadPreferences()

        # initialize the paths from a config file
        self.pf.setOverrideProjectsPath(self.dictPreferences['OverrideProjectsPath'])
        self.pf.setProjectsPath(self.dictPreferences['ProjectsPath'])

        # Verify that the the correct files are present
        self.InstallVerified = self._checkInstall()
        if not self.InstallVerified:
            raise RuntimeError('Installation')

        ##Application Variables
        self.listProjects = []
        self._createProjectsList()

        ##Project Variables
        self.dictProject = copy.deepcopy(self.constDictDefaultProject)
        self.listSolidFiles=['']
        self.listModelFiles=['Generate']

        self.listSims=[]
        self.listSimCancelled = []
        self.numRunningSims = 0
        self.listArchives = []

        self._modelVisualizer = model_visualizer()

    ##Register callbacks
    def registerProgress(self,value):
        self.cbProgress = value
    def registerUpdatedProjectFiles(self, value):
        self.cbUpdatedProjectFiles = value
    def registerUpdatedModelFiles(self, value):
        self.cbUpdatedModelFiles = value
    def registerUpdatedSolidFiles(self, value):
        self.cbUpdatedSolidFiles = value
    def registerUpdatedArchiveList(self, value):
        self.cbUpdatedArchiveList = value
    def registerSimulationComplete(self, value):
        self.cbSimulationComplete = value
    def registerErrorMessage(self, value):
        self.cbErrorMessage = value

    ##Set/Get private members
    def getInstallVerified(self):
        return self.InstallVerified

    def _setProjectName(self, value):
        self.dictProject['projectName'] = value
    def getProjectName(self):
        return self.dictProject['projectName']

    def setSensorsFile(self,value):
        self.dictProject['/sensors'] = value
        if self.getpref_Persistence():
            self.saveProjectFile()
    def getSensorsFile(self):
        return self.dictProject['/sensors']
    def getSensorsName(self):
        return self.dictProject['/sensors'].lower().split('.scad')[0].split('.stl')[0].split('_ascii')[0].split('_bin')[0]

    def setModelFile(self,value):
        self.dictProject['/model'] = value
        if self.getpref_Persistence():
            self.saveProjectFile()
    def getModelFile(self):
        return self.dictProject['/model']
    def getModelName(self):
        return self.getModelFile().lower().split('.json')[0]

    def setGenerate(self,value):
        self.dictProject['/generate'] = value
        if self.getpref_Persistence():
            self.saveProjectFile()
    def getGenerate(self):
        return self.dictProject['/generate']

    def setNsensors(self,value):
        self.dictProject['/nsensors'] = value
        if self.getpref_Persistence():
            self.saveProjectFile()
    def getNsensors(self):
        return self.dictProject['/nsensors']

    def setPermutations(self,value):
        self.dictProject['permutations'] = value
        if self.getpref_Persistence():
            self.saveProjectFile()
    def getPermutations(self):
        return self.dictProject['permutations']

    def getNumSimsToRun(self):
        if self.getGenerate():
            return self.dictProject['permutations']
        else:
            return 1
    
    def getCoolingRate(self):
        return self.dictProject['/coolingrate']

    def setCoolingRate(self, coolingrate):
        coolingrate = float(coolingrate)
        if coolingrate == self.dictProject['/coolingrate']:
            return
        self.dictProject['/coolingrate'] = coolingrate
        if self.getpref_Persistence():
            self.saveProjectFile()

    def getMaxSurfaceAngle(self):
        return self.dictProject['/maxsurfaceangle']
    
    def setMaxSurfaceAngle(self, maxsurfaceangle):
        maxsurfaceangle = float(maxsurfaceangle)
        if maxsurfaceangle == self.dictProject['/maxsurfaceangle']:
            return
        self.dictProject['/maxsurfaceangle'] = maxsurfaceangle
        if self.getpref_Persistence():
            self.saveProjectFile()

    def setView2D(self,value):
        self.dictProject['view2D'] = value
        if self.getpref_Persistence():
            self.saveProjectFile()
    def getView2D(self):
        return self.dictProject['view2D']

    def setView3D(self,value):
        self.dictProject['view3D'] = value
        if self.getpref_Persistence():
            self.saveProjectFile()
    def getView3D(self):
        return self.dictProject['view3D']

    def setViewSCAD(self,value):
        self.dictProject['viewSCAD'] = value
        if self.getpref_Persistence():
            self.saveProjectFile()

    def getBrowseFolder(self):
        return self.dictProject['browseFolder']
    def setBrowseFolder(self,value):
        self.dictProject['browseFolder'] = value
        self.saveProjectFile()

    def getViewSCAD(self):
        return self.dictProject['viewSCAD']

    def getObstacleFiles(self):
        return self.dictProject['/obstacles']

    def setpref_ScadEditor(self, value):
        self.dictPreferences['ScadEditor'] = value
    def getpref_ScadEditor(self):
        return self.dictPreferences['ScadEditor']

    def setpref_OpenScad(self, value):
        self.dictPreferences['OpenScad'] = value
    def getpref_OpenScad(self):
        return self.dictPreferences['OpenScad']

    def setpref_Persistence(self, value):
        self.dictPreferences['Persistence'] = value
    def getpref_Persistence(self):
        return self.dictPreferences['Persistence']

    def setpref_OverrideProjectsPath(self, value):
        self.dictPreferences['OverrideProjectsPath'] = value
        self.pf.setOverrideProjectsPath(value)
    def getpref_OverrideProjectsPath(self):
        return self.dictPreferences['OverrideProjectsPath']

    def setpref_ProjectsPath(self, value):
        self.dictPreferences['ProjectsPath'] = value
        self.pf.setProjectsPath(value)
    def getpref_ProjectsPath(self):
        return self.dictPreferences['ProjectsPath']

    ## Public Methods
    def createNewProject(self, newProjectName):
        ##Initialize the project data
        self._clearProjectData()
        self._setProjectName(newProjectName)
        ## Create the project folder structure
        if not os.path.exists(self.pf.projectsFolder()): os.makedirs(self.pf.projectsFolder())
        if not os.path.exists(self.pf.projectFolder(newProjectName)): os.makedirs(self.pf.projectFolder(newProjectName))
        if not os.path.exists(self.pf.inFolder(newProjectName)): os.makedirs(self.pf.inFolder(newProjectName))
        if not os.path.exists(self.pf.outFolder(newProjectName)): os.makedirs(self.pf.outFolder(newProjectName))
        if not os.path.exists(self.pf.archivesFolder(newProjectName)): os.makedirs(self.pf.archivesFolder(newProjectName))
        if not os.path.exists(self.pf.simsFolder(newProjectName)): os.makedirs(self.pf.simsFolder(newProjectName))
        ##Dump the project data to a project file
        self.saveProjectFile()
        self._createProjectsList()

    def deleteProject(self, projectName):
        shutil.rmtree(self.pf.projectFolder(projectName))
        self._createProjectsList()

    def openProject(self, projectName):
        ##Initialize the project data
        self._clearProjectData()

        ## Read in the project file
        self._loadProject(projectName)

        ##Scan in the input files in the project folder
        for filename in self._getImmediateFiles(self.pf.inFolder(self.getProjectName())):
            self._addFileToLists(filename)

        ##Check for the old project folder structure and update
        self._updateFolderStructure()

        ##create the sim list
        self._refreshSimList()

        ##create the archive list
        self._refreshArchiveList()

        ##remove orphaned entries from project dictionary
        self._scrubProjectFiles()

    def saveProjectFile(self):
        with open(self.pf.projectFile(self.getProjectName()), 'w') as text_file:
            text_file.write("{0}".format(json.dumps(self.dictProject)))

    def savePreferences(self):
        try:
            self._createProjectsList()
            with open(self.pf.preferencesFile(), 'w') as text_file:
                text_file.write("{0}".format(json.dumps(self.dictPreferences)))
            # Refresh the project list in case the projects path changed
            return True
        except:
            return False


    def addInputFile(self, filePath):
        srcFile = filePath
        addFile = srcFile.rsplit('/',1)[1]
        dstFile = os.path.join(self.pf.inFolder(self.getProjectName()),addFile)
        #print srcFile + ' ' + dstFile
        if os.path.abspath(srcFile) != os.path.abspath(dstFile):
            shutil.copyfile(srcFile, dstFile)
        self._addFileToLists(addFile)

        #save the current path
        self.setBrowseFolder(str(os.path.dirname(srcFile)))

        return addFile

    def getNextNewProject(self):
        suffixes = []
        #Get the NewProject Suffixes
        for projName in self.listProjects:
            if projName[:10] == 'NewProject' and (projName[10:].isdigit() or projName[10:] ==''):
                if projName[10:] =='':
                    num = 0
                else:
                    num = int(projName[10:])
                suffixes.append(num)

        #Find the first available suffix
        x = 0
        if len(suffixes) != 0:
            for x in xrange(len(suffixes)+1):
                if x not in suffixes:
                    break

        newSuffix = ''
        if x != 0:
            newSuffix = str(x)
        newName = 'NewProject' + newSuffix
        return newName

    def getNextArchive(self):
        suffixes = []
        #Get the Archive Suffixes
        for archive in self.listArchives:
            archiveName = archive[0]
            if (archiveName[:7] == 'archive') and (archiveName[7:].isdigit()):
                num = int(archiveName[7:])
                suffixes.append(num)

        #Find the first available suffix
        x = 0
        if len(suffixes) != 0:
            for x in xrange(len(suffixes)+1):
                if x not in suffixes:
                    break

        newSuffix = str(x)
        newName = 'archive' + newSuffix
        return newName

    def addObstacleFile(self,obstacleFile):
        if obstacleFile not in self.dictProject['/obstacles']:
            self.dictProject['/obstacles'].append(obstacleFile)
            if self.getpref_Persistence():
                self.saveProjectFile()
            return True
        return False

    def removeObstacleFile(self,obstacleFile):
        if obstacleFile in self.dictProject['/obstacles']:
            self.dictProject['/obstacles'].remove(obstacleFile)
            if self.getpref_Persistence():
                self.saveProjectFile()
            return True
        return True

    def echoSimText(self, numSims):
        print ''
        for index in range(numSims):
            print 'Command ' + str(index) + '> ' + ' '.join( self._buildCmdHmdDesigner(index, self.dictProject) )

    def simulate(self, numSims):
        self.listSims = []
        if not (self._deleteOutputFiles()):
            return False
        if not self._preprocessInputFiles():
            return False
        if not self._preprocessOutputFiles():
            return

        for index in range(numSims):
            simFolder = self.pf.simFolder(self.getProjectName(), index)
            if not os.path.exists(simFolder): os.makedirs(simFolder)
            if self.getGenerate() == False:
                ##Copy the json model file to the sim directory
                shutil.copy(self.pf.outModelFile(self.getProjectName(), self.getModelName()), self.pf.simModelFile(self.getProjectName(), index, PackageType.sim))

        self.numRunningSims = numSims

        myThreads = []
        self.listSimCancelled = []
        for index in range(numSims):
            self.listSims.append([index, 1000])

        for index in range(numSims):
            self.listSimCancelled.append(False)
            myThreads.append(Thread(target=self._workerRunHmdDesigner, args=(self,index,self._buildCmdHmdDesigner(index, self.dictProject))))
            myThreads[index].start()

        return True

    def simulationCompleted(self):
        self.numRunningSims = self.numRunningSims - 1
        if self.numRunningSims == 0:
            print "All simulations complete"
            #Clean up cancelled simulations
            for sim in self.listSims:
                if self.listSimCancelled[sim[0]]:
                    print "Deleting cancelled simulation output " + str(sim[0])
                    self.deleteSim(sim[0])
        if self.cbSimulationComplete != None:
            self.cbSimulationComplete()

    def cancelSimulation(self, index):
        self.listSimCancelled[index] = True

    def cancelAllSimulations(self):
        for i in range(len(self.listSimCancelled)):
            self.listSimCancelled[i] = True

    def visualizeModel(self):
        if not self._verifyOpenScadPath(self.dictPreferences['OpenScad']):
            return

        #create the visualize folder
        if not os.path.exists(self.pf.visualizeFolder(self.getProjectName())):
            os.makedirs(self.pf.visualizeFolder(self.getProjectName()))

        #create a folder for this model file or replace it if it already exists
        visualizeModelFolderPath = self.pf.visualizeModelFolder(self.getProjectName(), self.getModelName())
        #print visualizeModelFolderPath
        if os.path.exists(visualizeModelFolderPath):
            if not self._rmtree(visualizeModelFolderPath):
                return False
        os.makedirs(visualizeModelFolderPath)

        #preprocess the scad and stl files into the out directory
        if not self._preprocessInputFiles():
            return
        if not self._preprocessOutputFiles():
            return

        #copy the json file to visualize
        visualizeModelFile =  self.pf.visualizeModelFile(self.getProjectName(), self.getModelName())
        shutil.copy(self.pf.outModelFile(self.getProjectName(), self.getModelName()),visualizeModelFile)

        #copy the shapes.scad file and write.scad to the visualize folder
        shutil.copy(self.pf.shapesScadFile(), self.pf.visualizeShapesScad(self.getProjectName(), self.getModelName()))
        shutil.copytree(self.pf.writeScadFolder(), self.pf.visualizeModelWriteScadFolder(self.getProjectName(), self.getModelName()))

        #clear the read-only flags on scad files copied from the install folder
        self._clearReadOnly(visualizeModelFolderPath)

        #get the sensors file name
        if (self.getSensorsFile() != ""):
            sensorsName = self.getSensorsName()
        else:
            sensorsName = ""

        #copy the sensors ascii stl file to visualize
        stlFiles = []
        if (sensorsName != ""):
            shutil.copy(self.pf.outStlFile(self.getProjectName(), sensorsName, StlFormat.ascii), self.pf.visualizeStl(self.getProjectName(),self.getModelName(),sensorsName, StlFormat.ascii))
            stlFiles.append(self.pf.visualizeStl(self.getProjectName(),self.getModelName(),sensorsName, StlFormat.ascii))

        #generate the visualizer scad file
        self._modelVisualizer.visualizeModel(visualizeModelFile, stlFiles, self.pf.visualizeScad(self.getProjectName(), self.getModelName()))

        #launch openscad to view the new file
        subprocess.Popen(self._buildCmdOpenVisualizeScad(self.getModelName()),stdout=subprocess.PIPE)

        return True

    def viewSimulation(self, index):
        self._view(index, PackageType.sim)
        print 'View Simulation'

    def viewArchive(self, name):
        self._view(name, PackageType.arch)
        print 'View Archive'

    def archive(self, index, name):
        archiveName = str(name)
        #create the parent archive folder if it does not already exist
        if not os.path.exists(self.pf.archivesFolder(self.getProjectName())):
            os.makedirs(self.pf.archivesFolder(self.getProjectName()))

        #delete the old archive folder if it exists
        self.deleteArchive(archiveName)

        #copy the sim folder to the archive folder
        shutil.copytree(self.pf.simFolder(self.getProjectName(), index), self.pf.archiveFolder(self.getProjectName(), archiveName))

        #Refresh the list from
        self._refreshArchiveList()

        #signal the UI that the archive was updated
        self.cbUpdatedArchiveList()

        #print self.listArchives

    def deleteArchive(self, name):
        #remove the folder from the archive directory
        if os.path.exists(self.pf.archiveFolder(self.getProjectName(), name)):
            if not (self._rmtree(self.pf.archiveFolder(self.getProjectName(), name))):
                return

        # remove the archive from the archive list
        for i in reversed(range(len(self.listArchives))):
            if str(self.listArchives[i][0]) == name:
                del self.listArchives[i]

        #signal the UI that the archive list has updated
        self.cbUpdatedArchiveList()

    def deleteSim(self, index):
        if os.path.exists(self.pf.simFolder(self.getProjectName(), index)):
            shutil.rmtree(self.pf.simFolder(self.getProjectName(), index))

    ## Private Methods

    def _clearReadOnly(self, root):
        for dirpath, dirnames, filenames in os.walk(root):
            for fname in filenames:
                full_path = os.path.join(dirpath, fname)
                os.chmod(full_path, stat.S_IWRITE)
            for dname in dirnames:
                full_path = os.path.join(dirpath, dname)
                os.chmod(full_path, stat.S_IWRITE)
                #self._clearReadOnly(full_path)

    def _view(self, identifier, packageType = PackageType.sim):
        if self.dictProject['view2D']:
            simTxtPath = self.pf.simText(self.getProjectName(), identifier, packageType)
            simPngPath = self.pf.simPlot(self.getProjectName(), identifier, packageType)
            if os.path.exists(simTxtPath):
                if os.path.exists(simPngPath):
                    img = Image.open(simPngPath)
                    img.show()
                else:
                    subprocess.Popen(self._buildCmdSensorSimPlot(simTxtPath),stdout=subprocess.PIPE)
        if self.dictProject['viewSCAD']:
            outScadPath = self.pf.simScadFile(self.getProjectName(), identifier, packageType)
            if os.path.exists(outScadPath):
                self._replaceImportPathsInScad(outScadPath)
                subprocess.Popen(self._buildCmdOpenOutScad(outScadPath),stdout=subprocess.PIPE)
        if self.dictProject['view3D']:
            modelPath = self.pf.simModelFile(self.getProjectName(), identifier, packageType)
            simTextPath = self.pf.simText(self.getProjectName(), identifier, packageType)
            sensorsPath = str(os.path.join(self.pf.outFolder(self.getProjectName()), self.pf.cadToStlFilename(self.getSensorsFile(), StlFormat.bin)))
            if os.path.exists(modelPath) and os.path.exists(simTextPath) and os.path.exists(sensorsPath):
                subprocess.Popen(self._buildHmdDesignerViewer(modelPath, simTextPath, sensorsPath), stdout=subprocess.PIPE)

    def _loadPreferences(self):
        if not os.path.exists(self.pf.preferencesFile()):
            self.savePreferences()
        else:
            with open(self.pf.preferencesFile(), 'r') as text_file:
                filePreferences = json.load(text_file)
                #print filePreferences
                #Iterate through the saved settings and update the local dictionary
                #This allows updates to the default dictionary wihtout breaking backward compatibility
                #with older preference files.
                for key, value in filePreferences.iteritems():
                    if key in self.dictPreferences:
                        self.dictPreferences[key] = filePreferences[key]

                #print self.dictPreferences


    def _loadProject(self, projectName):
        #start with a fresh copy of the default project dictionary
        self.dictProject = copy.deepcopy(self.constDictDefaultProject)

        #set the project name
        self._setProjectName(projectName)

        #load the json file of the project
        with open(self.pf.projectFile(self.getProjectName()), 'r') as text_file:
            fileProject = json.load(text_file)
            #Iterate through the saved settings and update the local dictionary
            #This allows updates to the default dictionary wihtout breaking backward compatibility
            #with older project files.
            for key, value in fileProject.iteritems():
                if key in self.dictProject:
                    self.dictProject[key] = fileProject[key]

        #print self.dictProject

    def _createProjectsList(self):
        self._createProjectsDirectory()
        #Pull in the list of projects
        projectsFolder = self.pf.projectsFolder()
        #Create the projects folder if it does not already exist
        self.listProjects = self._getImmediateSubdirectories(projectsFolder)
        # signal the UI that the list changed
        if self.cbUpdatedProjectFiles != None:
            self.cbUpdatedProjectFiles()


    def _refreshArchiveList(self):
        self.listArchives = []
        if os.path.exists(self.pf.archivesFolder(self.getProjectName())):
            for foldername in self._getImmediateSubdirectories(self.pf.archivesFolder(self.getProjectName())):
                #Get the quality number from the simulation meta data
                simMetaDataPath = self.pf.simMetaData(self.getProjectName(),foldername, PackageType.arch)
                quality = self._getQualityFromMeta(simMetaDataPath)
                self.listArchives.append([foldername,quality])

        #signal the UI that the archive list has changed
        self.cbUpdatedArchiveList()

    def _refreshSimList(self):
        self.listSims = self._getListSims(self.pf.simsFolder(self.getProjectName()))

    def _clearProjectData(self):
        ##Create a new project dictionary
        self.dictProject = copy.deepcopy(self.constDictDefaultProject)
        self.listSolidFiles = ['']
        self.listModelFiles = ['Generate']
        self.listSims = []
        self.listArchives = []

    def _deleteOutputFiles(self):
        outFolderPath = self.pf.outFolder(self.getProjectName())
        listOutFiles = self._getImmediateFiles(outFolderPath)

        try:
            for fileName in listOutFiles:
                os.remove(os.path.join(self.pf.outFolder(self.getProjectName()),fileName))
        except OSError:
            self.cbErrorMessage('Delete Error', 'Error deleting ' + fileName + '. Please close any applications that may be using the file.')
            return False
        listFolders = self._getImmediateSubdirectories(self.pf.simsFolder(self.getProjectName()))
        for foldername in listFolders:
            #print foldername
            #print foldername[:3]
            if foldername[:3] == 'sim':
                if not (self._rmtree(str(os.path.join(self.pf.simsFolder(self.getProjectName()),foldername)))):
                    return False
        return True

    def _addFileToLists(self, filename):
        addExt = filename.rsplit('.',1)[1]
        if addExt.lower() == 'json':
            if filename not in self.listModelFiles:
                self.listModelFiles.append(filename)
                self.cbUpdatedModelFiles()
        elif addExt.lower() == 'scad' or addExt.lower() == 'stl':
            if filename not in self.listSolidFiles:
                self.listSolidFiles.append(filename)
                self.cbUpdatedSolidFiles()

    def _preprocessInputFiles(self):
        if not self._verifyOpenScadPath(self.dictPreferences['OpenScad']):
            return False
        print 'PreProcessing Input Files'
        inFolderPath = self.pf.inFolder(self.getProjectName())
        outFolderPath = self.pf.outFolder(self.getProjectName())
        for fileName in self.listSolidFiles:
            fileExtension = str(fileName).split('.')[-1]
            fileInPath = os.path.join(inFolderPath,fileName)
            fileOutPath = os.path.join(outFolderPath,fileName)
            if fileExtension.lower() == 'stl':
                ##Copy to the output folder
                shutil.copy(fileInPath,fileOutPath)
            elif fileExtension.lower() == 'scad':
                #print 'process scad ' + fileName
                ##Convert to stl in the output folder
                fileOutPath = fileOutPath.split('.')[-2]+'.stl'
                subprocess.call([self.dictPreferences['OpenScad'],fileInPath,'-o',fileOutPath],stdout=subprocess.PIPE)
                #print 'completed process scad'
        for fileName in self.listModelFiles:
            fileExtension = str(fileName).split('.')[-1]
            fileInPath = os.path.join(inFolderPath,fileName)
            fileOutPath = os.path.join(outFolderPath,fileName)
            if fileExtension == 'json':
                ##Copy to the output folder
                shutil.copy(fileInPath,fileOutPath)
        return True

    def _preprocessOutputFiles(self):
        retval = True
        print 'Preprocessing Output Files'
        outFolderPath = self.pf.outFolder(self.getProjectName())
        listOutputFile = self._getImmediateFiles(outFolderPath)
        for fileName in listOutputFile:
            fileExtension = str(fileName).split('.')[-1]
            if fileExtension.lower() == 'stl':
                ## Create ASCII and binary versions
                self._convertStlInPlace(os.path.join(outFolderPath, fileName))
            elif fileExtension.lower() == 'json':
                ## Scrub json files
                retval = self._scrubJsonFile(os.path.join(outFolderPath, fileName))
        return retval

    def _convertStlInPlace(self, filePath):
        print 'Converting STL files'
        ## Determine type of file (ASCII or binary)
        isAsciiFormat = self._stlIsAscii(filePath)
        if isAsciiFormat:
            ##Rename to ASCII
            newFilePath = self.pf.cadToStlFilename(filePath, StlFormat.ascii)
            if filePath != newFilePath:
                shutil.move(filePath, newFilePath)
            ##Convert to BINARY
            p1 = subprocess.call([str(os.path.join(os.path.dirname(sys.executable),'Scripts','stl2bin.exe')),newFilePath,os.path.join(self.pf.cadToStlFilename(filePath, StlFormat.bin))],stdout=subprocess.PIPE)
        else:
            ##Rename to BINARY
            newFilePath = self.pf.cadToStlFilename(filePath, StlFormat.bin)
            if filePath != newFilePath:
                shutil.move(filePath, newFilePath)
            ##Convert to ASCII
            p1 = subprocess.call([str(os.path.join(os.path.dirname(sys.executable),'Scripts','stl2ascii.exe')),newFilePath,os.path.join(self.pf.cadToStlFilename(filePath, StlFormat.ascii))],stdout=subprocess.PIPE)

    def _stlIsAscii(self, filePath):
        solidFound = False
        facetFound = False
        endSolidFound = False
        with open(filePath,'r') as stlfile:
            lines = stlfile.readlines()

        #check that the first word is 'solid'
        solidFound = lines[0].strip(' \t').split(' ',1)[0].lower() == 'solid'

        #check that the second line starts with 'facet'
        if len(lines) > 1:
            facetFound = lines[1].strip(' \t').split(' ',1)[0].lower() == 'facet'

        #check that the last line (with text) starts with 'endsolid'
        for index in reversed(range(len(lines))):
            line = lines[index]
            if not line.isspace():
                endSolidFound = lines[index].strip().split(' ',1)[0].lower() == 'endsolid'
                break

        return (solidFound and facetFound and endSolidFound)

    def _scrubJsonFile(self, filePath):
        #Open the old file for reading
        with open(filePath,'r') as jsonFile:
            lines = jsonFile.readlines()

        with open(filePath,'w') as jsonFile:
            for line in lines:
                if str(line).strip()[:2] != '//':
                    jsonFile.write(line)

        return self._formatJsonInPlace(filePath)

    def _verifyJsonFormating(self, jsonPath):
        jsonName = os.path.basename(jsonPath)

        #read in the entire file to a string
        try:
            with open(jsonPath, 'r') as jsonFile:
                strJson = jsonFile.read()
        except ValueError as e:
            dialogTitle = 'File Error: ' + jsonName
            self.cbErrorMessage(dialogTitle , str(e))
            return False


        #create the line/column map for non-whitespace characters
        line = 1
        column = 1
        mapChars = []
        for character in strJson:
            #record the line and column per character
            if not character.isspace():
                mapChars.append([line,column])
            if character == '\n':
                line = line + 1
                column = 1
            else:
                column = column + 1

        strippedJson = ''.join(strJson.split())

        #Search for invalid character combinations in the string
        dialogTitle = 'JSON Error'
        errors = []

        #Find trailing commas
        errorIndex = strippedJson.find(',}')
        if errorIndex >= 0:
            self.cbErrorMessage(dialogTitle, 'Error in file: ' + jsonName + '\n\nTrailing comma at ' + str(mapChars[errorIndex]))
            return False

        errorIndex = strippedJson.find(',]')
        if errorIndex >= 0:
            self.cbErrorMessage(dialogTitle, 'Error in file: ' + jsonName + '\n\nTrailing comma at ' + str(mapChars[errorIndex]))
            return False

        for i in range(len(strippedJson)):
            if strippedJson[i] == '.':
                if not strippedJson[i-1].isdigit():
                    self.cbErrorMessage(dialogTitle, 'Error in file: ' + jsonName + '\n\nLeading decimal at ' + str(mapChars[i]))
                    return False

        return True

    def _formatJsonInPlace(self, jsonPath):
        modelPoints = []
        modelNormals = []
        jsonName = os.path.basename(jsonPath)

        #Verify JSON formating not caught by the python json parser
        if not self._verifyJsonFormating(jsonPath):
            return False

        #import the json file
        try:
            with open(jsonPath, 'r') as jsonFile:
                model = json.load(jsonFile)
        except ValueError as e:
            dialogTitle = 'JSON Error'
            self.cbErrorMessage(dialogTitle , 'Error in file: ' + jsonName + '\n' + str(e))
            return False

        # get the imu
        if 'imu' in model:
            imu = model['imu']
        else:
            imu = None

        #set the next level
        if 'lighthouse_config' in model:
            model = model['lighthouse_config']

        if 'modelNormals' in model:
            modelNormals = model['modelNormals']
        if 'modelPoints' in model:
            modelPoints = model['modelPoints']
        if 'channelMap' in model:
            channelMap = model['channelMap']
        else:
            #create the channel map if it does not exist
            channelMap = range(len(modelNormals))

        errorTitle = 'JSON Error'

        #Verify that all arrays are the same length
        lengths = [len(modelNormals), len(modelPoints), len(channelMap)]
        if len(set(lengths)) > 1:
            self.cbErrorMessage(errorTitle, 'Error in file: ' + jsonName + '\n\nmodelNormals, modelPoints, and channelMap must have the same number of elements.')
            return False

        index = 0
        for normal in modelNormals:
            #Verify there are three components
            if len(normal) != 3:
                errorMessage = 'Error in file: ' + jsonName + '\n\nmodelNormal[' + str(index) + '] must have exactly three elements.'
                self.cbErrorMessage(errorTitle, errorMessage)
                return False

            #Verify that the magnitude is 1
            magnitude = math.sqrt(math.pow(normal[0],2) + math.pow(normal[1],2) + math.pow(normal[2],2))
            if abs(1.0-magnitude) > 0.001:
                errorMessage = 'Error in file: ' + jsonName + '\n\nmodelNormal[' + str(index) + ']\nmagnitude = ' + str(magnitude) + '\nNormals must be unit vectors'
                self.cbErrorMessage(errorTitle, errorMessage)
                return False
            index = index + 1

        index = 0
        #Verify positions have three elements
        for point in modelPoints:
            if len(point) != 3:
                errorMessage = 'Error in file: ' + jsonName + '\n\nmodelPoint[' + str(index) + '] must have exactly three elements.'
                self.cbErrorMessage(errorTitle, errorMessage)
                return False
            if (abs(point[0]) >= 1) or (abs(point[1]) >= 1) or (abs(point[2]) >= 1):
                errorMessage = 'Error in file: ' + jsonName + '\n\nmodelPoint[' + str(index) + '] contains an element greater than 1.\nPoint units must be meters.'
                self.cbErrorMessage(errorTitle, errorMessage)
                return False
            index = index + 1

        #Verify imu values
        if imu != None:
            for key, value in imu.iteritems():
                # Verify there are three components
                if len(value) != 3:
                    errorMessage = 'Error in file: ' + jsonName + '\n\nIMU: ' + key + ' must have exactly three elements.'
                    self.cbErrorMessage(errorTitle, errorMessage)
                    return False

                # Verify the magnitude is 1
                if key[:4].lower() == 'plus':
                    normal = value
                    magnitude = math.sqrt(math.pow(normal[0], 2) + math.pow(normal[1], 2) + math.pow(normal[2], 2))
                    if abs(1.0 - magnitude) > 0.001:
                        errorMessage = 'Error in file: ' + jsonName + '\n\nIMU: ' + key + '\nmagnitude = ' + str(magnitude) + '\nMust be unit vector'
                        self.cbErrorMessage(errorTitle, errorMessage)
                        return False

                #Verify units are meters
                if key.lower() == 'position':
                    point = value
                    if (abs(point[0]) >= 1) or (abs(point[1]) >= 1) or (abs(point[2]) >= 1):
                        errorMessage = 'Error in file: ' + jsonName + '\n\nIMU: ' + key + ' contains an element greater than 1.\nUnits must be meters.'
                        self.cbErrorMessage(errorTitle, errorMessage)
                        return False

        #write the output json
        with open(jsonPath, 'w') as jsonFile:
            jsonFile.write('{\n')
            jsonFile.write('\t"channelMap" : ' + str(channelMap) + ',\n')

            jsonFile.write('\t"modelNormals" : [\n')
            i = 0
            for normal in modelNormals:
                i = i + 1
                jsonFile.write('\t\t' + str(normal))
                if i != len(modelNormals):
                    jsonFile.write(',\n')
                else:
                    jsonFile.write('\n')
            jsonFile.write('\t],\n')

            jsonFile.write('\t"modelPoints" : [\n')
            i = 0
            for point in modelPoints:
                i = i + 1
                jsonFile.write('\t\t' + str(point))
                if i != len(modelPoints):
                    jsonFile.write(',\n')
                else:
                    jsonFile.write('\n')

            if imu != None:
                jsonFile.write('\t]\n')
                jsonFile.write('\t,"imu" : {\n')
                jsonFile.write('\t\t"plus_x" : ')
                jsonFile.write(str(imu['plus_x']) + ',\n')
                jsonFile.write('\t\t"plus_z" : ')
                jsonFile.write(str(imu['plus_z']) + ',\n')
                jsonFile.write('\t\t"position" : ')
                jsonFile.write(str(imu['position']) + '\n')
                jsonFile.write('\t}\n')
            else:
                jsonFile.write('\t]\n')


            jsonFile.write('}\n')

            return True

    def _replaceImportPathsInScad(self, scadPath):
        #Open the old file for reading
        with open(scadPath,'r') as jsonFile:
            lines = jsonFile.readlines()

        with open(scadPath,'w') as jsonFile:
            for line in lines:
                commands = line.strip().split('import',1)
                if len(commands) >= 2:
                    #replace the line with a new line that uses a relative path
                    path = commands[1].split('"')[1]
                    relativePath =  os.path.join('..', '..', os.path.basename(path))
                    relativePath = relativePath.replace('\\', '\\\\')
                    newLine = '\t' + commands[0] + 'import("' + relativePath + '", convexity = 4);\n'
                    jsonFile.write(newLine)
                else:
                    jsonFile.write(line)

    def _buildCmdHmdDesigner(self, index, dictProj):
        print 'Building HMD Designer command line'
        outFolderPath = self.pf.outFolder(self.getProjectName())
        sensorsPath = os.path.join(outFolderPath, self.pf.cadToStlFilename(self.getSensorsFile(), StlFormat.ascii))
        genModelPath = self.pf.simModelFile(self.getProjectName(),index, PackageType.sim)
        outScadPath = self.pf.simScadFile(self.getProjectName(), index, PackageType.sim)

        cmdHmdDesigner = []
        cmdHmdDesigner.append(self.pf.hmd_designer())
        if dictProj['/generate']:
            cmdHmdDesigner.append('/generate')
            cmdHmdDesigner.append('/nsensors')
            cmdHmdDesigner.append(str(dictProj['/nsensors']))
            cmdHmdDesigner.append('/maxsurfaceangle')
            cmdHmdDesigner.append(str(dictProj['/maxsurfaceangle']))
            cmdHmdDesigner.append('/coolingrate')
            cmdHmdDesigner.append(str(dictProj['/coolingrate']))
            cmdHmdDesigner.append('/outmodel')
            cmdHmdDesigner.append(genModelPath)
        else:
            cmdHmdDesigner.append('/model')
            cmdHmdDesigner.append(self.pf.outModelFile(self.getProjectName(), self.getModelName()))

        cmdHmdDesigner.append('/sensors')
        cmdHmdDesigner.append(sensorsPath)

        listObstacles = list(dictProj['/obstacles'])
        for obstacle in listObstacles:
            cmdHmdDesigner.append('/obstacles')
            ##Get the filename
            fileName = str(os.path.join(outFolderPath, self.pf.cadToStlFilename(obstacle, StlFormat.ascii)))
            cmdHmdDesigner.append(str(fileName))

        if dictProj['/generate']:
            cmdHmdDesigner.append('/outscad')
            cmdHmdDesigner.append(outScadPath)

        return cmdHmdDesigner

    def _buildCmdSensorSimPlot(self,filePath):
        print 'Building sensor_sim_plot.py command line'
        cmdSensorSimPlot = []
        toolPath = self.pf.sensor_sim_plot()
        cmdSensorSimPlot.append(sys.executable)
        cmdSensorSimPlot.append(toolPath)
        cmdSensorSimPlot.append('/tightbounds')
        cmdSensorSimPlot.append(filePath)
        return cmdSensorSimPlot

    def _buildCmdOpenOutScad(self, filePath):
        if not self._verifyOpenScadPath(self.dictPreferences['OpenScad']):
            return
        print 'Building open output scad command line'
        cmdOpenOutScad = []
        cmdOpenOutScad.append(self.dictPreferences['OpenScad'])
        cmdOpenOutScad.append(filePath)
        #print cmdOpenOutScad
        return cmdOpenOutScad

    def _buildCmdOpenVisualizeScad(self, modelName):
        if not self._verifyOpenScadPath(self.dictPreferences['OpenScad']):
            return
        print 'Building open output scad command line'
        cmdOpenOutScad = []
        cmdOpenOutScad.append(self.dictPreferences['OpenScad'])
        cmdOpenOutScad.append(self.pf.visualizeScad(self.getProjectName(), modelName))
        #print cmdOpenOutScad
        return cmdOpenOutScad

    def _buildHmdDesignerViewer(self, modelPath, simTextPath, sensorsPath):
        print 'Building hdm designer viewer command line'
        projectName = self.dictProject['projectName']
        toolPath = self.pf.hmd_designer_viewer()

        cmd = []
        cmd.append(toolPath)
        cmd.append('/model')
        cmd.append(modelPath)
        cmd.append('/simdata')
        cmd.append(simTextPath)
        cmd.append('/sensors')
        cmd.append(sensorsPath)

        listObstacles = list(self.dictProject['/obstacles'])
        for obstacle in listObstacles:
            cmd.append('/obstacles')
            ##Get the filename
            outFolderPath = self.pf.outFolder(self.getProjectName())
            fileName = str(os.path.join(outFolderPath, self.pf.cadToStlFilename(obstacle, StlFormat.bin)))
            cmd.append(str(fileName))

        #print cmd
        return cmd

    def _verifyOpenScadPath(self, pathToExe):
        if os.path.exists(pathToExe):
            return True
        else:
            self.cbErrorMessage('OpenSCAD Error', 'Cannot find:\n\r' + pathToExe + '\n\rInstall OpenSCAD or change the path under File > Preferences...')
            return False

    def _getImmediateSubdirectories(self, a_dir):
        return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

    def _getImmediateFiles(self, a_dir):
        return [name for name in os.listdir(a_dir)
            if not os.path.isdir(os.path.join(a_dir, name))]

    def _getQualityFromMeta(self, path):
        if os.path.exists(path):
            with open(path, 'r') as text_file:
                dictSimMetaData = json.load(text_file)
            quality = dictSimMetaData['quality']
        else:
            quality = -1

        return quality

    def _workerRunHmdDesigner(self,parent,index,cmdLine):
        dots = 0
        cancelled = False

        #Create the output file for simulation data
        simTextPath = self.pf.simText(self.getProjectName(), index, PackageType.sim)
        fileHandle = open(simTextPath, 'w')

        p1 = subprocess.Popen(cmdLine, stderr=subprocess.PIPE, stdout=fileHandle)
        if parent.getGenerate() == True:
            strQuality = '1000'
        else:
            strQuality = '-1'
        parent.cbProgress(index, True, int(strQuality))
        captureQuality = False
        while True:
            out = p1.stderr.read(1)
            if out == '' and p1.poll() != None:
                parent.cbProgress(index, False, int(strQuality))
                break
            elif parent.listSimCancelled[index]:
                #terminate the subprocess
                p1.terminate()
                p1.wait()
                cancelled = True
                break
            else:
                #increment a progress bar and update the quality value
                if out == '.':
                    captureQuality = False
                    dots += 1
                    if strQuality.isdigit():
                        parent.cbProgress(index,True,int(strQuality))
                elif out == '(':
                    dots = 0
                    strQuality = ''
                    captureQuality = True
                else:
                    dots = 0
                    if captureQuality:
                        strQuality = strQuality + out

                #print output to console if it is not just a series of periods
                if dots <= 3:
                    sys.stderr.write(out)
                    sys.stderr.flush()

        #Save Simulation Metadata
        if self.getGenerate() == True:
            if strQuality.isdigit():
                dictSimMetaData = {'quality':int(strQuality)}
                simMetaDataPath = self.pf.simMetaData(self.getProjectName(), index, PackageType.sim)
                with open(str(simMetaDataPath), 'w') as text_file:
                    text_file.write("{0}".format(json.dumps(dictSimMetaData)))

        ##Close the output file
        fileHandle.close()

        print '\nHmdDesigner Complete ' + str(index)
        #delete the partial sim folder if the simulation was cancelled
        if cancelled:
            print 'Cancelled ' + str(index)

        #decrement with each completion so the main app knows when all the simulations are finished
        parent.simulationCompleted()

    def _scrubProjectFiles(self):
        #/model (json)
        modelFile = self.getModelFile()
        if modelFile not in self.listModelFiles:
            self.setModelFile('')
            self.setGenerate(True)
        #/sensors (scad or stl)
        sensorsFile = self.getSensorsFile()
        if sensorsFile not in self.listSolidFiles:
            self.setSensorsFile('')
        #/obstacles (scad or stl)
        listObstacles = self.getObstacleFiles()
        #print listObstacles
        for i in reversed(range(len(listObstacles))):
            if listObstacles[i] not in self.listSolidFiles:
                del listObstacles[i]
        #print self.dictProject

    def _updateFolderStructure(self):
        #Create the simulations folder
        if not os.path.exists(self.pf.simsFolder(self.getProjectName())):
            self.pf.simsFolder(self.getProjectName())

            #Move the sim folders into 'simulations'
            outFolder = self.pf.outFolder(self.getProjectName())
            for sim in self._getListSims(outFolder):
                srcFolder = os.path.join(outFolder, 'sim' + str(sim[0]))
                dstFolder = os.path.join(outFolder, 'simulations', 'sim' + str(sim[0]))
                #copy the simulation folder
                shutil.copytree(srcFolder, dstFolder)
                #delete the old simulation folder
                shutil.rmtree(srcFolder)

        #rename the archive forlder to archives
        oldArchiveFolder = os.path.join(self.pf.outFolder(self.getProjectName()),'archive')
        newArchiveFolder = self.pf.archivesFolder(self.getProjectName())
        if os.path.exists(oldArchiveFolder):
            if not os.path.exists(newArchiveFolder):
                os.rename(oldArchiveFolder, newArchiveFolder)

    def _getListSims(self, parentFolder):
        listSims = []
        for foldername in self._getImmediateSubdirectories(parentFolder):
            if foldername[:3] == 'sim':
                if foldername[3:].isdigit():
                    simIndex = int(foldername[3:])
                    ##Get quality from metadata
                    simMetaDataPath = self.pf.simMetaData(self.getProjectName(), simIndex, PackageType.sim)
                    quality = self._getQualityFromMeta(simMetaDataPath)
                    listSims.append([simIndex,quality])
        return listSims

    def _rmtree(self, path):
        try:
            shutil.rmtree(path)
            return True
        except OSError:
            self.cbErrorMessage('Delete Error', 'Error removing ' + os.path.basename(path) + '. Please close any applications that may be using the folder or files within it.')
            return False

    def _createProjectsDirectory(self):
        projectsFolder = self.pf.projectsFolder()
        try:
            if not os.path.exists(projectsFolder): os.makedirs(projectsFolder)
        except OSError as e:
            self.cbErrorMessage('Error', e.strerror)

    def _checkInstall(self):
        filesVerified = True
        #Verify that the project directory exists
        self._createProjectsDirectory()

        checkPaths = [self.pf.hmd_designer_viewer(), self.pf.hmd_designer(), self.pf.sensor_sim_plot()]

        #Check for the folders
        for path in checkPaths:
            if not os.path.exists(path):
                filesVerified = False
                errorText = os.path.basename(path) + ' not found in ' + os.path.dirname(path)
                print errorText

        return filesVerified