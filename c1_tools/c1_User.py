# A login panel which prompts the user for:
#   - Their initials (used for identification),
#   - Their local working directory(used for shotBrowser when downloading shots locally).
# --------------------------------------------------------------------------------------------------
import hashlib
import nuke
from nukescripts.panels import PythonPanel
import fileinput
import os
import smtplib
import sys


class Login(PythonPanel):

    def __init__(self):
        PythonPanel.__init__(self, 'C1 Login')
        self.email = None
        self.workingDir = None
        self.scriptDir = {
            'root': os.path.join(os.path.join(os.path.realpath(__file__), os.pardir), os.pardir),
            'c1_tools': os.path.join(os.path.realpath(__file__), os.pardir)
        }
        # define knobs
        self.inp_email = nuke.String_Knob('email', 'Artist: ')
        self.inp_workingDir = nuke.String_Knob(
            'workingDir', 'Local Working Directory: ')
        self.btn_workingDir = nuke.PyScript_Knob("Set Working Dir")
        self.loginButton = nuke.PyScript_Knob("Login")
        self.cancelButton = nuke.PyScript_Knob("Cancel")
        # add knobs
        self.addKnob(self.inp_workingDir)
        self.addKnob(self.btn_workingDir)
        self.addKnob(self.inp_email)
        self.addKnob(self.loginButton)
        self.addKnob(self.cancelButton)
        # retrieve previous login from login.txt
        self.retrieveLogin()
        return

    def validate(self):
        self.retrieveLogin()
        # If needed, future validation checks will go here
        return

    def retrieveLogin(self):
        # if Login.txt already exists, skip prompt and login automatically
        if os.path.exists(os.path.join(self.scriptDir['c1_tools'], 'login.txt')):
            text = open(os.path.join(self.scriptDir[
                        'c1_tools'], 'login.txt'), 'r+')
            lines = []
            for line in text:
                # append each line of login.txt
                lines.append(line)
            text.close()
            self.email = lines[0]
            self.workingDir = lines[1]
        else:
            # if no Login.txt was found, show prompt
            self.prompt()
        print('Succsessfully logged in as: ' + self.email)
        return

    def createLogin(self):
        # creates login.txt data
        try:
            text = open(os.path.join(self.scriptDir[
                        'c1_tools'], 'login.txt'), 'w')
            text.write(self.inp_email.value() + '\n')
            text.write(self.inp_workingDir.value())
            text.close()
        except:
            print('Failed to save login info! ')
        return

    def prompt(self):
        PythonPanel.showModal(self)
        return

    def knobChanged(self, knob):
        if knob.name() == 'Login':
            # capture user-inputted values
            self.email = self.inp_email.value()
            self.workingDir = self.inp_workingDir.value()
            # write login.txt
            self.createLogin()
            self.status = 'online'
            # this is a built-in PythonPanel method for pressing ok button
            self.ok()
        elif knob.name() == 'Set Working Dir':
            # open Nuke's file navigator
            self.inp_workingDir.setValue(os.path.abspath(
                nuke.getFilename('Navigate to Local Working Directory...')))
        return
