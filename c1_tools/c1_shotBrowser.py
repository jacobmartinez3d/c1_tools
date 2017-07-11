import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
from nukescripts import panels
import nuke
import os
from string import ascii_lowercase
import c1_tools
import subprocess
import shutil
import threading

class ShotBrowser( QtGui.QWidget ):
    def __init__( self, parent=None ):
        self.gladiator = c1_tools.findGladiator()
        self.data = {
            'path': {},
            'nameParts': [],
            'version': []
            }
        self.things = {
            'roots': [],
            'dirs': [],
            'files': []
            }
        self.buttonsArr = {}
        QtGui.QWidget.__init__(self, parent)
        self.btn_group = QtGui.QButtonGroup( self )
        self.setLayout(QtGui.QVBoxLayout())
        #_Choose show___________________________________________________________
        self.showChoices = QtGui.QComboBox(self)
        self.showChoices.addItem('TGR - Tigers of America')
        self.showChoices.addItem('OMF - Operation Mayflower')
        self.showChoices.addItem('ODS - Operation Deathstar')
        self.showChoices.addItem('ODT - Operation Downtown')
        self.showChoices.addItem('ODL - Operation Daylight')
        self.showChoices.addItem('BRZ - Brazil')
        self.showChoices.activated[str].connect(self.retrieveShowData)
        self.layout().addWidget(self.showChoices)
        #_______________________________________________________________________
        #_Download button_
        # self.btn_download = QtGui.QPushButton('Download Shot')
        #_Shot Table____________________________________________________________
        self.shotTable          = QtGui.QTableWidget()
        self.shotTable.header   = ['Shot', 'Version', 'Download']
        self.shotTable.size     = [ 375, 375, 375 ]
        self.shotTable.setColumnCount(len(self.shotTable.header))
        self.shotTable.setHorizontalHeaderLabels(self.shotTable.header)
        self.shotTable.setSelectionMode(QtGui.QTableView.ExtendedSelection)
        self.shotTable.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self.shotTable.setSortingEnabled(1)
        self.shotTable.sortByColumn(1, QtCore.Qt.DescendingOrder)
        self.shotTable.setAlternatingRowColors(True)
        self.shotTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.layout().addWidget(self.shotTable)
        self.shotTable.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        self.retrieveShowData('TGR - Tigers of America')
        self.btn_group.buttonClicked.connect( self.handleButtonClicked )

    def handleButtonClicked( self, button ):
        self.task = nuke.ProgressTask("Downloading...")
        self.numberOfThings = 0

        for roots, dirs, files in os.walk( self.data['path'][button.text()] ):
            self.things['roots'].append(roots)
            for dir in dirs:
                self.things['dirs'].append(dir)
            for file in files:
                self.things['files'].append(file)
        print(str(self.things))
        if len(self.things['files']) > 0:
            self.numberOfThings = len(self.things['files'])
        else:
            self.numberOfThings = 1
        #need to un-include files not to be copied
        self.download(button.text())
        return
    #_Runs each time show menu item is selected_________________________________
    def retrieveShowData(self, choice):
        self.reset()
        showCode = choice.split(' - ')[0]
        # scan the VFX folder and assemble as list
        for folder in os.listdir(self.gladiator):
            # iterate through all folders in the gladiator/___Projects directory
            folderName = os.path.basename(folder)
            # split folder name into parts here so I can count them for validation
            folderNameParts = folderName.split('_')
            # nuke.message(str(folder))
            if folderNameParts[-1] == showCode and not folderNameParts[0] == '.':
                path1 = os.path.join(self.gladiator, folder)
                path2 = os.sep + '6.VFX' + os.sep
                fullPath = path1 + path2
                for shotFolder in os.listdir(fullPath):
                    nameParts = os.path.basename(shotFolder).split('_', 1)
                    path = os.path.join(fullPath, shotFolder)
                    version = c1_tools.retrieveLatestVersion(path, showCode)['int']
                    # compile self.data
                    if nameParts[0] == showCode:
                        self.data['nameParts'].append(nameParts)
                        # set shotName as key, shotFolder path as value
                        versionFolderName = nameParts[0] + '_' + nameParts[1] + '_v' + str(version).zfill(3)
                        self.data['path'][nameParts[1]] = os.path.join(path, versionFolderName)
                        if version < 1:
                            self.data['version'].append('No Submissions')
                        else:
                            self.data['version'].append(version)
                    self.showCode = nameParts[0]
        def populate(data):
            self.shotTable.setRowCount(0)
            for i in range(0, len(data['nameParts'])):
                # nuke.message(str(self.data['version'][i]))
                self.shotTable.insertRow(i)
                # write shotName...
                self.shotTable.setItem(i, 0, QtGui.QTableWidgetItem(self.data['nameParts'][i][1]))
                # write version... (breaks populate() for some reason...)
                # self.shotTable.setItem(i, 1, QtGui.QTableWidgetItem(str(self.data['version'][i]).zfill(3)))
                # button
                self.btn_group.addButton( QtGui.QPushButton(data['nameParts'][i][1]), i )
                self.shotTable.setCellWidget( i, 2, self.btn_group.button(i) )
            return
        populate(self.data)
    def reset( self ):
        self.data = {
            'path': {},
            'nameParts': [],
            'version': []
            }
        for button in self.btn_group.buttons():
            self.btn_group.removeButton(button)
        return
    def download( self, shotName ):
        #_NOTES_
        # need a valid iterator for taskbar
        # need to integrate/share with SubmitShot()
        progIncr = 100.0 / self.numberOfThings

        def copy(src, dst):
            fsrc = open(src, 'rb').read()
            with open(dst, 'wb') as fdst:
                fdst.write(fsrc)
            fsrc.close()
            fdst.close()
        if self.task.isCancelled():
            nuke.executeInMainThread( nuke.message, args=( "Aborted!" ) )
            return
        newDir = 'd:' + os.sep + self.showCode + '_' + shotName
        if not os.path.exists(newDir):
            os.mkdir(newDir)
            if not os.path.exists(os.path.join(newDir, self.showCode + '_' + shotName + '_v' + 005)):
                os.mkdir(os.path.join(newDir, self.showCode + '_' + shotName + '_v' + 005))
        # os.mkdir(os.path.join(newDir, 'Prerenders'))
        for thing in os.listdir(self.data['path'][shotName]):
            copyFrom = os.path.join(self.data['path'][shotName], thing)
            copyTo = os.path.join(newDir, thing)
            nuke.message(copyFrom + '_' + copyTo)
            try:
                shutil.copytree(copyFrom, copyTo)
            except:
                print('error occured downloading something')
            self.task.setProgress(int(progIncr)) #have to multiple progIncr by iterator
            self.task.setMessage(thing)
        # nuke.message(self.data['path'][shotName])
        return subprocess.Popen('explorer "%s"' % newDir)
