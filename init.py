import c1_tools.c1_tools as c1_tools
import c1_tools.c1_ShotBrowser as c1_shotBrowser
import c1_tools.c1_User as c1_User
import nuke
import smtplib
# import nukescripts

#_What this file is for:________________________________________________________
#   Altering the initial state of Nuke when it launches, making custom changes
#_______________________________________________________________________________

#_chech for login.txt
# def validate():
#     thisDir = os.path.join(os.path.realpath(__file__), os.pardir)
#     try:
#         text = open(os.path.join(thisDir, 'c1_tools/login.txt'), 'r+')
#         text.close()
#         return True
#     except:
#         result = c1_User.Login().validate()
#         if result:
#             text = open(os.path.join(thisDir, 'c1_tools/login.txt'), 'w')
#             for line in result:
#                 text.write( line + '\n')
#             text.close()
#         return False

user = c1_User.Login()
# if user.validate()
