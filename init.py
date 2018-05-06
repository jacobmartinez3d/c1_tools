import nuke
from nukescripts import *

#_What this file is for:________________________________________________________
#   Altering the initial state of Nuke when it launches, making custom changes
#_______________________________________________________________________________
print(str(nuke.rawArgs))
import c1_tools.c1_User as c1_User
user = c1_User.Login()
user.validate()
