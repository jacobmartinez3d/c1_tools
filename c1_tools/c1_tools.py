import nuke
import nukescripts
#from nukescripts import panels
from PySide import QtGui
import os
import re
from string import ascii_lowercase
import shutil
import threading

import submitShot as submitShotClass

c1_folders = {
'___CameraRaw': False,
'__ProductionStitches': False,
'_ImageSequences': False,
'zFINAL': False
}

#_Utility Functions_____________________________________________________________

def findGladiator():
    debugDir = 'g' + ':' + os.sep + 'Users' + os.sep + 'Jacob' + os.sep
    for c in ascii_lowercase:
        gladiator = c + ':' + os.sep + 'Departments' + os.sep + '_Post' + os.sep + '__Projects' + os.sep
        if os.path.exists(gladiator):
            return debugDir
            #return gladiator
def setServerShotFolder(gladiator, showCode, shotName):
    # scan gladiator and return the remote shot folder path that matches current local shot folder name
    serverShowFolder = None
    try:
        for folder in os.listdir(gladiator):
            # validate that it's a directory
            if os.path.isdir(os.path.join(gladiator, folder)):
                # check if ends with showCode
                if folder.split('_')[-1] == showCode:
                    serverShowFolder = os.path.join(gladiator, folder)
        serverShotFolder = os.path.join(os.path.join(serverShowFolder, '6.VFX'), shotName) + os.sep
        # found matching show folder, and returning supposed shot folder
        return serverShotFolder
    except:
        # no matching show folder found
        return None
def getLatestVersion(serverShotFolder, showCode):
    # get latest version on server
    latestVersion = 0
    for folder in os.listdir(serverShotFolder):
        pieces = folder.split('_v')
        if os.path.isdir(os.path.join(serverShotFolder, folder)):
            # one last small validation..
            if pieces[0].split('_')[0] == showCode and int(pieces[1]) > 0:
                versionNum = int(pieces[1])
                latestVersion = versionNum if versionNum > latestVersion else latestVersion
    return latestVersion
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

def getShotVersions(foundDirs):
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

#_C1 Tools______________________________________________________________________
def createShotFolder():
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

    data = {'found': str(results['foundDirs']), 'missing': results['missing'], 'versions': getShotVersions(results['foundDirs'])}
    print 'Found:' + '\n', data['found']
    print 'Missing C1 Subfolders:' + '\n', data['missing']
    print 'Versions:' + '\n', data['versions']

    return data

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
            # nuke.render(node, ranges)
            # node.knob('Render').execute()

            # node.knob('frame_range_string').setValue(string)

    # tempNode = nuke.createNode('Write')
    # nuke.render(tempNode, ranges)
            # return(nuke)
def versionUp(file):
    filepath = os.path.abspath(file)
    # filename pieces
    filename = os.path.basename(file).split('_v')
    currentVersion = int(os.path.basename(file).split('_v')[1].split('.')[0])

    versionFolder = os.path.abspath(os.path.join(filepath, os.pardir))
    shotFolder = os.path.dirname(versionFolder)

    newVersion = str(currentVersion + 1).zfill(3)
    newDir = os.path.join(shotFolder, filename[0] + '_v' + newVersion)
    newFileName = filename[0] + '_v' + newVersion + '_%V' + '.%04d.png'
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

def submitShot( file ):
    # define all the os paths to be used
    filepath = os.path.abspath(file)
    filename = os.path.basename(file).split('_v')
    showCode = filename[0].split('_')[0]
    versionFolder = os.path.abspath(os.path.join(filepath, os.pardir))
    localShotFolder = os.path.dirname(versionFolder)
    shotName = showCode + '_' + os.path.splitext(filename[0].split('_')[1])[0]
    try:
        # find Gladiator, define serverShotFolder, retrieve latestVersion
        gladiator = findGladiator()
        try:
            serverShotFolder = setServerShotFolder(gladiator, showCode, shotName)
            latestVersion = getLatestVersion(serverShotFolder, showCode)
            try:
                # try to convert current Nuke script's version to int
                currentVersion = int(os.path.basename(file).split('_v')[1].split('.')[0])
                try:
                    #_show modal window_________________________________________
                    dialogueText = nuke.Text_Knob( '','', 'Latest version of this shot on Gladiator is: ' + shotName + '_v' + str(latestVersion).zfill(3) + '.\n\nContinue submission as:' )
                    p = submitShotClass.submitShotDialogue( filepath, filename, currentVersion, latestVersion, versionFolder, localShotFolder, serverShotFolder, shotName, showCode, gladiator, dialogueText )
                    p.show( 'button1' )
                except:
                    raise
            except( IndexError ):
                dialogueText = nuke.Text_Knob( '','', 'Latest version of this shot on Gladiator is: ' + shotName + '_v' + str(latestVersion).zfill(3) + '.\n\nCurrent filename contains no version-number! Auto-version and continue submission as:' )
                currentVersion = latestVersion
                p = submitShotClass.submitShotDialogue( filepath, filename, currentVersion, latestVersion, versionFolder, localShotFolder, serverShotFolder, shotName, showCode, gladiator, dialogueText )
                p.show( 'button2' )
                #raise
            except( ValueError ):
                dialogueText = nuke.Text_Knob( '','', 'Latest version of this shot on Gladiator is: ' + shotName + '_v' + str(latestVersion).zfill(3) + '.\n\nSomething is wrong with your file version! Auto-version and continue submission as: ')
                currentVersion = latestVersion
                p = submitShotClass.submitShotDialogue( filepath, filename, currentVersion, latestVersion, versionFolder, localShotFolder, serverShotFolder, shotName, showCode, gladiator, dialogueText )
                p.show( 'button2' )
                #raise
        except:
            raise
            if not serverShotFolder:
                nuke.message( 'Unable to locate remote show folder which corresponds to current filename, possibly due to incorrect naming.\n\nCorrect naming:\nshowcode_shotname_vXXX\n\nRemote show folders are located at: ' + gladiator)
            else:
                nuke.message( 'Unable to find matching location on Gladiator for current shot. Please check that your local shot folders are named correctly and that a corresponding shot folder exists at:\n\n' + serverShotFolder)
    except:
        raise
        nuke.message( 'Unable to locate Gladiator at [drive]:\Departments\_Post\__Projects')

    return
