import hashlib
import nuke
import nukescripts
import fileinput
import os
import smtplib

class Login( nukescripts.PythonPanel ):
    def __init__( self ):
        nukescripts.PythonPanel.__init__( self, 'C1 Login')
        self.validated = False
        self.inp_email = nuke.String_Knob( 'email', 'C1 Email: ')
        self.inp_password = nuke.Password_Knob( 'password', 'Password: ')
        self.loginButton = nuke.PyScript_Knob("Login")
        self.cancelButton = nuke.PyScript_Knob("Cancel")
        #_add knobs
        self.addKnob( self.inp_email )
        self.addKnob( self.inp_password )
        self.addKnob( self.loginButton )
        self.addKnob( self.cancelButton )

        thisDir = os.path.join(os.path.realpath(__file__), os.pardir)
        if os.path.exists(os.path.join(thisDir, 'login.txt')):
            text = open(os.path.join(thisDir, 'login.txt'), 'r+')
            lines = []
            for line in text:
                lines.append( line )
            text.close()
            validate(lines[0], lines[1])
            # self.email = lines[0]
            # self.password = lines[1]
        else:
            nukescripts.PythonPanel.showModal( self )
        return

            # text = open(os.path.join(thisDir, 'login.txt'), 'w')
            # text.write( self.inp_email.value() + '\n')
            # text.write( self.inp_password.value() + '\n')
            # text.close()
        # if not self.validate():
        #     except:
        #         os.remove(os.path.join(thisDir, 'c1_tools/login.txt'))
        #         user = self.validate()
        #         server.login(user[0], user[1])

    def prompt( self ):
        nukescripts.PythonPanel.showModal( self )
        return
    def knobChanged( self, knob ):
        if knob.name() == 'Login':
            if self.validate():
                self.ok()
        return
    def validate( self, email=None, password=None ):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        thisDir = os.path.join(os.path.realpath(__file__), os.pardir)
        self.validated = False

        if not email or not password:
            #_run default search
            if os.path.exists(os.path.join(thisDir, 'login.txt')):
                text = open(os.path.join(thisDir, 'login.txt'), 'r+')
                lines = []
                for line in text:
                    lines.append( line )
                text.close()
                try:
                    server.login(email, password)
                    self.validated = True
                    return [email, password]
                except:
                    print( 'Login Failed!' )
            else:
                try:
                    print(self.inp_email.value(), self.inp_password.value())
                    server.login(self.inp_email.value(), self.inp_password.value())
                    self.validated = True
                    self.email = self.email.value()
                    self.password = self.password.value()
                except:
                    print( 'Prompt Login Failed!')

            return
