import c1_tools
import c1_shotBrowser
import nuke
import nukescripts

def open_shotBrowser():
    nukescripts.panels.registerWidgetAsPanel('c1_shotBrowser.shotBrowser', 'C1 Shot Browser', 'c1_shotBrowser', True).addToPane()

# _callbacks____________________________________________________________________
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Shot Browser', 'open_shotBrowser()' )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Set Local Shot Folder', 'c1_tools.setShotFolder()' )



#_write node override_________________________________________________________________
