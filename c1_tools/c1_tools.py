import nuke
import nukescripts
#from nukescripts import panels
from PySide import QtGui
import os
import re
from string import ascii_lowercase
import shutil
import threading

import submitShot as submit

c1_folders = {
    '___CameraRaw': False,
    '__ProductionStitches': False,
    '_ImageSequences': False,
    'zFINAL': False
}

#_Utility Functions_____________________________________________________________

def findGladiator():
    debugDir = 'g' + ':' + os.sep + 'Users' + os.sep + 'Jacob' + os.sep
    laptopDir = 'e:' + os.sep + 'C1_LOCAL' + os.sep
    # for c in ascii_lowercase:
    #     gladiator = c + ':' + os.sep + 'Departments' + os.sep + '_Post' + os.sep + '__Projects' + os.sep
    #     if os.path.exists(gladiator):
    #         nuke.message('yo')
            #return gladiator
    return laptopDir


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

#_compile list of versions in directory(folders only)___________________________
def retrieveShotFolderVersions(foundDirs):
    if not foundDirs:
        return None
    versions = []
    for folder in foundDirs:
        if len(folder.split('_v')) > 1:
            version = int(folder.split('_v')[1])
            if version >= 1:
                versions.append(folder)
    if not versions:
        versions = None
    return versions

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

    data = {'found': str(results['foundDirs']), 'missing': results['missing'], 'versions': retrieveShotFolderVersions(results['foundDirs'])}
    print 'Found:' + '\n', data['found']
    print 'Missing C1 Subfolders:' + '\n', data['missing']
    print 'Versions:' + '\n', data['versions']
    return data

#_Scan for missing rener frames in write output directory_______________________
def Luis_Solver():
    node = nuke.toNode('_render')
    # if type(node) == type(nuke.root()):
    #     return nuke.message('Must have a write node selected!')

    file = node.knob('file').getValue()
    filepath = os.path.dirname(nuke.root().name()) + os.sep + 'Prerenders' + os.sep
    arr = []
    missing = []
    i = 0

    for img in os.listdir(filepath):
        n = int(img.split('.')[1])
        # n = int(re.search(r'\d+', img).group(0))
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
            nuke.render(node, ranges)
            # node.knob('Render').execute()

            # node.knob('frame_range_string').setValue(string)

    # tempNode = nuke.createNode('Write')
    # nuke.render(tempNode, ranges)
    return

def versionUp(file):
    filepath = os.path.abspath(file)
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
    return

def submitShot( filepath ):
    class Attr():
        def __init__( self, name=None, val=None ):
            if name:
                setattr( self, str(name), val )
            return
        def set( self, name, val ):
            setattr( self, str(name), val)
            return val
        def setAnd( self, name, val ):
            setattr( self, str(name), val)
            return self
    class Folder():
        def __init__( self ):
            self.path = Attr( 'remote', None )
            self.ver = Attr()
            return
        def set( self, name, val ):
            setattr( self, str(name), val)
            return val
        def setAnd( self, name, val ):
            setattr( self, str(name), val)
            return self
    class Submission():
        def __init__( self, filepath, gladiator ):
            self.gladiator = gladiator
            self.dialogueText = ''
            self.validated = False
            #_filename fragments
            self.filepath = os.path.abspath(filepath)
            self.filename = None
            self.showCode = None
            self.shotName = None
            self.fileversion = None
            #_folders
            self.versionFolder = Folder()
            self.shotFolder = Folder()
            self.showFolder = Folder()

            def validate():
                fragment1 = os.path.basename(filepath).split('_v')
                fragment2 = fragment1[0].split('_')
                fragmentsArr = []
                self.filename = fragment1[0]

                #_VALIDATE______________________________________________________
                exceptions = []

                try:
                    fileversion = int(fragment1[1].split('.')[0])
                    self.fileversion = fileversion
                except:
                    exceptions.append('--> Current filename contains no version-number!\n\nCorrect naming:\nshowcode_shotname_vXXX\n')
                if self.fileversion:
                    #_____showFolder, showCode, shotName
                    try:
                        if not self.showFolder.path.set( 'remote', retrieveServerShowFolder( fragment2[0]) ):
                            exceptions.append( '--> No corresponding Show folder found at: ' + self.gladiator + '\n\nCorrect naming:\nshowcode_shotname_vXXX\n')
                        else:
                            self.showCode = fragment2[0]
                            self.shotName = fragment1[0].split((self.showCode + '_'))[1].split('.')[0]
                    except:
                        exceptions.append('--> Problem retrieving Show directories. Now show found for: ' + str(fragment2[0]) + '\n' )
                if self.showFolder.path.remote:
                    #_____shotFolder
                    try:
                        if not self.shotFolder.path.set( 'remote', retrieveServerShotFolder(self.showFolder.path.remote, self.showCode, self.shotName) ):
                            exceptions.append('--> No corresponding Shot folder found for \'' + str( self.shotName ) + '\'\n')
                        else:
                            self.shotFolder.path.set( 'local', os.path.abspath(os.path.join(filepath, os.pardir)) )
                    except:
                        exceptions.append('--> Problem retrieving Shot directories. Now shot found for: \'' + str( self.shotName ) + '\'\n')
                if self.shotFolder.path.remote:
                    #_____versionFolder
                    try:
                        self.versionFolder.path.set( 'local', os.path.abspath(os.path.join(self.filepath, os.pardir)) )
                        latestVersion = retrieveLatestVersion(self.shotFolder.path.remote, self.showCode)
                        # nuke.message( self.shotFolder.path.remote )
                        self.versionFolder.path.set( 'remote', latestVersion['path'] )
                        self.versionFolder.ver.set( 'remote', latestVersion['int'] )
                    except:
                        exceptions.append('--> Problem setting the path or version for ' + self.shotFolder.path.remote + '.\n')
                    try:
                        ver = int(os.path.basename(self.versionFolder.path.local).split('_v')[1])
                        self.versionFolder.ver.set( 'local', ver )
                    except:
                        exceptions.append('--> The folder you\'r working out of doesn\'t have a valid version-number.\n\nCorrect naming:\nshowcode_shotname_vXXX\n' )
                #_exceptions____________________________________________________
                if len(exceptions) > 0:
                    msg = ''
                    i = 1
                    for exception in exceptions:
                        msg = msg + 'Exception ' + str(i) + ') ' + exception
                        i = i+1
                    nuke.message( msg )
                    return False
                else:
                    return True

            def retrieveServerShowFolder( showCode ):
                serverShowFolder = None
                for folder in os.listdir(self.gladiator):
                    # validate that it's a directory
                    if os.path.isdir(os.path.join(self.gladiator, folder)):
                        # check if ends with showCode
                        if folder.split('_')[-1] == showCode:
                            serverShowFolder = os.path.join(os.path.join(self.gladiator, folder), '6.VFX')
                return serverShowFolder

            def retrieveServerShotFolder( serverShowFolder, showCode, shotName ):
                serverShotFolder = None
                for folder in os.listdir(serverShowFolder):
                    # validate that it's a directory
                    if os.path.isdir(os.path.join(serverShowFolder, folder)):
                        # check if ends with showCode
                        if folder.split(showCode + '_')[-1] == shotName:
                            serverShotFolder = os.path.join(serverShowFolder, folder)
                return serverShotFolder

            def retrieveLatestVersion( directory, showCode ):
                # get latest version on server
                latestVersion = 0
                path = None
                for folder in os.listdir(directory):
                    pieces = folder.split('_v')
                    if os.path.isdir(os.path.join(directory, folder)):
                        # one last small validation..
                        if pieces[0].split('_')[0] == showCode and int(pieces[1]) > 0:
                            versionNum = int(pieces[1])
                            if versionNum > latestVersion:
                                latestVersion = versionNum
                                path = os.path.join(directory, folder )
                    # nuke.message(directory + '_' + str(os.path.abspath(folder)))
                return { 'int':latestVersion, 'path':path }

            if validate():
                self.validated = True
            #/init

    data = Submission(filepath, findGladiator())
    # nuke.message( data.versionFolder.path.remote )
    if not data.validated:
        # if validat() doesn't pass don't go any further
        return False
    elif data.versionFolder.ver.local <= data.versionFolder.ver.remote:
        # file's version already exists
        data.dialogueText = nuke.Text_Knob( '','', 'Latest version of this shot on Gladiator is: ' + data.shotName + '_v' + str(data.versionFolder.ver.remote).zfill(3) + '.\n\nYour file\'s version already exists! Continue submission as:' )
        data.fileversion = data.versionFolder.ver.remote + 1
        p = submit.submitShotDialogue( data )
        p.show( 'button1' )
    else:
        # save as current version
        if data.versionFolder.ver.remote == 0:
            data.dialogueText = nuke.Text_Knob( '','', 'This shot has no prior submissions.\n\nContinue as first submission:' )
        else:
            data.dialogueText = nuke.Text_Knob( '','', 'Latest version of this shot on Gladiator is: ' + data.shotName + '_v' + str(data.versionFolder.ver.remote).zfill(3) + '.\n\nContinue submission as:' )
        p = submit.submitShotDialogue( data )
        p.show( 'button2' )
    return
