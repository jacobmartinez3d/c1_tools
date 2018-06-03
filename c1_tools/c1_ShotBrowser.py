try:
    # < Nuke 11
    import PySide.QtCore as QtCore
    import PySide.QtGui as QtGui
    import PySide.QtGui as QtGuiWidgets
except:
    # >= Nuke 11
    import PySide2.QtCore as QtCore
    import PySide2.QtGui as QtGui
    import PySide2.QtWidgets as QtGuiWidgets
import sys
import nuke
import os
import c1_tools
import subprocess
import shutil
import threading
from nukescripts import panels
from string import ascii_lowercase
from c1_Data import Data
from c1_Copy import Copy
sys.path.append('../init.py')
from init import user
import opentimelineio as otio
otio_timeline = require("E:/local_work/c1_otio/src/OTIO/CMP_testTimeline.json")

class ShotBrowser(QtGuiWidgets.QWidget):
    def __init__(self, parent=None):
        self.gladiator = c1_tools.findGladiator()
        self.data = {
            'path': {},
            'nameParts': [],
            'version': []
        }
        self.buttonsArr = {}
        QtGuiWidgets.QWidget.__init__(self, parent)
        self.btn_group = QtGuiWidgets.QButtonGroup(self)
        self.setLayout(QtGuiWidgets.QVBoxLayout())
        # Choose show
        self.showChoices = QtGuiWidgets.QComboBox(self)
        self.showChoices.addItem('TGR - Tigers of America')
        self.showChoices.addItem('OMF - Operation Mayflower')
        self.showChoices.addItem('ODS - Operation Deathstar')
        self.showChoices.addItem('ODT - Operation Downtown')
        self.showChoices.addItem('ODL - Operation Daylight')
        self.showChoices.addItem('BRZ - Brazil')
        self.showChoices.addItem('SOM - Somalia')
        self.showChoices.addItem('CWF - Wildfires')
        self.showChoices.activated[str].connect(self.retrieveShowData)
        self.layout().addWidget(self.showChoices)
        # Shot Table
        self.shotTable = QtGuiWidgets.QTableWidget()
        self.shotTable.header = ['Download', 'Latest Version']
        self.shotTable.size = [375, 375, 375]
        self.shotTable.setColumnCount(len(self.shotTable.header))
        self.shotTable.setHorizontalHeaderLabels(self.shotTable.header)
        self.shotTable.setSelectionMode(
            QtGuiWidgets.QTableView.ExtendedSelection)
        self.shotTable.setSelectionBehavior(QtGuiWidgets.QTableView.SelectRows)
        self.shotTable.setSortingEnabled(1)
        self.shotTable.sortByColumn(1, QtCore.Qt.DescendingOrder)
        self.shotTable.setAlternatingRowColors(True)
        self.shotTable.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.layout().addWidget(self.shotTable)
        self.shotTable.setSizePolicy(QtGuiWidgets.QSizePolicy(QtGuiWidgets.QSizePolicy.Expanding,
                                                              QtGuiWidgets.QSizePolicy.Expanding))
        self.setSizePolicy(QtGuiWidgets.QSizePolicy(QtGuiWidgets.QSizePolicy.Expanding,
                                                    QtGuiWidgets.QSizePolicy.Expanding))
        self.retrieveShowData('TGR - Tigers of America')
        self.btn_group.buttonClicked.connect(self.handleButtonClicked)
        target = self.data['path'][button.text()]
        data = Data('download', target, self.gladiator)
        request = Copy(target, user.workingDir, data)
        request.download()
        return

    # retrieveShowData each time drop-down menu item is selected
    def retrieveShowData(self, choice):
        self.reset()
        showCode = choice.split(' - ')[0]
        # scan the VFX folder and assemble as list
        for folder in os.listdir(self.gladiator):
            # iterate through all folders in the gladiator/___Projects
            # directory
            folderName = os.path.basename(folder)
            # split folder name into parts to count them for validation
            folderNameParts = folderName.split('_')
            if folderNameParts[-1] == showCode and not folderNameParts[0] == '.':
                path1 = os.path.join(self.gladiator, folder)
                path2 = os.sep + '6.VFX' + os.sep
                fullPath = path1 + path2
                # matching showFolder found, iterate through all its VFX shots
                for shotFolder in os.listdir(fullPath):
                    nameParts = os.path.basename(shotFolder).split('_', 1)
                    path = os.path.join(fullPath, shotFolder)
                    version = c1_tools.retrieveLatestVersion(path, showCode)
                    version = version['int']
                    # compile self.data
                    if nameParts[0] == showCode:
                        self.data['nameParts'].append(nameParts)
                        # set shotName as key, shotFolder path as value
                        versionFolderName = nameParts[
                            0] + '_' + nameParts[1] + '_v' + str(version).zfill(3)
                        self.data['path'][nameParts[1]] = os.path.join(
                            path, versionFolderName)
                        if int(version) < 1:
                            self.data['version'].append('No Submissions')
                        else:
                            self.data['version'].append(version)
                    self.showCode = nameParts[0]

        def populate(data):
            self.shotTable.setRowCount(0)
            for i in range(0, len(data['nameParts'])):
                self.shotTable.insertRow(i)
                # button
                self.btn_group.addButton(
                    QtGuiWidgets.QPushButton(data['nameParts'][i][1]), i)
                self.shotTable.setCellWidget(i, 0, self.btn_group.button(i))
                # write version...
                self.shotTable.setItem(i, 1, QtGuiWidgets.QTableWidgetItem(
                    str(self.data['version'][i]).zfill(3)))
            return
        populate(self.data)

    def reset(self):
        self.data = {
            'path': {},
            'nameParts': [],
            'version': []
        }
        for button in self.btn_group.buttons():
            self.btn_group.removeButton(button)
        return

    def download(self, shotName):
        # NOTES ____________________________________________________________________________________
        # need to integrate/share with SubmitShot()
        #_Notes for next version_
        # 1) create localShotFolder
        # 2) create subFolderStructure
        # 3) checkbox to include:
        #       raw footage,
        #       most recent submission,
        #       pipeline layers
        # 4) copy() selected items + Production Stitches
        # 5) version up & create new shotFolder
        # ------------------------------------------------------------------------------------------
        progIncr = 100.0 / self.numberOfThings

        def copy(src, dst):
            fsrc = open(src, 'rb').read()
            with open(dst, 'wb') as fdst:
                fdst.write(fsrc)
            fsrc.close()
            fdst.close()
        if self.task.isCancelled():
            nuke.executeInMainThread(nuke.message, args=("Aborted!"))
            return
        newDir = 'd:' + os.sep + self.showCode + '_' + shotName  # temp
        if not os.path.exists(newDir):
            os.mkdir(newDir)
            if not os.path.exists(os.path.join(newDir, self.showCode + '_' + shotName + '_v' + 005)):
                os.mkdir(os.path.join(newDir, self.showCode + '_' + shotName + '_v' + 005))
        for thing in os.listdir(self.data['path'][shotName]):
            copyFrom = os.path.join(self.data['path'][shotName], thing)
            copyTo = os.path.join(newDir, thing)
            nuke.message(copyFrom + '_' + copyTo)
            try:
                shutil.copytree(copyFrom, copyTo)
            except:
                print('error occured downloading something')
            # have to multiple progIncr by iterator
            self.task.setProgress(int(progIncr))
            self.task.setMessage(thing)
        # nuke.message(self.data['path'][shotName])
        return subprocess.Popen('explorer "%s"' % newDir)
