import nuke
import sys
import os
import shutil
import threading
import c1_tools
sys.path.append('../init.py')
from init import user as c1_user

class Copy():
    def __init__( self, src, dst, data, includes=None ):
        self.gladiator = data.gladiator
        self.user = c1_user
        self.filename = data.filename
        self.fileversion = data.fileversion
        self.shotName = data.shotName
        self.src= src
        self.dst = dst
        self.includes = includes
        #_folders_
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
        return
    def copyPaste( self, src, dst ):
        fsrc = open(src, 'rb').read()
        with open(dst, 'wb') as fdst:
            fdst.write(fsrc)
        return
    def download( self ):
        def downloadThread():
            task = nuke.ProgressTask("Downloading...")
            # 1) create localShotFolder
            try:
                localShotFolder = os.path.join(self.user.workingDir, self.filename)
                os.mkdir( localShotFolder )
                # 2) create subFolderStructure
                c1_tools.createShotFolder( 'auto', localShotFolder )
            except:
                raise
                print('exception occured')
            # 4) copy() selected items + Production Stitches
            try:
                # set up task variables---------------------------------------------
                remote_productionStitches = os.path.join(self.shotFolder.path.remote, '__ProductionStitches')
                thingsToCopy = os.listdir(remote_productionStitches)
                progIncr = 100.0 / len(thingsToCopy)
                i = 0
                if task.isCancelled():
                    nuke.executeInMainThread( nuke.message, args=( "Aborted!" ) )
                #-------------------------------------------------------------------
                local_productionStitches = os.path.join(self.shotFolder.path.local, '__ProductionStitches')
                for thing in thingsToCopy:
                    task.setProgress(int(i * progIncr))
                    task.setMessage(thing)
                    if os.path.exists( os.path.join(local_productionStitches, thing) ):
                        continue
                    shutil.copyfile( os.path.join(remote_productionStitches, thing), os.path.join(local_productionStitches, thing) )
                    i = i + 1
            except:
                raise
                print('exception occured')
            # 5) version up & create new versionFolder
            newVersionFolder = os.path.join( self.shotFolder.path.local, self.filename + '_v' + str(self.fileversion + 1).zfill(3) )
            os.mkdir( newVersionFolder )
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
        # nuke.message( self.versionFolder.path.local)
        # threading.Thread( target = downloadThread ).start()
        downloadThread()
        return
