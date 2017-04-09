import nuke
import nukescripts
from nukescripts import panels
from PySide import QtGui
import os

def getShotVersions(foundDirs):
    versions = []
    for folder in foundDirs:
        if len(folder.split('_v')) > 1:
            version = int(folder.split('_v')[1])
            if not version < 1:
                versions.append(folder)
    if not versions:
        versions = None
    return versions

def setShotFolder():
    shotFolder = nuke.getFilename('Navigate to local Shot Folder...')
    if os.path.isdir(shotFolder):
        shot = shotFolder.split('/')[-2]
    else:
        nuke.message('You must choose a folder or directory!')
        return

    #_flags_____________________________________________________________________
    # c1_folders = {
    #     'cameraRaw': False,
    #     'productionStitches': False,
    #     'imageSequences': False,
    #     'zFinal': False
    # }
    cameraRaw = False
    productionStitches = False
    imageSequences = False
    zFinal = False
    #_flags_____________________________________________________________________
    foundDirs = []
    missingDirs = []

    for thing in os.listdir(shotFolder):
        # check if its a folder or not...
        if os.path.isdir(os.path.join(shotFolder, thing)):
            foundDirs.append(thing)
    if not foundDirs:
        foundDirs = None

    # Validate...
    for folder in foundDirs:
        # set validation flags...
        if folder == '___CameraRaw':
            cameraRaw = True
        if folder == '__ProductionStitches':
            productionStitches = True
        if folder == '_ImageSequences':
            imageSequences = True
        if folder == 'zFINAL':
            zFinal = True

    # then append missing folders to list
    if cameraRaw == False:
        missingDirs.append('___CameraRaw')
    if productionStitches == False:
        missingDirs.append('__ProductionStitches')
    if imageSequences == False:
        missingDirs.append('_ImageSequences')
    if zFinal == False:
        missingDirs.append('zFINAL')

    # if missing dirs exist, ask user to create
    if missingDirs:
        if nuke.ask('The following folders are missing: ' + '\n' + str(missingDirs)[1:-1] + ', create them now?'):
            for missingDir in missingDirs:
                os.mkdir(os.path.join(shotFolder, missingDir))
    else:
        missingDirs = None

    data = {'found': str(foundDirs)[1:-1], 'missing': missingDirs, 'versions': getShotVersions(foundDirs)}

    print 'Found:' + '\n', data['found']
    print 'Missing Subfolders:' + '\n', data['missing']
    print 'Versions:' + '\n', data['versions']

    return data

def openShotBrowser():
    p = nuke.Panel('C1 Shot Browser')
    p.show()
