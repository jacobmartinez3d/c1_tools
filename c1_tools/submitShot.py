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
        print('got to line 51')

        def createNewRemoteVersion(serverShotFolder, latestVersion):
            print('got to line 53')
            if userChoice == 'autoVersion':
                newVersionFolderName = self.shotName + '_v' + str(self.latestVersion + 1).zfill(3)
            elif userChoice == 'currentVersion':
                newVersionFolderName = self.shotName + '_v' + str(self.currentVersion).zfill(3)

            newVersionFolderPath = os.path.join(serverShotFolder, newVersionFolderName)
            localPrerenders = os.path.join(self.versionFolder, 'Prerenders')
            remotePrerenders = os.path.join(newVersionFolderPath, 'Prerenders')
            print('got to line 61')
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
                #_NOTES_________________________________________________________
                # 1. need to add auto-renaming if auto-versioning is used
                # 2. add the 360_3DV.mp4 to the copy operation
                # 3. after aborting, need to delete the files
                #_______________________________________________________________
                print('got here')
                task = nuke.ProgressTask("Submitting...")
                #need to change
                versionFiles = os.listdir(self.versionFolder)
                #filter out unaccepted files
                arr = versionFiles
                for item in versionFiles:
                    if os.path.isdir(item):
                        print(item)
                    # nuke.executeInMainThread( nuke.message, args=( str(item) ) )
                prerenderFrames = os.listdir(localPrerenders)

                #need to un-include files not to be copied
                progIncr = 100.0 / len(versionFiles)

                for i, f in enumerate(versionFiles):
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
                            copyFrom = os.path.join(self.versionFolder, (self.filename[0] + '_v' + str(self.currentVersion).zfill(3) + '_360_3DV.mp4'))
                            copyTo = os.path.join(os.path.join(self.serverShotFolder, (self.filename[0] + '_v' + str(self.currentVersion).zfill(3))), (self.filename[0] + '_360_3DV.mp4'))
                            shutil.copyfile(copyFrom, copyTo)

                    # shutil.copyfile(copyFrom, copyTo)
                nuke.executeInMainThread(nuke.message, args=('Shot succsessfully submitted to Gladiator as: ' + newVersionFolderName + '.\n\nGood work! ;p'))

            threading.Thread( target = copyPrerenders ).start()
        createNewRemoteVersion(self.serverShotFolder, self.latestVersion)
