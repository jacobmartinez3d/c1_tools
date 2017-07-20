# import c1_tools.c1_tools as c1_tools
# import c1_tools.c1_ShotBrowser as c1_shotBrowser
# import c1_tools.c1_User as c1_User
# # import init
# import nuke
# import nukescripts
#
# def open_shotBrowser():
#     nukescripts.panels.registerWidgetAsPanel('c1_shotBrowser.ShotBrowser', 'C1 Shot Browser', 'c1_shotBrowser', True).addToPane(nuke.getPaneFor('Properties.1'))
# # _menu____________________________________________________________________
# nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Shot Browser', 'open_shotBrowser()', icon='c1vrlogo.png' )
# nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Submit Shot', 'c1_tools.submitShot(nuke.root().name())', icon='submitShot.png' )
# nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Version Up', 'c1_tools.versionUp(nuke.root().name())', icon='versionUp.png' )
# nuke.menu( 'Nuke' ).addSeparator( index=2 )
# nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/C1 Create Missing Subfolders', 'c1_tools.createShotFolder()')
# nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Scan for Missing Frames', 'c1_tools.Luis_Solver()' )
# nuke.menu( 'Nuke' ).addCommand( 'C1 Tools/Render OU.mp4 with FFmpeg', 'c1_tools.ffmpegRender()', icon='ffmpeg.png' )
#
# user = c1_User.Login()
# user.validate()
