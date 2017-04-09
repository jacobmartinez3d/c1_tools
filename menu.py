import c1_tools
import nuke

nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Shot Browser', 'c1_tools.openShotBrowser()' )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Set Local Shot Folder', 'c1_tools.setShotFolder()' )
