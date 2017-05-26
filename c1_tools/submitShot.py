import nuke
import nukescripts
import os
import shutil
import threading

class submitShotDialogue( nukescripts.PythonPanel ):
    def __init__( self, filepath, filename, currentVersion, latestVersion, versionFolder, localShotFolder, serverShotFolder, shotName, showCode, gladiator, dialogueText ):
        nukescripts.PythonPanel.__init__( self, 'Submit Shot')

        #_properties____________________________________________________________
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
        #_knobs_________________________________________________________________
        self.dialogueText = dialogueText
        self.addKnob( self.dialogueText )
        self.cancelButton = nuke.PyScript_Knob("Cancel")
        self.button1 = nuke.PyScript_Knob( "currentVersion", shotName + '_v' + str( self.currentVersion).zfill(3) )
        self.button2 = nuke.PyScript_Knob( "autoVersion", shotName + '_v' + str( self.latestVersion + 1).zfill(3) )

    def knobChanged(self, knob):
        if knob.name() == 'autoVersion':
            self.submitShot('autoVersion')
        elif knob.name() == 'currentVersion':
            nuke.message('Current Version')

    def submitShot( self, userChoice ):
        #_NOTES_________________________________________________________________
        # -error when file not named
        # -currently creates folder on gladiator before user has chance to accept or not
        #_______________________________________________________________________

        def createNewRemoteVersion(serverShotFolder, latestVersion):
            newVersionFolderName = self.shotName + '_v' + str(self.latestVersion + 1).zfill(3)
            newVersionFolderPath = os.path.join(serverShotFolder, newVersionFolderName)

            localPrerenders = os.path.join(self.versionFolder, 'Prerenders')
            remotePrerenders = os.path.join(newVersionFolderPath, 'Prerenders')

            try:
                if len(os.listdir(localPrerenders)) < 2:
                    nuke.message('Your Prerenders folder has less than 2 files in it. Please check and re-submit!')
                    return

                # create folders/files on Gladiator...
                os.mkdir(newVersionFolderPath)
            except( WindowsError ):
                nuke.message('No Prerenders folder found!')
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

        createNewRemoteVersion(self.serverShotFolder, self.latestVersion)

    def show ( self, button ):
        if button == 'button1':
            self.addKnob( self.button1 )
        elif button == 'button2':
            self.setMinimumSize(550, 100)
            self.addKnob( self.button2 )
        self.addKnob( self.cancelButton )
        nukescripts.PythonPanel.showModal( self )
