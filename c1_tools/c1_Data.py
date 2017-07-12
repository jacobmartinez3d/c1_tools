import nuke
import os
import c1_tools


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
class Data():
    def __init__( self, type, filepath, gladiator ):
        self.gladiator = gladiator
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
            #-upload------------------------------------------------------------
            if type == 'upload':
                nukeScriptName = nuke.toNode('root').name()
                nukeScriptName = 'Untitled' if nukeScriptName == 'Root' else nukeScriptName
                # elif type = 'download':
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
                    exceptions.append('--> Problem retrieving Show directories. Now show found for:\n' + str(fragment2[0]) + '\n\n' )
                #_____shotFolder
                try:
                    if not self.shotFolder.path.set( 'remote', retrieveServerShotFolder(self.showFolder.path.remote, self.showCode, self.shotName) ):
                        exceptions.append('--> No corresponding Shot folder found for\n\'' + str( nukeScriptName ) + '\'\n\n')
                    else:
                        self.shotFolder.path.set( 'local', os.path.abspath(os.path.join(filepath, os.pardir)) )
                except:
                    exceptions.append('--> Problem retrieving Shot directories. Now shot found for:\n\'' + str( nukeScriptName ) + '\'\n\n')
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
                    exceptions.append('--> The folder you\'r working out of doesn\'t have a valid version-number.\n\n' )
            #-download----------------------------------------------------------
            elif type == 'download':
                fragment1 = os.path.basename(self.filepath).split('_v')
                fragment2 = fragment1[0].split('_')
                fragmentsArr = []
                self.filename = fragment1[0]
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
                    exceptions.append('--> Problem retrieving Show directories. Now show found for:\n' + str(fragment2[0]) + '\n\n' )
                #_____shotFolder
                try:
                    if not self.shotFolder.path.set( 'remote', retrieveServerShotFolder(self.showFolder.path.remote, self.showCode, self.shotName) ):
                        exceptions.append('--> No corresponding Shot folder found for\n\'' + str( nukeScriptName ) + '\'\n\n')
                    else:
                        self.shotFolder.path.set( 'local', os.path.abspath(os.path.join(filepath, os.pardir)) )
                except:
                    exceptions.append('--> Problem retrieving Shot directories. Now shot found for:\n\'' + str( nukeScriptName ) + '\'\n\n')
                #_____versionFolder
                try:
                    # self.versionFolder.path.set( 'local', os.path.abspath(os.path.join(self.filepath, os.pardir)) )
                    latestVersion = c1_tools.retrieveLatestVersion(self.shotFolder.path.remote, self.showCode)
                    self.versionFolder.path.set( 'remote', latestVersion['path'] )
                    self.versionFolder.ver.set( 'remote', latestVersion['int'] )
                except:
                    raise
                    exceptions.append('--> Problem setting the path or version for ' + fragment1[0] + '.\n\n')
                # try:
                #     ver = int(os.path.basename(self.versionFolder.path.local).split('_v')[1])
                #     # self.versionFolder.ver.set( 'local', ver )
                # except:
                #     exceptions.append('--> The folder you\'r working out of doesn\'t have a valid version-number.\n\n' )


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
