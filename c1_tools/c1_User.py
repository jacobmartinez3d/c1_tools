import hashlib
import nuke
import nukescripts
import fileinput
import os
import smtplib

class Login( nukescripts.PythonPanel ):
    def __init__( self ):
        nukescripts.PythonPanel.__init__( self, 'C1 Login')
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.status = 'offline'
        self.server.starttls()
        self.email = None
        self.password = None
        self.scriptDir = {
            'root': os.path.join(os.path.join(os.path.realpath(__file__), os.pardir), os.pardir),
            'c1_tools': os.path.join(os.path.realpath(__file__), os.pardir)
            }
        #_define knobs
        self.inp_email = nuke.String_Knob( 'email', 'C1 Email: ')
        self.inp_password = nuke.Password_Knob( 'password', 'Password: ')
        self.loginButton = nuke.PyScript_Knob("Login")
        self.cancelButton = nuke.PyScript_Knob("Cancel")
        #_add knobs
        self.addKnob( self.inp_email )
        self.addKnob( self.inp_password )
        self.addKnob( self.loginButton )
        self.addKnob( self.cancelButton )
        #_retrieve previous login from login.txt
        self.retrieveLogin()
        return
    #_Retrieve login.txt data
    def retrieveLogin( self ):
        if os.path.exists(os.path.join(self.scriptDir['c1_tools'], 'login.txt')):
            text = open(os.path.join(self.scriptDir['c1_tools'], 'login.txt'), 'r+')
            lines = []
            for line in text:
                lines.append( line )
            text.close()
            self.email = lines[0]
            self.password = lines[1]
        return
    #_create login.txt data
    def createLogin( self ):
        try:
            text = open(os.path.join(self.scriptDir['c1_tools'], 'login.txt'), 'w')
            text.write( self.inp_email.value() + '\n')
            text.write( self.inp_password.value() + '\n')
            text.close()
        except:
            print( 'Failed to save login info! ')
        return
    def prompt( self ):
        nukescripts.PythonPanel.showModal( self )
        return
    def knobChanged( self, knob ):
        if knob.name() == 'Login':
            try:
                if self.server.login(self.inp_email.value(), self.inp_password.value())[0] == 235:
                    self.status = 'online'
                else:
                    self.status = 'offline'
                self.email = self.inp_email.value()
                self.password = self.inp_password.value()
                print( 'Succsessfully logged in as: ' + self.email )
                #_write login.txt
                self.createLogin()
                self.ok()
            except:
                raise
                return False
        return
    def validate( self ):
        self.retrieveLogin()
        try:
            #_try login.txt
            # print( 'Trying to connect using:\n' + self.email + '\n' + self.password)
            if self.server.login(self.email, self.password)[0] == 235:
                self.status = 'online'
                print( 'Succsessfully logged in as: ' + self.email )
                return [self.email, self.password]
            else:
                self.status = 'offline'
        except:
            print( 'Auto-Login Failed!' )
            self.prompt()
        return
