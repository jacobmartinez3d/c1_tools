import nuke
import nukescripts
try:
    import PySide.QtGui as QtGui
except:
    import PySide2.QtGui as QtGui
import os
import re
from string import ascii_lowercase
import shutil
import threading
import smtplib
import c1_SubmitShot as submit
nuke.pluginAddPath('C:\Users\Jacob\.nuke\OpenTimelineIO-master')
import opentimelineio as otio

for clip in timeline.each_clip():
  print clip.media_reference

c1_folders = {
    '___CameraRaw': False,
    '__ProductionStitches': False,
    '_vrweb_Assets': False,
    'zFINAL': False
    }

#_Utility Functions_____________________________________________________________
def findGladiator():
    debugDir = 'g' + ':' + os.sep + 'Users' + os.sep + 'Jacob' + os.sep
    laptopDir = 'e:' + os.sep + 'C1_LOCAL' + os.sep
    for c in ascii_lowercase:
        gladiator = c + ':' + os.sep + 'Departments' + os.sep + '_Post' + os.sep + '__Projects' + os.sep
        # if os.path.exists(gladiator):
            # nuke.message('Gladiator found at: ' + gladiator)
            # return gladiator
    return laptopDir

def writeToRead():
    selectedNodes = nuke.selectedNodes()
    writeNodes = []
    connectNodes = []
    if selectedNodes:
        for node in selectedNodes:
            if node.Class() == 'Write':
                writeNodes.append(node)
            else:
                connectNodes.append(node)
        if len(writeNodes) > 0:
            flag = True if len(writeNodes) == len(connectNodes) else False
            frameRange = ()
            # if multiple write nodes are selected...
            for i in range(len(writeNodes)):
                fileLoc = writeNodes[i].knob('file').getValue()
                filename = os.path.basename(fileLoc).split('.')[0]
                framesArr = os.listdir(os.path.join(fileLoc, os.pardir))
                # need to comb out anything that doesnt name-match
                for i in range(len(framesArr)):
                    if len(framesArr[i].split(filename)) == 0:
                        del framesArr[i]
                n = nuke.nodes.Read(file=fileLoc)
                n.knob('first').setValue(int(framesArr[0].split('.')[1]))
                n.knob('last').setValue(int(framesArr[-1].split('.')[1]))
                if flag == True:
                    # create @ connectNodes locs
                    n.setName('from_' + writeNodes[i].name())
                    n.setXYpos(connectNodes[i].xpos(), connectNodes[i].ypos() - (connectNodes[i].height()/100)*5)
                    connectNodes[i].setInput(0, n)
                else:
                    # create @ write node locs
                    print(i)
                    n.setName('from_' + writeNodes[i].name())
                    n.setXYpos(writeNodes[i].xpos() + (writeNodes[i].width()/100)*2, writeNodes[i].ypos())
    return

def proresToMp4():
    target = os.path.abspath( nuke.getFilename('Select .mov.') )
    output = os.path.abspath( nuke.getFilename('Select output file destination.') )
    text = ['ffmpeg -i ', target, ' -c:v libx264 -crf 20 -pix_fmt yuv420p -coder 0 -refs 2 -x264opts b-pyramid=0 -g 29.97 -bf 0 -r 29.97 ', output + '.mp4']
    string = ''.join(text)
    saveBatAs = os.path.splitext(output)[0] + '.bat'
    fileObj = open( saveBatAs , 'wb')
    fileObj.write( string )
    fileObj.close()
    os.system("start "+saveBatAs)
    return

def titles_qc():
    def validateFrames(type):
        missing = {}
        frameNum = None
        arr = []                   
        i = 0
        # validate 'mono/' directory frames...
        for thing in sorted(os.listdir(os.path.join(titlesFolder_dct[folder], type))):
            #print("attempting to match: " + thing)           
            validated_frame = re_framePattern.match(thing)
            
            if validated_frame:
                titleName = os.path.basename(titlesFolder_dct[folder]) + "_" + validated_frame.group(1)
                print("'" + validated_frame.string + "\' successfully validated!")
                n = int(validated_frame.group(2))
                arr.append(n)
                if len(arr) > 1:
                    
                    difference = arr[i] - arr[i-1]
                    if difference > 1:                                  
                        for n in range(difference):
                            if titleName in missing:
                                missing[titleName].append(arr[i-1]+n)
                            else:
                                missing[titleName] = [(arr[i-1]+n)]   
                i+=1
            else:
                print("'" + thing + "\' is not named correctly!")
        #results = {"missingFrames": missing}
        return missing

    def writeSummary(type, data):
        result = ""
        if type == 'missingFrames':
            for folderObject in data:
                result += str(folderObject) + "\n"
                print(str(folderObject))
        # elif type == 'fileList':
            # for file in data:
                
        return result
        
    # def writeFileList(data):
        
        
    #_PRECHECKS_________________________________________________________________________________________________________
    titleName = ".{1,}"
    re_framePattern = re.compile(titleName + "_(?i)(left|l|right|r|mono|m)\.(\d{1,})\.(fbx|png|tiff?|dpx)")
    # group 1: left|right|mono
    # group 2: frame number
    # group 3: file ext
    re_folderPattern = re.compile('(^\d{1,})_')
    # group 1: folder number
    titles_directory = os.path.abspath( nuke.getFilename( 'Navigate to any directory with properly-named frames...' ) )
    titlesFolder_dct = {}
    # validate 'Titles' folder...
    for thing in os.listdir(titles_directory):
        validated_folder = re_folderPattern.match(thing)
        if validated_folder:
            titlesFolder_dct[int(validated_folder.group(1))] = os.path.join(titles_directory, validated_folder.string)
            print("'" + validated_folder.string + "\' validated!")
    titlesFolder_dct = dict(sorted(titlesFolder_dct.items()))
    
    if len(titlesFolder_dct) > 0:
        summary = ""
        fileList = ""
    #___________________________________________________________________________________________________________________
        missingFrames = []
        for folder in titlesFolder_dct:
            try:
                if os.path.isdir(os.path.join(titlesFolder_dct[folder], 'mono')):
                    results = validateFrames('mono')
                    if results:
                        missingFrames.append(results)                                   
                    summary += ('\n' + os.path.basename(titlesFolder_dct[folder]) + " MONO: FOUND.")
                    fileList = "file '"
                    continue
                if os.path.isdir(os.path.join(titlesFolder_dct[folder], 'left')):
                    results = validateFrames('left')
                    if results:
                        missingFrames.append(results)
                    summary += ('\n' + os.path.basename(titlesFolder_dct[folder]) + " left: FOUND.")
                else:
                    summary += ('\n' + os.path.basename(titlesFolder_dct[folder]) + " left: MISSING")
                if os.path.isdir(os.path.join(titlesFolder_dct[folder], 'right')):
                    results = validateFrames('right')
                    if results:
                        missingFrames.append(results)
                    summary += ('\n' + os.path.basename(titlesFolder_dct[folder]) + " right: FOUND.")
                else:
                    summary += ('\n' + os.path.basename(titlesFolder_dct[folder]) + " right: MISSING")                               
            except:
                raise             
                nuke.message(os.path.basename(titlesFolder_dct[folder]) + " is missing 'left' and 'right', or 'mono' subdirectories!")

        
        
        print(missingFrames)
        concatList = open(os.path.join(titles_directory, 'concatList.txt'), 'w')
        concatList.write(summary + "\n")
        concatList.write(writeSummary('missingFrames', missingFrames))
        # Now I need the actual concat code...        

        concatList.close()
        # print(os.path.join(titles_directory, 'concatList.txt'))
        # print("Missing frames detected! @: " + str(missing))
        #print(summary)

    # Next steps:
    # -create a concat.txt list and save to titles dir
    # -need to handle missing folders and misnamed frames before continuing, possibly giving user option to skip those folders

def ffmpegRender(titles=False):
    try:
        filepath = os.path.dirname(nuke.root().name()) + os.sep + 'Prerenders' + os.sep
        prerenders = filepath
        arr = os.listdir( prerenders )
    except:
        prerenders = os.path.abspath( nuke.getFilename( 'Navigate to any directory with properly-named frames...' ) )
        arr = os.listdir( prerenders )
    inputStream_left = None
    inputStream_right = None
    inputStream_main = None
    shotName = None
    re_pattern = "^(\w{3}).{1}(.*).{1}v(\d{1,}).{1}(left|right|main|mono)\.(\d{3,})(\.fbx|\.png|\.tiff?|\.dpx)"
    re_c1_frame = re.compile(re_pattern)
    for thing in arr:
        #___________________________________________________________________________________________
        match = re_c1_frame.search(thing)
        # Results will be:
        # 0: entire string
        # 1: showCode
        # 2: shotName
        # 3: versionNum
        # 4: eye (left/right)
        # 5: frameNum
        # 6: ext
        #___________________________________________________________________________________________
        # check file-extension (\.fbx|\.png|\.tiff?|\.dpx)
        if match.group(6) and match.group(4):
            shotName = match.group(1) + '_' + match.group(2) + '_v' + match.group(3)
            # check if left/right found
            if match.group(4) == 'left':
                inputStream_left = os.path.join( prerenders, shotName + '_' + match.group(4) + '.%%04d.png' )
            elif match.group(4) == 'right':
                inputStream_right = os.path.join( prerenders, shotName + '_' + match.group(4) + '.%%04d.png' )
            # no 'left'/'right' found so it must be 'main' or 'mono'
            else:
                inputStream_main = os.path.join( prerenders, shotName + '_' + match.group(4) + '.%%04d.png' )
    if inputStream_left and inputStream_right:
        saveBatAs = os.path.join( prerenders, os.pardir, shotName + '_OU.bat')
        output = os.path.join( prerenders, os.pardir, shotName + '_360_3DV.mp4')
        fileObj = open( saveBatAs , 'wb')
        text = [
            'ffmpeg -i ',
            inputStream_left,
            ' -i ',
            inputStream_right,
            ' -filter_complex "[0:v]scale=iw:ih/2[top]; [1:v]scale=iw:ih/2[bottom]; [top][bottom]vstack[v]" -map "[v]" -c:v libx264 -b:v 20m -minrate 20m -maxrate 20m -bufsize 40m -pix_fmt yuv420p -coder 0 -refs 2 -x264opts b-pyramid=0 -g 29.97 -bf 0 -r 29.97 ',
            output]
        string = ''.join( text )
        fileObj.write( string )
        fileObj.close()
        os.system("start "+saveBatAs)
    elif inputStream_main:
        saveBatAs = os.path.join( prerenders, os.pardir, shotName + '_OU.bat')
        output = os.path.join( prerenders, os.pardir, shotName + '_360.mp4')
        fileObj = open( saveBatAs , 'wb')
        text = [
            'ffmpeg -i ',
            inputStream_main,
            ' -c:v libx264 -crf 18 -pix_fmt yuv420p -coder 0 -refs 2 -c:v libx264 -b:v 20m -minrate 20m -maxrate 20m -bufsize 40m b-pyramid=0 -g 29.97 -bf 0 -r 29.97 ',
            output]
        string = ''.join( text )
        fileObj.write( string )
        fileObj.close()
        os.system("start "+saveBatAs)
    return

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
    except:
        raise
        return nuke.message('Must have a write node named \'_render\' in your network!')
    # if type(node) == type(nuke.root()):
    #     return nuke.message('Must have a write node selected!')

            # node.knob('Render').execute()

            # node.knob('frame_range_string').setValue(string)

    # tempNode = nuke.createNode('Write')
    # nuke.render(tempNode, ranges)
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
    try:
        for folder in os.listdir(directory):
            if os.path.isdir(os.path.join(directory, folder)):
                # pieces = os.path.basename(folder).split('_v')
                pieces = os.path.basename(folder).split('_v')
                # one last small validation..
                if pieces[0].split('_')[0] == showCode and int(pieces[1]) > 0:
                    versionNum = int(pieces[1])
                    if versionNum > latestVersion:
                        latestVersion = versionNum
                        path = os.path.join(directory, folder )
    except:
        print('c1_tools.retrieveLatestVersion(): Error processing something in' + str(directory) + '.')
        # nuke.message('c1_tools.retrieveLatestVersion(): Error processing something in' + str(directory) + '.')
        # nuke.message(directory + '_' + str(os.path.abspath(folder)))
    data = { 'int':latestVersion, 'path':path }
    return data

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

def c1_timeline( filepath ):
    timeline = otio.adapters.read_from_file(filepath)
    for clip in timeline.each_clip():
    print clip.media_reference
