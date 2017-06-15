import c1_tools.c1_tools as c1_tools
import c1_tools.c1_shotBrowser as c1_shotBrowser
import nuke
import nukescripts

def open_shotBrowser():
    nukescripts.panels.registerWidgetAsPanel('c1_shotBrowser.shotBrowser', 'C1 Shot Browser', 'c1_shotBrowser', True).addToPane()

# _callbacks____________________________________________________________________
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Shot Browser', 'open_shotBrowser()' )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Create Shot Sub-Folder Structure', 'c1_tools.createShotFolder()' )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Scan for missing frames', 'c1_tools.Luis_Solver()' )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Version Up', 'c1_tools.versionUp(nuke.root().name())' )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Submit Shot', 'c1_tools.submitShot(nuke.root().name())' )
