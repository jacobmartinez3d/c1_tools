if not nuke.rawArgs[1] == '--studio':
    import c1_tools.c1_tools as c1_tools
    import c1_tools.c1_ShotBrowser as c1_shotBrowser
    import nuke
    import nukescripts
    # try:
    #     # < Nuke 11
    #     import PySide.QtCore as QtCore
    #     import PySide.QtGui as QtGui
    #     import PySide.QtGui as QtGuiWidgets
    # except:
    #     # >= Nuke 11
    #     import PySide2.QtCore as QtCore
    #     import PySide2.QtGui as QtGui
    #     import PySide2.QtWidgets as QtGuiWidgets

    def open_shotBrowser():
        nukescripts.panels.registerWidgetAsPanel('c1_shotBrowser.ShotBrowser', 'C1 Shot Browser', 'c1_shotBrowser', True).addToPane(nuke.getPaneFor('Properties.1'))
    # _menu____________________________________________________________________
    nuke.menu( 'Nuke' ).addCommand( 'File/C1 Version Up', 'c1_tools.versionUp(nuke.root().name())', icon='versionUp.png' )
    nuke.menu( 'Nuke' ).addCommand( 'File/C1 Submit Shot', 'c1_tools.submitShot(nuke.root().name())', icon='submitShot.png' )
    nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Shot Browser', 'open_shotBrowser()', icon='sb.png' )
    nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Version Up', 'c1_tools.versionUp(nuke.root().name())', icon='versionUp.png' )
    nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Submit Shot', 'c1_tools.submitShot(nuke.root().name())', icon='submitShot.png' )
    nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Render OU.mp4 with FFmpeg', 'c1_tools.ffmpegRender()', icon='ffmpeg.png' )
    nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Scan for Missing Frames', 'c1_tools.Scan_for_missing_frames()', icon='missingFrames.png' )
