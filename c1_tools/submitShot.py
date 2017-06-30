import nuke
import nukescripts
import os
import shutil
import threading


class submitShotDialogue( nukescripts.PythonPanel ):
    def __init__( self, data ):
        nukescripts.PythonPanel.__init__( self, 'Submit Shot')
        self.gladiator = data.gladiator
        #filename fragments
        self.filepath = data.filepath
        self.filename = data.filename
        self.showCode = data.showCode
        self.shotName = data.shotName
        self.versionNum = data.versionNum
        #local
        self.localShotFolder = data.localShotFolder
        self.localVersionFolder = data.localVersionFolder
        #server
        self.serverShowFolder = data.serverShowFolder
        self.serverShotFolder = data.serverShotFolder
        self.serverVersionFolder = data.serverVersionFolder
        self.serverLatestVersion = data.serverLatestVersion

        #_knobs_________________________________________________________________
        self.dialogueText = data.dialogueText
        self.addKnob( self.dialogueText )
        self.cancelButton = nuke.PyScript_Knob("Cancel")
        self.button1 = nuke.PyScript_Knob( "autoVersion", self.shotName + '_v' + str( self.serverLatestVersion + 1).zfill(3) )
        self.button2 = nuke.PyScript_Knob( "currentVersion", self.shotName + '_v' + str( self.versionNum).zfill(3) )


    def show ( self, button ):
        if button == 'button1':
            self.addKnob( self.button1 )
            self.addKnob( self.cancelButton )
            nukescripts.PythonPanel.showModal( self )
        elif button == 'button2':
            self.setMinimumSize(550, 100)
            self.addKnob( self.button2 )
            self.addKnob( self.cancelButton )
            nukescripts.PythonPanel.showModal( self )

    def knobChanged(self, knob):
        if knob.name() == 'autoVersion':
            self.submitShot('autoVersion')
            self.ok()
        elif knob.name() == 'currentVersion':
            self.submitShot('currentVersion')
            self.ok()

    def submitShot( self, userChoice ):
        #_NOTES_________________________________________________________________
        # -currently creates folder on gladiator before user has chance to accept or not
        #_______________________________________________________________________

        def createNewRemoteVersion(serverShotFolder, latestVersion):
            if userChoice == 'autoVersion':
                newVersionFolderName = self.shotName + '_v' + str(self.serverLatestVersion + 1).zfill(3)
            elif userChoice == 'currentVersion':
                newVersionFolderName = self.shotName + '_v' + str(self.versionNum).zfill(3)

            # newVersionFolderPath = os.path.join(serverShotFolder, newVersionFolderName)
            localPrerenders = os.path.join(self.localVersionFolder, 'Prerenders')
            remotePrerenders = os.path.join(self.serverVersionFolder, 'Prerenders')
            nuke.message(localPrerenders + '_' + remotePrerenders)
            if len(os.listdir(localPrerenders)) < 2:
                nuke.message('Your Prerenders folder has less than 2 files in it. Please check and re-submit!')
                return

            # create folders/files on Gladiator...
            os.mkdir(self.serverVersionFolder)
            # do little dance to save to remote dir, then revert back to previous local session
            currentScript = nuke.toNode('root').name()
            nuke.scriptSaveAs(os.path.join(self.serverVersionFolder, os.path.basename(self.serverVersionFolder) + '.nk'))
            nuke.toNode('root').knob('name').setValue(currentScript)
            os.mkdir(remotePrerenders)

            def copyPrerenders():
                #_NOTES_________________________________________________________
                # 1. need to add auto-renaming if auto-versioning is used
                # 2. add the 360_3DV.mp4 to the copy operation
                # 3. after aborting, need to delete the files
                #_______________________________________________________________

                task = nuke.ProgressTask("Submitting...")
                #need to change
                versionFiles = os.listdir(self.serverVersionFolder)
                #filter out unaccepted files
                arr = versionFiles
                for item in versionFiles:
                    if os.path.isdir(item):
                        print(item)
                    # nuke.executeInMainThread( nuke.message, args=( str(item) ) )
                frames = os.listdir(localPrerenders)

                #need to un-include files not to be copied
                progIncr = 100.0 / len(frames)

                for i, f in enumerate(frames):
                    if task.isCancelled():
                        nuke.executeInMainThread( nuke.message, args=( "Aborted!" ) )
                        #_delete files after subission__________________________
                        #def cancelSubmission():
                            #use os module
                        #nuke.executeInMainThread( cancelSubmission, args=( newVersionFolderPath ) )
                        #_______________________________________________________
                        return;
                    task.setProgress(int(i * progIncr))
                    task.setMessage(f)

                    acceptedFiles = {
                        'Prerenders': 'Prerenders',
                        '360_3DV.mp4': '_360_3DV.mp4',
                        'mocha': '.moc',
                        'ae': '.ae',
                        'shotNotes': 'shotNotes.txt'
                        }
                    for item in acceptedFiles:
                        # nuke.executeInMainThread( nuke.message, args=( item ) )
                        if item == 'prerenders':
                            copyFrom = os.path.join(localPrerenders, f)
                            copyTo = os.path.join(remotePrerenders, f)
                            # shutil.copyfile(copyFrom, copyTo)
                        elif item == '360_3DV.mp4':
                            copyFrom = os.path.join(self.localVersionFolder, (self.filename + '_v' + str(self.versionNum).zfill(3) + '_360_3DV.mp4'))
                            copyTo = os.path.join(os.path.join(self.serverShotFolder, (self.filename + '_v' + str(self.serverLatestVersion + 1).zfill(3))), (self.filename + '_360_3DV.mp4'))
                            shutil.copyfile(copyFrom, copyTo)

                    # shutil.copyfile(copyFrom, copyTo)
                nuke.executeInMainThread(nuke.message, args=('Shot succsessfully submitted to Gladiator as: ' + newVersionFolderName + '.\n\nGood work! ;p'))

            threading.Thread( target = copyPrerenders ).start()
        createNewRemoteVersion(self.serverShotFolder, self.serverLatestVersion)
