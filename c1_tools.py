import nuke
import nukescripts
from nukescripts import panels
from PySide import QtGui
import os
import re

c1_folders = {
'___CameraRaw': False,
'__ProductionStitches': False,
'_ImageSequences': False,
'zFINAL': False
}

def scanDir(inputDir):
    #_flags_____________________________________________________________________
    #_data packages_____________________________________________________________
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

def setShotFolder():
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
    os.mkdir(newDir)

    # # make c1_folders
    for folder in c1_folders:
        os.mkdir(os.path.join(newDir, folder))

    #save nuke script
    nuke.scriptSaveAs(os.path.join(newDir, filename[0] + '_v' + newVersion + '.nk'))
