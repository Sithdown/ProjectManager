import os
import sys
import shutil
import datetime
import json
import re
import zipfile

import ttkbootstrap as tk
from ttkbootstrap.constants import *
from tkinter import simpledialog

path = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

logstdout = os.path.join(path, "Logs", "stdout-pm_pyw.txt")
logstderr = os.path.join(path, "Logs", "stderr-pm_pyw.txt")

sys.stdout = open(logstdout, "w")
sys.stderr = open(logstderr, "w")


def mainLoop():
    ROOT = tk.Window(themename="darkly")

    ROOT.eval('tk::PlaceWindow . center')
    ROOT.title('SPManager')
    ROOT.resizable(False, False)
    ROOT.geometry('240x60')
    ROOT.lift()
    ROOT.call('wm', 'attributes', '.', '-topmost', True)

    text_disp= tk.Button(ROOT, 
                       text="New",
                       bootstyle="success",
                       command=createNewProject
                       )

    text_disp.pack(side=tk.LEFT, padx=5, pady=10)

    exit_button = tk.Button(ROOT,
                       text="Clean",
                       bootstyle="danger-outline",
                       command=cleanProjects)
    exit_button.pack(side=tk.RIGHT, padx=5, pady=10)

    ROOT.mainloop()


def createPath(root, path):
    try:
        os.makedirs(os.path.join(root,path), exist_ok=True)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s" % path)

def createNewProject():
    '''
    - New Project
        - <Year>/<MM_Month>/<ProjectNumberPad000>_<ProjectName>
            - Assets
            - Builds
            - Delivery
            - Docs
            - Generated
            - Info
    '''
    now = datetime.datetime.now()
    year = '{:02d}'.format(now.year)
    month = '{:02d}'.format(now.month)
    #day = '{:02d}'.format(now.day)
    #hour = '{:02d}'.format(now.hour)
    #minute = '{:02d}'.format(now.minute)
    #day_month_year = '{}-{}-{}'.format(year, month, day)
    month_name = now.strftime("%B")

    createPath(root, year)
    yearPath = os.path.join(root, year)
    monthPath = os.path.join(yearPath, month+"_"+month_name)

    createPath(yearPath, monthPath)

    ROOT = tk.Window(themename="darkly")
    ROOT.withdraw()
    # the input dialog
    newProjectName = simpledialog.askstring(title="Project Creator", prompt="Project Name?")

    config['lastProjectNumber'] = config['lastProjectNumber'] + 1;

    projectPath = os.path.join(monthPath, str(config['lastProjectNumber']).zfill(3)+"_"+newProjectName)

    for path in createPaths:
        createPath(projectPath,path)


    with open('config.json', "w") as configFile:
        print(json.dumps(config, indent=4))
        configFile.write(json.dumps(config, indent=4))

    quit()

def getYears():

    years = []

    for item in os.listdir(root):
        if(item.isnumeric()):
            years.append(item)

    return years

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))

def rPaths(d):

    for path in removePaths:
        pathToRemove = os.path.join(d, path)
        shutil.rmtree(pathToRemove, ignore_errors=True)

    for path in os.listdir(d):
        newPath = os.path.join(d,path)
        if(os.path.isdir(newPath)):

            if(path not in ignorePaths):
                rPaths(newPath)
            else:
                #print("IGNORED "+newPath)
                break

    dirName = os.path.basename(d)
    if(projectPathFormat.match(dirName)):
        print("\t\t"+dirName)
        #zip folder contents
        if(dirName not in ignoreProjects):
            print("\t\t\tZipping...")
            zipf = zipfile.ZipFile(os.path.join(d,"../"+dirName+".zip"), 'w', zipfile.ZIP_DEFLATED)
            zipdir(d, zipf)
            zipf.close()

def cleanProjects():

    print("----------------------------------------\n")

    years = getYears()
    # For every year
    for y in years:
        print(y+"\n")

        yPath = os.path.join(root, y)

        # For every folder in year
        for item in os.listdir(yPath):

            yDir = os.path.join(os.path.join(root, y),item)

            if(os.path.isdir(yDir)):

                if(monthPathFormat.match(item)):
                    
                    print("\t"+item)

                    # We are on a project folder
                    for i in os.listdir(yDir):
                        if(os.path.isdir(os.path.join(yDir,i))):
                            rPaths(os.path.join(yDir,i))

                else:
                    rPaths(yDir)

            else:
                print("    \t"+item)

        print("\n")

    quit()


#open json config file
configFile = open(os.path.join(path,'config.json'))
config = json.load(configFile)
configFile.close()

root = config['root']
createPaths = config["newProjectConfig"]["createPaths"]
removePaths = config["cleanProjectConfig"]["removePaths"]
ignorePaths = config["cleanProjectConfig"]["ignorePaths"]
ignoreProjects = config["cleanProjectConfig"]["ignoreProjects"]
projectPathFormat = re.compile(config["projectPathFormat"])
monthPathFormat = re.compile(config["monthPathFormat"])

mainLoop()
