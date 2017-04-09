import c1_tools
import c1_shotBrowser
import nuke
import nukescripts
from nukescripts import panels

nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Shot Browser', "panels.registerWidgetAsPanel('shotBrowser', 'C1 Shot Browser', 'c1_shotBrowser', True).addToPane()" )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Set Local Shot Folder', 'c1_tools.setShotFolder()' )
