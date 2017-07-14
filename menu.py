# import c1_tools.c1_tools as c1_tools
# import c1_tools.c1_ShotBrowser as c1_shotBrowser
# import init
# import nuke
# import nukescripts
#
# def open_shotBrowser():
#     nukescripts.panels.registerWidgetAsPanel('c1_shotBrowser.ShotBrowser', 'C1 Shot Browser', 'c1_shotBrowser', True).addToPane(nuke.getPaneFor('Properties.1'))
# # _callbacks____________________________________________________________________
# nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Shot Browser', 'open_shotBrowser()', icon='sb.png' )
# nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Submit Shot', 'c1_tools.submitShot(nuke.root().name())' )
# nuke.menu( 'Nuke' ).addSeparator( index=2 )
# nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Create Missing Subfolders', 'c1_tools.createShotFolder()' )
# nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Scan for Missing Frames', 'c1_tools.Luis_Solver()' )
# nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Version Up', 'c1_tools.versionUp(nuke.root().name())' )
# nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Render OU.mp4 with FFmpeg', 'c1_tools.ffmpegRender()' )
