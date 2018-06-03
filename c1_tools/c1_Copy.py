# Handles downloading and progress bar for shotBrowser _____________________________________________
import nuke
import sys
import os
import shutil
import threading
import subprocess
import c1_tools
sys.path.append('../init.py')

class Copy():
    def __init__( self, src, dst, data, includes=None ):
        from init import user as c1_user
        self.gladiator = data.gladiator
        self.user = c1_user
        self.filename = data.filename
        self.fileversion = data.fileversion
        self.shotName = data.shotName
        self.src= src
        self.dst = dst
        self.includes = includes
        # folders
        self.shotFolder = data.shotFolder
        self.shotFolder.path.set( 'local', os.path.join(dst, data.filename) )
        self.versionFolder = data.versionFolder
        self.versionFolder.path.set( 'local', os.path.join(self.shotFolder.path.local, data.filename + '_v' + str(self.fileversion).zfill(3)) )
        self.showFolder = data.showFolder
        self.acceptedFiles = {
            'nk': '.nk',
            '360_3DV.mp4': '_360_3DV.mp4',
            'mocha': '.moc',
            'ae': '.ae',
            'shotNotes': 'shotNotes.txt'
            }
        self.fileList = []
        self.exceptions = []
        self.task = nuke.ProgressTask("Downloading...")
        self.taskBuffer = 0
        return
    def copyfileobj(self, fsrc, fdst, length=16*1024):
        # copies source to destination, and updates Nuke's progress bar
        filesize = os.stat(fsrc)
        fsrcObj = open(fsrc, 'rb')
        fdstObj = open(fdst, 'wb')
        copied = 0
        while True:
            if self.task.isCancelled():
                break
            buf = fsrcObj.read(length)
            if not buf:
                break
            fdstObj.write(buf)
            copied += len(buf)
            self.updateTask(copied, filesize.st_size, os.path.basename(fsrc))
    def download( self ):
        # starts the shot downloading process
        def downloadThread():
            # 1) create localShotFolder
            try:
                localShotFolder = os.path.join(self.user.workingDir, self.filename)
                os.mkdir( localShotFolder )
                # 2) create subFolderStructure
                c1_tools.createShotFolder( 'auto', localShotFolder )
            except:
                nuke.executeInMainThread( nuke.message, args=( 'Shot-folder and version already exists locally!'))
                # split filename into 2 parts: name & version
                fragments = os.path.basename(self.versionFolder.path.local).split('_v')
                newVersionFolder = os.path.join(self.shotFolder.path.local, fragments[0] + '_v' + str(int(fragments[1])+1))
                self.versionFolder.path.set( 'local', newVersionFolder )
                del(self.task)
                return

            # 3) copy Production Stitches
            try:
                remote_productionStitches = os.path.join(self.shotFolder.path.remote, '__ProductionStitches')
                thingsToCopy = os.listdir(remote_productionStitches)
                local_productionStitches = os.path.join(self.shotFolder.path.local, '__ProductionStitches')
                for thing in thingsToCopy:
                    if len(thing.split( 'Pano-LR' )) > 1:
                        continue
                    if os.path.exists( os.path.join(local_productionStitches, thing) ):
                        continue
                    self.copyfileobj( os.path.join(remote_productionStitches, thing), os.path.join(local_productionStitches, thing) )
            except:
                nuke.executeInMainThread( nuke.message, args=( 'No \'__ProductionStitches\' folder found for this shot!'))
                del(self.task)

            # 5) version up & create new versionFolder
            newVersionFolder = os.path.join( self.shotFolder.path.local, self.filename + '_v' + str(self.fileversion + 1).zfill(3) )
            os.mkdir( newVersionFolder )
            self.versionFolder.path.set( 'local', newVersionFolder )
            if self.fileversion > 0:
                for thing in os.listdir( self.versionFolder.path.remote ):
                    for fragment in self.acceptedFiles:
                        if len(thing.split( fragment )) > 1:
                            target = os.path.join(self.versionFolder.path.remote, thing)
                            shutil.copyfile( target, os.path.join(newVersionFolder, self.filename + '_v' + str(self.fileversion + 1).zfill(3) + '.nk') )
            if self.includes:
                if self.includes['Prerenders']:
                    print('Copy Prerenders')
                elif self.includes['Raw']:
                    print('Copy Raw')
            else:
                os.mkdir( os.path.join(newVersionFolder, 'Prerenders') )
            del(self.task)
            return self.versionFolder.path.local
        return subprocess.Popen('explorer "%s"' % downloadThread())
    def updateTask( self, completed, total, msg ):
        self.task.setProgress( int((float(completed)/float(total))*100) )
        self.task.setMessage( msg )
