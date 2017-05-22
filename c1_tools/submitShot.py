import nuke
import nukescripts

class submitShotDialogue( nukescripts.PythonPanel ):
    def __init__( self ):
        nukescripts.PythonPanel.__init__( self, 'Submit Shot', )
        self.dialogueText = nuke.Text_Knob('','', 'Latest version of this shot on Gladiator is:\n\n' + shotName + '_v' + str(latestVersion).zfill(3) + '.\n\n')
        self.addKnob( self.dialogueText )
        self.button1 = nuke.PyScript_Knob("autoVersion", newVersionFolderName)
        self.addKnob( self.button1 )

    def submitShot(file):
        #_NOTES_____________________________________________________________________
        # -error when file not named
        # -currently creates folder on gladiator before user has chance to accept or not
        #___________________________________________________________________________
        filepath = os.path.abspath(file)
        filename = os.path.basename(file).split('_v')
        currentVersion = int(os.path.basename(file).split('_v')[1].split('.')[0])
        versionFolder = os.path.abspath(os.path.join(filepath, os.pardir))
        localShotFolder = os.path.dirname(versionFolder)
        shotName = os.path.basename(localShotFolder)
        showCode = filename[0].split('_')[0]

        gladiator = findGladiator()
        def setServerShotFolder(gladiator):
            # scan gladiator and return the remote shot folder path that matches current local shot folder name
            serverShowFolder = None

            for folder in os.listdir(gladiator):
                # validate that it's a directory
                if os.path.isdir(os.path.join(gladiator, folder)):
                    # check if ends with showCode
                    if folder.split('_')[-1] == showCode:
                        serverShowFolder = os.path.join(gladiator, folder)
            serverShotFolder = os.path.join(os.path.join(serverShowFolder, '6.VFX'), shotName) + os.sep
            return serverShotFolder
        serverShotFolder = setServerShotFolder(gladiator)
        # get latest version on server
        latestVersion = 0
        for folder in os.listdir(serverShotFolder):
            pieces = folder.split('_v')
            if os.path.isdir(os.path.join(serverShotFolder, folder)):
                # one last small validation..
                if pieces[0].split('_')[0] == showCode and int(pieces[1]) > 0:
                    versionNum = int(pieces[1])
                    latestVersion = versionNum if versionNum > latestVersion else latestVersion

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
