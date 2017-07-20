import c1_tools.c1_User as c1_User
import nuke
#_What this file is for:________________________________________________________
#   Altering the initial state of Nuke when it launches, making custom changes
#_______________________________________________________________________________

if not nuke.rawArgs[1] == '--studio':
    user = c1_User.Login()
    user.validate()
