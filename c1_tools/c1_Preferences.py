# preferences panel to allow inputting cutom parameters for the structure of a project and its
# naming conventions.
# --------------------------------------------------------------------------------------------------
import hashlib
import nuke
from nukescripts.panels import PythonPanel
import fileinput
import os
import smtplib
import sys

class Preferences( PythonPanel ):
    def __init__( self ):
        PythonPanel.__init__( self, 'C1 Preferences')
        # C1 Preferences
        self.email = None
        self.localDir = None
        self.projectDir = None
        # custom regex definitions for validation engine
        self.regex = {}
        self.projectStructure = {
        	'root': {}
        }
        self.scriptDir = {
            'root': os.path.join(os.path.join(os.path.realpath(__file__), os.pardir), os.pardir),
            'c1_tools': os.path.join(os.path.realpath(__file__), os.pardir)
            }
        # define knobs
        self.inp_email = nuke.String_Knob( 'email', 'C1 Initials: ')
        self.inp_localDir = nuke.String_Knob( 'localDir', 'Local Working Directory: ')
        self.btn_localDir = nuke.PyScript_Knob("Set Working Dir")
        self.loginButton = nuke.PyScript_Knob("Login")
        self.cancelButton = nuke.PyScript_Knob("Cancel")
        # Project Map Tab
        self.projectMapTab = nuke.Tab_Knob("Project Map")
        self.setProjectButton = nuke.File_Knob('projectDir','Project Location')
        self.inp_projectLocation = nuke.String_Knob( 'projectDir',
            '<b><font size="3" color="red">Remote Project Directory</font></b>')
        self.inp_projectName = nuke.String_Knob( 'projectName', 'Project Name' )
        self.inp_projectNum = nuke.Int_Knob( 'projectNum')
        # self.inp_projectNum.clearFlag( nuke.STARTLINE )
        self.inp_projectCode = nuke.String_Knob( 'projectCode', 'Project Code' )
        self.inp_projectCode.clearFlag( nuke.STARTLINE )
        
        # add knobs
        self.addKnob( self.inp_localDir )
        self.addKnob( self.btn_localDir )
        self.addKnob( self.inp_email )
        self.addKnob( self.loginButton )
        self.addKnob( self.cancelButton )
        # Project Map Tab
        self.addKnob( self.projectMapTab )
        self.addKnob( self.setProjectButton )
        self.addKnob( self.inp_projectName )
        self.addKnob( self.inp_projectNum )
        self.addKnob( self.inp_projectCode )
        # retrieve previous login from login.txt
        self.retrieveLogin()
        return

    def validate( self ):
        self.retrieveLogin()
        return
    # Retrieve login.txt data
    def retrieveLogin( self ):
        if os.path.exists(os.path.join(self.scriptDir['c1_tools'], 'login.txt')):
            text = open(os.path.join(self.scriptDir['c1_tools'], 'login.txt'), 'r+')
            lines = []
            for line in text:
                # append each line of the found login.txt                
                lines.append( line )
            text.close()
            self.email = lines[0]
            self.localDir = lines[1]
        else:
            self.prompt()
        print( 'Succsessfully logged in as: ' + self.email )
        return
    # create login.txt data
    def createLogin( self ):
        try:
            text = open(os.path.join(self.scriptDir['c1_tools'], 'login.txt'), 'w')
            text.write( self.inp_email.value() + '\n')
            text.write( self.inp_localDir.value())
            text.close()
        except:
            print( 'Failed to save login info! ')
        return
    def prompt( self ):
        PythonPanel.showModal( self )
        return
    def knobChanged( self, knob ):
        if knob.name() == 'Login':
            self.email = self.inp_email.value()
            self.localDir = self.inp_localDir.value()
            # write login.txt
            self.createLogin()
            self.status = 'online'
            self.ok()
        elif knob.name() == 'Set Working Dir':
            self.inp_localDir.setValue(os.path.abspath(nuke.getFilename(
                'Navigate to Local Working Directory...')))
        elif knob.name() == 'Project Location':
            self.inp_projectLocation.setValue(os.path.abspath(nuke.getFilename(
                'Navigate to Remote \'Root\' Project Directory...')))
        return
