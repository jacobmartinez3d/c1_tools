import nuke
import nukescripts
from PySide import QtGui
import os
import re
from string import ascii_lowercase
import shutil
import threading
import smtplib
import c1_SubmitShot as submit

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
    for c in ascii_lowercase:
        gladiator = c + ':' + os.sep + 'Departments' + os.sep + '_Post' + os.sep + '__Projects' + os.sep
        if os.path.exists(gladiator):
            # nuke.message('yo')
            return gladiator
    return debugDir

def ffmpegRender():
    target = os.path.abspath( nuke.getFilename( 'Navigate to Prerenders folder, or any directory with L/R frames...' ) )
    arr = os.listdir( target )
    left = None
    right = None
    filename = None
    for thing in arr:
        while not left or not right:
            if len(thing.split('.png')) > 1:
                if len(thing.split('_L.')) > 1:
                    fragments = thing.split('_L.')
                    left = os.path.join( target, fragments[0] + '_L.%%04d.png' )
                    right = os.path.join( target, fragments[0] + '_R.%%04d.png' )
                    filename = fragments[0]
                elif len(thing.split('_left.')) > 1:
                    fragments = thing.split('_left.')
                    left = os.path.join( target, fragments[0] + '_left.%%04d.png' )
                    right = os.path.join( target, fragments[0] + '_right.%%04d.png' )
                    filename = fragments[0]
                elif len(thing.split('_l.')) > 1:
                    fragments = thing.split('_l.')
                    left = os.path.join( target, fragments[0] + '_l.%%04d.png' )
                    right = os.path.join( target, fragments[0] + '_r.%%04d.png' )
                    filename = fragments[0]
                elif len(thing.split('_Left.')) > 1:
                    fragments = thing.split('_Left.')
                    left = os.path.join( target, fragments[0] + '_Left.%%04d.png' )
                    right = os.path.join( target, fragments[0] + '_Right.%%04d.png' )
                    filename = fragments[0]
    if left and right:
        saveBatAs = os.path.join( os.path.join( target, os.pardir ), filename + '_OU.bat')
        output = os.path.join( os.path.join( target, os.pardir ), filename + '_360_3DV.mp4')
        fileObj = open( saveBatAs , 'wb')
        text = [
            'ffmpeg -i ',
            left,
            ' -i ',
            right,
            ' -filter_complex "[0:v]scale=iw:ih/2[top]; [1:v]scale=iw:ih/2[bottom]; [top][bottom]vstack[v]" -map "[v]" -c:v libx264 -crf 18 -pix_fmt yuv420p -coder 0 -refs 2 -x264opts b-pyramid=0 -g 29.97 -bf 0 -r 29.97 ',
            output]
        string = ''.join( text )
        fileObj.write( string )
        fileObj.close()
        os.system("start "+saveBatAs)

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

def createShotFolder( flag=None, shotFolder=None ):
    if flag is 'auto':
        shotFolder = shotFolder
    else:
        shotFolder = nuke.getFilename('Navigate to local Shot Folder...')
    parentFolder = os.path.abspath(os.path.join(shotFolder, os.pardir))

    if flag is not 'auto':
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
    if results['missing']:
        if flag is 'auto':
            for missingDir in results['missing']:
                os.mkdir(os.path.join(shotFolder, missingDir))
        else:
            # if missing C1 folders exist, ask user to create
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

def Luis_Solver():
    try:
        node = nuke.toNode('_render')
        file = node.knob('file').getValue()
        filepath = os.path.dirname(nuke.root().name()) + os.sep + 'Prerenders' + os.sep
        arr = []
        missing = []
        i = 0

        for img in os.listdir(filepath):
            nuke.message(str(re.findall('\d{0,4}[.](jpe?g|png|gif|bmp)/i', img)[0]).split('.')[0])
            n = int(str(re.findall('\d{0,4}\.(jpe?g|png|gif|bmp)$/i', img)[0]).split('.')[0])
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
    except:
        raise
        return nuke.message('Must have a write node named \'_render\' in your network!')
    return nuke.message( 'No Missing frame-ranges found!')

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

def retrieveLatestVersion( directory, showCode ):
    # get latest version on server
    latestVersion = 0
    path = None
    # nuke.message(directory)
    try:
        for folder in os.listdir(directory):
            # nuke.message(folder)
            if os.path.isdir(os.path.join(directory, folder)):
                pieces = folder.split('_v')
                # one last small validation..
                if pieces[0].split('_')[0] == showCode and int(pieces[1]) > 0:
                    versionNum = int(pieces[1])
                    if versionNum > latestVersion:
                        latestVersion = versionNum
                        path = os.path.join(directory, folder )
    except:
        print('c1_tools.retrieveLatestVersion(): Error processing something in' + str(directory) + '.')
            # nuke.message(directory + '_' + str(os.path.abspath(folder)))
    return { 'int':latestVersion, 'path':path }

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
                nukeScriptName = nuke.toNode('root').name()
                nukeScriptName = 'Untitled' if nukeScriptName == 'Root' else nukeScriptName
                fragment1 = os.path.basename(self.filepath).split('_v')
                fragment2 = fragment1[0].split('_')
                fragmentsArr = []
                self.filename = fragment1[0]

                #_VALIDATE______________________________________________________
                exceptions = []
                try:
                    fileversion = int(fragment1[1].split('.')[0])
                    self.fileversion = fileversion
                except:
                    exceptions.append('--> Current filename contains no version-number!\n\nCorrect naming:\nshowcode_shotname_vXXX\n\n')
                #_____showFolder, showCode, shotName
                try:
                    if not self.showFolder.path.set( 'remote', retrieveServerShowFolder( fragment2[0]) ):
                        exceptions.append( '--> No corresponding Show folder found at:\n' + self.gladiator + '\n\n')
                    else:
                        self.showCode = fragment2[0]
                        self.shotName = fragment1[0].split((self.showCode + '_'))[1].split('.')[0]
                except:
                    exceptions.append('--> Problem retrieving Show directories. No show found for:\n' + str(fragment2[0]) + '\n\n' )
                #_____shotFolder
                try:
                    if not self.shotFolder.path.set( 'remote', retrieveServerShotFolder(self.showFolder.path.remote, self.showCode, self.shotName) ):
                        exceptions.append('--> No corresponding Shot folder found for\n\'' + str( nukeScriptName ) + '\'\n\n')
                    else:
                        self.shotFolder.path.set( 'local', os.path.abspath(os.path.join(filepath, os.pardir)) )
                except:
                    exceptions.append('--> Problem retrieving Shot directories. No shot found for:\n\'' + str( nukeScriptName ) + '\'\n\n')
                #_____versionFolder
                try:
                    self.versionFolder.path.set( 'local', os.path.abspath(os.path.join(self.filepath, os.pardir)) )
                    latestVersion = retrieveLatestVersion(self.shotFolder.path.remote, self.showCode)
                    self.versionFolder.path.set( 'remote', latestVersion['path'] )
                    self.versionFolder.ver.set( 'remote', latestVersion['int'] )
                except:
                    exceptions.append('--> Problem setting the path or version for ' + nukeScriptName + '.\n\n')
                try:
                    ver = int(os.path.basename(self.versionFolder.path.local).split('_v')[1])
                    self.versionFolder.ver.set( 'local', ver )
                except:
                    exceptions.append('--> The folder you\'re working out of doesn\'t have a valid version-number.\n\n' )
                #_exceptions____________________________________________________
                if len(exceptions) > 0:
                    msg = ''
                    i = 1
                    for exception in exceptions:
                        msg = msg + 'Filenaming Error ' + str(i) + '):\n ' + exception
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
