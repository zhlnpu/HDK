from enum import Enum
import json
import os

class StlFormat(Enum):
    bin = 1
    ascii = 2

class PackageType(Enum):
    sim = 1
    arch = 2

class path_factory():
    def __init__(self):

        self._overrideProjectPaths = False
        self._projectsPath = ''

        self.paths = {}
        self.hmd_designer_path = []
        self.hmd_designer_viewer_path = []
        self.sensor_sim_plot_path = []

        pathsFile = 'steam.paths'
        if os.path.exists('p4v.paths'):
            pathsFile = 'p4v.paths'
        with open(pathsFile, 'r') as text_file:
            self.paths = json.load(text_file)

        self.hmd_designer_path = self.paths['hmd_designer']
        #print str(os.path.join(*self.hmd_designer_path))
        self.hmd_designer_viewer_path = self.paths['hmd_designer_viewer']
        #print str(os.path.join(*self.hmd_designer_viewer_path))
        self.sensor_sim_plot_path = self.paths['sensor_sim_plot']
        #print str(os.path.join(*self.sensor_sim_plot_path))

        #print self.hmd_designer_path
        #print self.hmd_designer_viewer_path
        #print self.sensor_sim_plot_path

    def setOverrideProjectsPath(self, value):
        self._overrideProjectPaths = value
    def getOverrideProjectsPath(self, value):
        return self._overrideProjectPaths

    def setProjectsPath(self, value):
        self._projectsPath = value
    def getProjectsPath(self, value):
        return self._projectsPath

    def preferencesFile(self):
        return 'hmd_designer_gui.pref'

    def projectsFolder(self):
        if not self._overrideProjectPaths:
            return str(os.path.join(os.path.expanduser('~'),'Documents','SteamVRTrackingHDK','HmdDesignerProjects'))
        else:
            return str(os.path.join(self._projectsPath,'SteamVRTrackingHDK','HmdDesignerProjects'))

    def toolsFolder(self):
        return str(os.path.join('tools'))

    def hmd_designer(self):
        return str(os.path.join(*self.hmd_designer_path))

    def hmd_designer_viewer(self):
        return str(os.path.join(*self.hmd_designer_viewer_path))

    def sensor_sim_plot(self):
        return str(os.path.join(*self.sensor_sim_plot_path))

    def shapesScadFile(self):
        return str(os.path.join('shapes.scad'))

    def projectFolder(self, projectName):
        return str(os.path.join(self.projectsFolder(), projectName))

    def projectFile(self, projectName):
        return str(os.path.join(self.projectFolder(projectName), projectName + '.PrjHmdDes'))

    def inFolder(self, projectName):
        return str(os.path.join(self.projectFolder(projectName), 'in'))

    def outFolder(self, projectName):
        return str(os.path.join(self.projectFolder(projectName), 'out'))

    def archivesFolder(self, projectName):
        return str(os.path.join(self.outFolder(projectName), 'archives'))

    def simsFolder(self, projectName):
        return str(os.path.join(self.outFolder(projectName), 'simulations'))

    def simFolder(self, projectName, simIndex):
        return str(os.path.join(self.simsFolder(projectName), 'sim' + str(simIndex)))

    def archiveFolder(self, projectName, archiveName):
        return str(os.path.join(self.archivesFolder(projectName), archiveName))

    def outModelFile(self, projectName, model):
        return str(os.path.join(self.outFolder(projectName), model + '.json'))

    def outStlFile(self, projectName, stlName, format = StlFormat.ascii):
        return str(os.path.join(self.outFolder(projectName), stlName + self.stlSuffix(format) + '.stl'))

    def simScadFile(self, projectName, identifier, packageType = PackageType.sim):
        if packageType == PackageType.sim:
            return str(os.path.join(self.simFolder(projectName, identifier), projectName + '.scad'))
        else:
            return str(os.path.join(self.archiveFolder(projectName, identifier), projectName + '.scad'))

    def simModelFile(self, projectName, identifier, packageType = PackageType.sim):
        if packageType == PackageType.sim:
            return str(os.path.join(self.simFolder(projectName, identifier), projectName + '.json'))
        else:
            return str(os.path.join(self.archiveFolder(projectName, identifier), projectName + '.json'))

    def simText(self, projectName, identifier, packageType = PackageType.sim):
        if packageType == PackageType.sim:
            return str(os.path.join(self.simFolder(projectName, identifier), projectName + '.simTxt'))
        else:
            return str(os.path.join(self.archiveFolder(projectName, identifier), projectName + '.simTxt'))

    def simMetaData(self, projectName, identifier, packageType = PackageType.sim):
        if packageType == PackageType.sim:
            return str(os.path.join(self.simFolder(projectName, identifier), projectName + '.simMeta'))
        else:
            return str(os.path.join(self.archiveFolder(projectName, identifier), projectName + '.simMeta'))

    def simPlot(self, projectName, identifier, packageType = PackageType.sim):
        if packageType == PackageType.sim:
            return str(os.path.join(self.simFolder(projectName, identifier), projectName + '.png'))
        else:
            return str(os.path.join(self.archiveFolder(projectName, identifier), projectName + '.png'))

    def visualizeFolder(self, projectName):
        return str(os.path.join(self.outFolder(projectName), 'visualize'))

    def visualizeModelFolder(self, projectName, modelName):
        return str(os.path.join(self.visualizeFolder(projectName), modelName))

    def visualizeScad(self, projectName, modelName):
        return str(os.path.join(self.visualizeModelFolder(projectName, modelName), 'visualize.scad'))

    def visualizeShapesScad(self, projectName, modelName):
        return str(os.path.join(self.visualizeModelFolder(projectName, modelName), 'shapes.scad'))

    def visualizeModelFile(self, projectName, modelName):
        return str(os.path.join(self.visualizeModelFolder(projectName, modelName), modelName + '.json'))

    def visualizeModelWriteScadFolder(self, projectName, modelName):
        return str(os.path.join(self.visualizeModelFolder(projectName, modelName), 'writescad'))

    def visualizeStl(self,projectName, modelName, stlName, format = StlFormat.ascii):
        return str(os.path.join(self.visualizeModelFolder(projectName, modelName), stlName + self.stlSuffix(format) + '.stl'))

    def writeScadFolder(self):
        return os.path.join('writescad')

    def cadToStlFilename(self,filename, format):
        suffix = '_ascii'
        if format == StlFormat.bin:
            suffix = '_bin'
        return str(str(filename).lower().split('.scad')[0].split('.stl')[0].split('_ascii')[0].split('_bin')[0] + suffix + '.stl')

    def stlSuffix(self,format):
        if format == StlFormat.ascii:
            return '_ascii'
        else:
            return '_bin'

