import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
from nukescripts import panels
import nuke
import os
from string import ascii_lowercase

class shotBrowser(QtGui.QWidget):
    def __init__(self, parent=None):
        self.gladiator = self.findGladiator()
        QtGui.QWidget.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout())
        #_Choose show___________________________________________________________
        self.showChoices = QtGui.QComboBox(self)
        self.showChoices.addItem('TGR - Tigers of America')
        self.showChoices.addItem('OMF - Operation Mayflower')
        self.showChoices.addItem('ODS - Operation Deathstar')
        self.showChoices.activated[str].connect(self.retrieveShowData)
        self.layout().addWidget(self.showChoices)
        #_Shot Table____________________________________________________________
        self.shotTable          = QtGui.QTableWidget()
        self.shotTable.header   = ['Show', 'Shot', 'Version', 'Notes' ]
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
    def findGladiator(self):
        for c in ascii_lowercase:
            gladiator = c + ':' + os.sep + 'Departments' + os.sep + '_Post' + os.sep + '__Projects' + os.sep
            if os.path.exists(gladiator):
                # nuke.message('found gladiator drive on drive: ' + c)
                return gladiator


    def retrieveShowData(self, choice):
        showCode = choice.split(' - ')[0]
        # scan the VFX folder and assemble as list
        arr = []
        for folder in os.listdir(self.gladiator):
            # iterate through all folders in '//gladiator.../_Post/__Projects/'
            folderName = os.path.basename(folder)
            folderNameParts = folderName.split('_')
            if len(folderNameParts) == 3 and not folderNameParts[0] == '.':
                # only append the right folders
                arr.append(folderNameParts)
        def populate(folderNameParts):
            self.shotTable.setRowCount(0)
            for i in range(0, len(folderNameParts)-1):
                self.shotTable.insertRow(i)
                self.shotTable.setItem(i, 0, QtGui.QTableWidgetItem(folderNameParts[i][0]))
        populate(arr)
