import c1_tools.c1_tools as c1_tools
import c1_tools.c1_ShotBrowser as c1_shotBrowser
import c1_tools.c1_Preferences as c1_Preferences
import nuke
import nukescripts
try:
    import PySide.QtGui as QtGui
except:
    import PySide2.QtGui as QtGui

def open_shotBrowser():
    nukescripts.panels.registerWidgetAsPanel('c1_shotBrowser.ShotBrowser', 'C1 Shot Browser', 'c1_shotBrowser', True).addToPane(nuke.getPaneFor('Properties.1'))
def open_Preferences():
	preferences = c1_Preferences.Preferences()
	preferences.prompt()
# _menu____________________________________________________________________
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Shot Browser', 'open_shotBrowser()', icon='sb.png' )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Submit Shot', 'c1_tools.submitShot(nuke.root().name())', icon='submitShot.png' )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Version Up', 'c1_tools.versionUp(nuke.root().name())', icon='versionUp.png' )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Scan for Missing Frames', 'c1_tools.Luis_Solver()', icon='missingFrames.png' )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Render OU.mp4 (FFmpeg)', 'c1_tools.ffmpegRender()', icon='ffmpeg.png' )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Render Titles QC-Sequence (FFmpeg)', 'c1_tools.titles_qc()', icon='ffmpeg.png' )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Write --> Read', 'c1_tools.writeToRead()' ).setShortcut('Ctrl+Alt+R')
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Convert Prores to mp4', 'c1_tools.proresToMp4()' )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Build local shot folder', 'c1_tools.createShotFolder()' )
nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Preferences', 'open_Preferences()' )
