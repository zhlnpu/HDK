import sys
import os

def update_scripts():
    # Get the current path to the active python.exe
    pathPython = sys.executable
    print pathPython

    # Get a list of all the .py files in the Scripts directory
    dirScripts = os.path.join(os.path.dirname(pathPython),"Scripts")
    print dirScripts

    # Open each file and replace the first line if it starts with #!
    listPyFiles = []
    for filename in os.listdir(dirScripts):
        filePath = os.path.join(dirScripts,filename)
        if os.path.isfile(filePath):
            if (filename[-3:] == '.py'):
                #print filename
                #read the file into memory
                lines = []
                with open(filePath, 'r') as infile:
                    for line in infile:
                        lines.append(line)
                #write the output file
                if lines[0][:2] == '#!':
                    lines[0] = '#!"' + pathPython + '"\n'
                    with open(filePath, 'w') as outfile:
                        for line in lines:
                            outfile.write(line)


