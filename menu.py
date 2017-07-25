if not nuke.rawArgs[1] == '--studio':
    import c1_tools.c1_tools as c1_tools
    import c1_tools.c1_ShotBrowser as c1_shotBrowser
    import nuke
    import nukescripts
    import PySide.QtGui as QtGui

    def open_shotBrowser():
        nukescripts.panels.registerWidgetAsPanel('c1_shotBrowser.ShotBrowser', 'C1 Shot Browser', 'c1_shotBrowser', True).addToPane(nuke.getPaneFor('Properties.1'))
    # _menu____________________________________________________________________
    nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Shot Browser', 'open_shotBrowser()', icon='sb.png' )
    nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Submit Shot', 'c1_tools.submitShot(nuke.root().name())', icon='submitShot.png' )
    nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Version Up', 'c1_tools.versionUp(nuke.root().name())', icon='versionUp.png' )
    nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Scan for Missing Frames', 'c1_tools.Luis_Solver()', icon='missingFrames.png' )
    nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Render OU.mp4 with FFmpeg', 'c1_tools.ffmpegRender()', icon='ffmpeg.png' )
    nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Write --> Read', 'c1_tools.writeToRead()' ).setShortcut('Ctrl+Alt+R')
