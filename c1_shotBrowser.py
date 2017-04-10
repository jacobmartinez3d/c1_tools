import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
from nukescripts import panels
import nuke
import os
from string import ascii_lowercase

class shotBrowser(QtGui.QWidget):
    def __init__(self, parent=None):
        self.usingTemp = False
        self.remoteDir = self.findGladiator()
        QtGui.QWidget.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout())
        #_Choose show___________________________________________________________
        self.showChoices = QtGui.QComboBox(self)
        # i want to automate this list eventually.. for now it's hard-coded...
        self.showChoices.addItem('TGR - Tigers of America')
        self.showChoices.addItem('OMF - Operation Mayflower')
        self.showChoices.addItem('ODS - Operation Deathstar')
        self.showChoices.activated[str].connect(self.retrieveShowData)
        self.layout().addWidget(self.showChoices)
        #_Shot Table____________________________________________________________
        self.shotTable          = QtGui.QTableWidget()
        self.shotTable.header   = ['Show', 'Shot', 'Version', '' ]
        self.shotTable.size     = [ 75, 375, 85, 600 ]
        self.shotTable.setColumnCount(len(self.shotTable.header))
        self.shotTable.setHorizontalHeaderLabels(self.shotTable.header)
        self.shotTable.setSelectionMode(QtGui.QTableView.ExtendedSelection)
        self.shotTable.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self.shotTable.setSortingEnabled(1)
        self.shotTable.sortByColumn(1, QtCore.Qt.DescendingOrder)
        self.shotTable.setAlternatingRowColors(True)
        self.shotTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.shotTable.setRowCount(50)
        self.layout().addWidget(self.shotTable)

        self.shotTable.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        self.retrieveShowData('TGR - Tigers of America')

    # class downloadButton(self, id):
    #     QtGui.QPushButton.__init__(self, id=None)
    #     self.button = QtGui.QPushButton('Download')

    def findGladiator(self):
        for c in ascii_lowercase:
            gladiator = c + ':' + os.sep + 'Departments' + os.sep + '_Post' + os.sep + '__Projects' + os.sep
            if os.path.exists(gladiator):
                # nuke.message('found gladiator drive on drive: ' + c)
                return gladiator
        def setGladiatorSubstitute():
            nuke.message('No gladiator drive found. You may use a temporary directory as long as it follows C1 naming-conventions' +
                '\n\n' + 'Directory must contain show folders with C1 naming: ' +
                '\n\n' + '[show-number]_[show name]_[show-code] (eg: "018_TigerRescue_TGR")')
            self.usingTemp = True
            return nuke.getFilename('Select remote projects directory...')
        return setGladiatorSubstitute()

    def retrieveShowData(self, choice):
        showCode = choice.split(' - ')[0]
        # scan the VFX folder and assemble as list
        data = []
        for folder in os.listdir(self.remoteDir):
            # iterate through all folders in '//gladiator.../_Post/__Projects/'
            folderName = os.path.basename(folder)
            # split folder name into parts here so I can count them for validation
            folderNameParts = folderName.split('_')
            # nuke.message(str(folder))
            if folderNameParts[-1] == showCode and not folderNameParts[0] == '.':
                path1 = os.path.join(self.remoteDir, folder)
                if self.usingTemp == True:
                    fullPath = path1
                else:
                    path2 = os.sep + '6.VFX' + os.sep
                    fullPath = path1 + path2
                for shotFolder in os.listdir(fullPath):
                    nameParts = os.path.basename(shotFolder).split('_', 1)
                    if nameParts[0] == showCode:
                        data.append(nameParts)
                # nuke.message(str(data))
                # os.path.join(self.gladiator, folder)
                # data.append(os.path.join(self.gladiator, folder))

        def populate(data):
            self.shotTable.setRowCount(0)
            for i in range(0, len(data)-1):
                self.shotTable.insertRow(i)
                # write showCode...
                self.shotTable.setItem(i, 0, QtGui.QTableWidgetItem(data[i][0]))
                # write shotCode...
                self.shotTable.setItem(i, 1, QtGui.QTableWidgetItem(data[i][1]))
                # create download button...
                button = QtGui.QPushButton('download')
                self.shotTable.setCellWidget(i, 3, button)
                # self.shotTable.setItem(i, 4, QtGui.QTableWidgetItem(QtGui.QPushButton('test')))
        populate(data)
