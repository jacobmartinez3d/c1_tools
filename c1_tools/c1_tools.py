import nuke
import nukescripts
from nukescripts import panels
from PySide import QtGui
import os
import re
from string import ascii_lowercase
import shutil
import threading

c1_folders = {
'___CameraRaw': False,
'__ProductionStitches': False,
'_ImageSequences': False,
'zFINAL': False
}

#_Check if gladiator exists, or have user choose local__________________________
def findGladiator():
    for c in ascii_lowercase:
        gladiator = c + ':' + os.sep + 'Departments' + os.sep + '_Post' + os.sep + '__Projects' + os.sep
        if os.path.exists(gladiator):
            nuke.message('found gladiator drive on drive: ' + c)
            return gladiator
        else:
            nuke.message('No Gladiator __Projects/ directory found, please navigate to a local directory containing project folders named like this:\n\n"018_tigerrescue_TGR/6.VFX/[shot folders]"')
            gladiator = nuke.getFilename('Use local __Projects directory...')
        return gladiator

#_Scan directory and compile list of found/missing c1 folders___________________
def scanDir(inputDir):
    foundDirs = []
    foundC1Dirs = []
    missing = []

    for thing in os.listdir(inputDir):
        # check if its a folder or not...
        if os.path.isdir(os.path.join(inputDir, thing)):
            foundDirs.append(thing)
    if len(foundDirs) < 1:
        foundDirs = None
    # Validate...
    names = c1_folders.keys()
    if foundDirs:
        for folder in foundDirs:
            # set validation flags...
            for i in range(0, len(names)):
                if folder == names[i]:
                    c1_folders[names[i]] = True
                    foundC1Dirs.append(folder)

    # then append any missing folders to list
    for folder in c1_folders:
        if c1_folders[folder] == False:
            missing.append(folder)
    return {'foundDirs': foundDirs, 'foundC1Dirs': foundC1Dirs, 'missing': missing}

#_compile list of versions in directory(folders only)___________________________
def retrieveShotFolderVersions(foundDirs):
    if not foundDirs:
        return None
    versions = []
    for folder in foundDirs:
        if len(folder.split('_v')) > 1:
            version = int(folder.split('_v')[1])
            if not version < 1:
                versions.append(folder)
    if not versions:
        versions = None
    return versions

#_Initialize selected local directory as a C1 shotFolder________________________
def createLocalShotFolder():
    shotFolder = nuke.getFilename('Navigate to local Shot Folder...')
    parentFolder = os.path.abspath(os.path.join(shotFolder, os.pardir))

    # run a quick validation on the parent folder to see if user mis-clicked
    parentResults = scanDir(parentFolder)['foundC1Dirs']
    if parentResults:
        if nuke.ask('This folder appears to be nested inside a shot folder, did you mean to choose, ' + parentFolder + '?'):
            shotFolder = parentFolder
            print 'changing shot folder to: ' + parentFolder + '...'
    if os.path.isdir(shotFolder):
        shot = shotFolder.split(os.sep)[-1]
    else:
        nuke.message('You must choose a folder or directory!')
        return

    results = scanDir(shotFolder)
    # if missing C1 folders exist, ask user to create
    if results['missing']:
        if nuke.ask('The following folders are missing: ' + '\n' + str(results['missing'])[1:-1] + ', create them now?'):
            for missingDir in results['missing']:
                os.mkdir(os.path.join(shotFolder, missingDir))
            results['missing'] = None
    else:
        results['missing'] = None

    data = {'found': str(results['foundDirs']), 'missing': results['missing'], 'versions': retrieveShotFolderVersions(results['foundDirs'])}
    print 'Found:' + '\n', data['found']
    print 'Missing C1 Subfolders:' + '\n', data['missing']
    print 'Versions:' + '\n', data['versions']

    return data

#_Scan for missing rener frames in write output directory_______________________
def Luis_Solver():
    node = nuke.thisNode()

    file = node.knob('file').getValue()
    filepath = os.path.split(file)[0]
    filename = os.path.split(file)[1]
    arr = []
    missing = []
    i = 0

    for img in os.listdir(filepath):
        n = int(re.search(r'\d+', img).group(0))
        arr.append(n)
        if len(arr) > 1:
            difference = arr[i] - arr[i-1]
            if difference > 1:
                #print(range(arr[i-1]+1, arr[i]))
                missing.append(range(arr[i-1]+1, arr[i]))
        i+=1
    if len(missing) > 0:
        string = ''
        # hyphenate list...
        i = 1
        for span in missing:
            if len(span) > 2:
                string = string + str(span[0]) + '-' + str(span[-1])
            else:
                string = string + str(span[0])
            if i < len(missing):
                string = string + ', '
            i+=1
        if nuke.ask('Found missing frames: ' + string + '\n' + 'Render these frames now?'):
            ranges = nuke.FrameRanges()
            for s in string.split(', '):
                fr = nuke.FrameRange(s)
                ranges.add(fr)

def versionUp(file):
    filepath = os.path.abspath(file)
    filename = os.path.basename(file).split('_v')
    currentVersion = int(os.path.basename(file).split('_v')[1].split('.')[0])
    versionFolder = os.path.abspath(os.path.join(filepath, os.pardir))
    shotFolder = os.path.dirname(versionFolder)
    newVersion = str(currentVersion + 1).zfill(3)
    newDir = os.path.join(shotFolder, filename[0] + '_v' + newVersion)
    newFileName = filename[0] + '_v' + newVersion + '_%V' + '.04d.png'

    if os.path.exists(newDir):
        nuke.message("Looks like there's already a folder for version " + newVersion + ', aborting!')
        return

    os.mkdir(newDir)
    os.mkdir(os.path.join(newDir, 'Prerenders'))

    for node in nuke.allNodes():
        if node.name() == "_render":
            node.knob('file').setValue('Prerenders/' + newFileName)

    #save nuke script
    nuke.scriptSaveAs(os.path.join(newDir, filename[0] + '_v' + newVersion + '.nk'))
    nuke.message('Current version: ' + newVersion)
    return

#_Submit Shot___________________________________________________________________
def submitShot(file):
    filepath = os.path.abspath(file)
    filename = os.path.basename(file).split('_v')
    currentVersion = int(os.path.basename(file).split('_v')[1].split('.')[0])
    versionFolder = os.path.abspath(os.path.join(filepath, os.pardir))
    localShotFolder = os.path.dirname(versionFolder)
    shotName = os.path.basename(localShotFolder)
    showCode = filename[0].split('_')[0]
    gladiator = findGladiator()

    #_Define remote directory for current shot folder___________________________
    def setServerShotFolder(gladiator):
        # scan gladiator and return the remote shot folder path that matches current local shot folder name
        serverShowFolder = None
        try:
            for folder in os.listdir(gladiator):
                # validate that it's a directory
                if os.path.isdir(os.path.join(gladiator, folder)):
                    # check if ends with showCode
                    if folder.split('_')[-1] == showCode:
                        serverShowFolder = os.path.join(gladiator, folder)
            serverShotFolder = os.path.join(os.path.join(serverShowFolder, '6.VFX'), shotName)
            return serverShotFolder
        except Exception, e:
            return nuke.messageg('Failed to find remote shot folder for this shot! \n\n' + 'error: ' + str(e))
    serverShotFolder = setServerShotFolder(gladiator)

    #_get latest version on server______________________________________________
    def retrieveLatestShotVersion(serverShotFolder):
        i = 0
        latestVersion = 0
        for root, dirs, files in os.walk(serverShotFolder):
            # stop after first level
            if i > 0:
                break
            for folder in dirs:
                pieces = folder.split('_v')
                if len(pieces) > 1:
                    # one last small validation..
                    if pieces[0].split('_')[0] == showCode:
                        versionNum = int(pieces[1])
                        if versionNum > latestVersion:
                            latestVersion = versionNum
        return latestVersion
    latestVersion = retrieveLatestShotVersion(serverShotFolder)

    #_Validate and create new remote version____________________________________
    def createNewRemoteVersion(serverShotFolder, latestVersion):
        newVersionFolderName = shotName + '_v' + str(latestVersion + 1).zfill(3)
        newVersionFolderPath = os.path.join(serverShotFolder, newVersionFolderName)
        localPrerenders = os.path.join(versionFolder, 'Prerenders')
        remotePrerenders = os.path.join(newVersionFolderPath, 'Prerenders')

        # validate Prerenders folder
        if len(os.listdir(localPrerenders)) < 2:
            return nuke.message('Your Prerenders folder has less than 2 files in it. Please check and re-submit!')
        try:
            # create folders/files on Gladiator...
            os.mkdir(newVersionFolderPath)
            # do little dance to save to remote dir, then revert back to previous local session
            currentScript = nuke.toNode('root').name()
            nuke.scriptSaveAs(os.path.join(newVersionFolderPath, newVersionFolderName + '.nk'))
            nuke.toNode('root').knob('name').setValue(currentScript)
            os.mkdir(remotePrerenders)
        except Exception, e:
            nuke.message('Problem occurred when attempting to create new version folder at: ' + remotePrerenders + '.\n\n' + 'error: ' + str(e))

        def copyPrerenders():
            task = nuke.ProgressTask("Submitting...")
            files = os.listdir(localPrerenders)
            progIncr = 100.0 / len(files)

            for i, f in enumerate(files):
                if task.isCancelled():
                    nuke.executeInMainThread( nuke.message, args=( "Aborted!" ) )
                    return;
                task.setProgress(int(i * progIncr))
                task.setMessage(f)
                copyFrom = os.path.join(localPrerenders, f)
                copyTo = os.path.join(remotePrerenders, f)
                shutil.copyfile(copyFrom, copyTo)

            nuke.executeInMainThread(nuke.message, args=('Shot succsessfully submitted to Gladiator as: ' + newVersionFolderName))
            return

        if nuke.ask('Latest version of this shot on Gladiator is:\n\n' + shotName + '_v' + str(latestVersion).zfill(3) + '.\n\n' + 'Continue submission as: ' + newVersionFolderName + '?'):
            threading.Thread( target = copyPrerenders ).start()

    createNewRemoteVersion(serverShotFolder, latestVersion)
