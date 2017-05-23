import nuke
import nukescripts

class submitShotDialogue( nukescripts.PythonPanel ):
    def __init__( self, filepath, filename, currentVersion, latestVersion, versionFolder, localShotFolder, serverShotFolder, shotName, showCode, gladiator ):
        nukescripts.PythonPanel.__init__( self, 'Submit Shot' )
        self.dialogueText = nuke.Text_Knob( '','', 'Latest version of this shot on Gladiator is:\n\n' + shotName + '_v' + str(latestVersion).zfill(3) + '.\n\n' )
        self.addKnob( self.dialogueText )
        self.button1 = nuke.PyScript_Knob( "autoVersion", newVersionFolderName )
        self.addKnob( self.button1 )

        self.filepath = filepath
        self.filename = filename
        self.currentVersion = currentVersion
        self.versionFolder = versionFolder
        self.localShotFolder = localShotFolder
        self.shotName = shotName
        self.showCode = showCode
        self.gladiator = gladiator
        self.serverShotFolder = serverShotFolder
        self.latestVersion = latestVersion

    def submitShot(file):
        #_NOTES_____________________________________________________________________
        # -error when file not named
        # -currently creates folder on gladiator before user has chance to accept or not
        #___________________________________________________________________________

        def createNewRemoteVersion(serverShotFolder, latestVersion):
            newVersionFolderName = shotName + '_v' + str(latestVersion + 1).zfill(3)
            newVersionFolderPath = os.path.join(serverShotFolder, newVersionFolderName)

            localPrerenders = os.path.join(versionFolder, 'Prerenders')
            remotePrerenders = os.path.join(newVersionFolderPath, 'Prerenders')

            if len(os.listdir(localPrerenders)) < 2:
                nuke.message('Your Prerenders folder has less than 2 files in it. Please check and re-submit!')
                return

            # create folders/files on Gladiator...
            os.mkdir(newVersionFolderPath)
            # do little dance to save to remote dir, then revert back to previous local session
            currentScript = nuke.toNode('root').name()
            nuke.scriptSaveAs(os.path.join(newVersionFolderPath, newVersionFolderName + '.nk'))
            nuke.toNode('root').knob('name').setValue(currentScript)
            os.mkdir(remotePrerenders)

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

        createNewRemoteVersion(serverShotFolder, latestVersion)

    def showModalDialogue ( self ):
        nukescripts.PythonPanel.showModalDialog( self )
