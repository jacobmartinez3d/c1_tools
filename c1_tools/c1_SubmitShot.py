import nuke
import nukescripts
import os
import shutil
import threading
import smtplib
import email.utils as emailUtils
import sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
sys.path.append('../init.py')
from init import user as c1_user

class submitShotDialogue( nukescripts.PythonPanel ):
    def __init__( self, data ):
        nukescripts.PythonPanel.__init__( self, 'Submit Shot')
        self.gladiator = data.gladiator
        self.dialogueText = data.dialogueText
        self.validated = data.validated
        self.user = c1_user
        #filename fragments
        self.filepath = data.filepath
        self.filename = data.filename
        self.showCode = data.showCode
        self.shotName = data.shotName
        self.fileversion = data.fileversion
        #_folders
        self.versionFolder = data.versionFolder
        self.shotFolder = data.shotFolder
        self.showFolder = data.showFolder
        #_knobs_________________________________________________________________
        self.emailBool = nuke.Boolean_Knob('emailBool', 'Send Email to VFX')
        self.addKnob( self.emailBool )
        self.emailBool.setValue( False )
        self.emailMsg = nuke.Multiline_Eval_String_Knob( 'Type your shot notes here(if enabled).', '')
        self.addKnob( self.emailMsg )
        self.emailMsg.setEnabled( False )
        self.sep = nuke.Text_Knob('','')
        self.addKnob( self.sep )
        self.cancelButton = nuke.PyScript_Knob("Cancel")
        self.addKnob( self.dialogueText )
        self.button1 = nuke.PyScript_Knob( "submit", self.shotName + '_v' + str( self.versionFolder.ver.remote + 1 ).zfill(3) )
        self.button2 = nuke.PyScript_Knob( "submit", self.shotName + '_v' + str( self.fileversion ).zfill(3) )

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
        if knob.name() == 'submit':
            self.submitShot()
            self.ok()
        if knob.name() == 'emailBool':
            self.emailMsg.setEnabled( self.emailBool.value() )

    def submitShot( self ):
        #_NOTES_________________________________________________________________
        # -currently creates folder on gladiator before user has chance to accept or not
        #_______________________________________________________________________
        def email():
            if self.user.status == 'online':
                myid = emailUtils.make_msgid()
                toaddr = "umbrellabuddha@gmail.com"
                subject = str(self.shotName) + '_v' + str(self.fileversion).zfill(3)
                body = self.versionFolder.path.remote + '\n\n' + self.emailMsg.value()
                msg = MIMEMultipart()
                msg['Subject'] = subject
                msg['From'] = self.user.email
                msg['To'] = toaddr
                msg.add_header( "Message-ID", myid )
                msg.attach(MIMEText(body, 'plain'))
                try:
                    self.user.server.login(self.user.email, self.user.password)
                    text = msg.as_string()
                    self.user.server.sendmail(self.user.email, toaddr, text)
                    # c1_user.server.quit()
                except:
                    nuke.message( 'Could not log in, no email was sent with this submission! Restart Nuke to try reconnecting.' )
            else:
                nuke.message( 'Could not log in, no email was sent with this submission! Restart Nuke to try reconnecting.' )
            return

        def createNewRemoteVersion( serverShotFolder ):
            newVersionFolderName = self.shotName + '_v' + str(self.fileversion).zfill(3)
            self.versionFolder.path.set( 'remote', os.path.join(serverShotFolder, self.showCode + '_' + newVersionFolderName))
            # newVersionFolderPath = os.path.join(serverShotFolder, newVersionFolderName)
            localPrerenders = os.path.join(self.versionFolder.path.local, 'Prerenders')
            remotePrerenders = os.path.join(self.versionFolder.path.remote, 'Prerenders')
            # nuke.message(localPrerenders + '_' + remotePrerenders)
            if len(os.listdir(localPrerenders)) < 2:
                nuke.message('Your Prerenders folder has less than 2 files in it. Please check and re-submit!')
                return

            # create folders/files on Gladiator...
            os.mkdir(self.versionFolder.path.remote)
            # do little dance to save to remote dir, then revert back to previous local session
            currentScript = nuke.toNode('root').name()
            nuke.scriptSaveAs(os.path.join(self.versionFolder.path.remote, os.path.basename(self.versionFolder.path.remote) + '.nk'))
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
                versionFiles = os.listdir(self.versionFolder.path.local)
                #filter out unaccepted files
                arr = versionFiles
                # for item in versionFiles:
                #     if os.path.isdir(item):
                #         nuke.executeInMainThread( nuke.message, args=( str(item) ) )
                frames = os.listdir(localPrerenders)

                #need to un-include files not to be copied
                progIncr = 100.0 / len(frames)
                acceptedFiles = {
                    'Prerenders': 'Prerenders',
                    '360_3DV.mp4': '_360_3DV.mp4',
                    'mocha': '.moc',
                    'ae': '.ae',
                    'shotNotes': 'shotNotes.txt'
                    }
                exceptions = []
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

                    # nuke.executeInMainThread( nuke.message, args=( str(copyFrom) ) )
                    for item in acceptedFiles:
                        if item == 'Prerenders':
                            copyFrom = os.path.join(localPrerenders, f)
                            copyTo = os.path.join(remotePrerenders, f)
                            try:
                                shutil.copyfile(copyFrom, copyTo)
                            except:
                                msg = "--> No 'Prerenders' folder found!\n"
                                exceptions.append( msg )
                        elif item == '360_3DV.mp4':
                            copyFrom = os.path.join(self.versionFolder.path.local, (self.filename + '_v' + str(self.versionFolder.ver.local).zfill(3) + '_360_3DV.mp4'))
                            copyTo = os.path.join(os.path.join(self.shotFolder.path.remote, (self.filename + '_v' + str(self.versionFolder.ver.remote + 1).zfill(3))), (self.filename + '_360_3DV.mp4'))
                            try:
                                shutil.copyfile(copyFrom, copyTo)
                            except:
                                msg = "--> No '360_3DV.mp4' found!\n"
                                exceptions.append( msg )

                nuke.executeInMainThread(nuke.message, args=('Shot succsessfully submitted to Gladiator as: ' + self.showCode + '_' + newVersionFolderName + '.\n\nGood work! ;p'))
            threading.Thread( target = copyPrerenders ).start()
        createNewRemoteVersion( self.shotFolder.path.remote )
        if self.emailBool.value() == True:
            email()
