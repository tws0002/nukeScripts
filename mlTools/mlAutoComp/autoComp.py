import nuke,sys,os,shutil
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
from nukescripts import panels
import collections
from collections import defaultdict

'''
from mlTools.mlCacheManager import cacheManager

reload(cacheManager)
from nukescripts import panels
win=panels.registerWidgetAsPanel('cacheManager.nukeAutoCompWindow', 'cacheManager', 'farts', True)



pane = nuke.getPaneFor('Properties.1')
#pane = nuke.getPaneFor('DAG.1')
#win.show()
win.addToPane(pane)
'''



class nukeAutoCompWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        self.assetData={}
        self.columns=[]
        self.rows=[]
        self.publishItems=[]
        self.selection=[]
        self.localDrive="D:"
        
        nuke.tprint("test")
        
        QtGui.QWidget.__init__(self, parent)
        self.shotsTableListen=False
        #createParentTab
        self.mainGridLayout = QtGui.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.setLayout(self.mainGridLayout)

        #create menubar
        self.menubar = QtGui.QMenuBar()
        self.mainGridLayout.setMenuBar(self.menubar)

        #task menu
        self.menuTasks = QtGui.QMenu(self.menubar)
        self.menuTasks.setTitle("&Tasks")
        self.menubar.addAction(self.menuTasks.menuAction())
        #edit menu
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setTitle("&Edit")
        self.menubar.addAction(self.menuEdit.menuAction())

            

        
        self.vSplitter = QtGui.QSplitter()
        self.vSplitter.setOrientation(QtCore.Qt.Vertical)
        self.vSplitter.setObjectName("vSplitter")

        #topTabWidgetWidget(SHOTS, SETTINGS)
        self.topTabWidget = QtGui.QTabWidget(self.vSplitter)
        self.topTabWidget.setObjectName("topTabWidget")
        
        #shotsTab
        self.shotsTab = QtGui.QWidget()
        self.shotsTab.setObjectName("shotsTab")

        #shots Layout
        self.shothorizontalLayout = QtGui.QHBoxLayout(self.shotsTab)
        self.shothorizontalLayout.setObjectName("shothorizontalLayout")

        
        #shotsTable
        self.shotTable = TableSwitcher(self.shotsTab)
        self.shotTable.setObjectName("shotTable")
        self.shotTable.verticalHeader().hide()
        #self.shotTable.horizontalHeader().hide()


        self.shotTable.setAlternatingRowColors(True)
        self.shotTable.setSortingEnabled(False)
        self.shotTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.shotTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.shotTable.setDragEnabled(True)
        #self.shotTable.setAcceptDrops(True)
        #self.shotTable.setDragDropOverwriteMode(False)
        #self.shotTable.setDragDropMode(QtGui.QAbstractItemView.InternalMove) 
        #self.shotTable.horizontalHeader().setStretchLastSection(True) 
        self.shothorizontalLayout.addWidget(self.shotTable)
        
        #add viewerLayout before shots
        self.shotsViewerVLayout = QtGui.QVBoxLayout()
        self.shotsViewerVLayout.setObjectName("shotsGrpVLayout")    
        self.iconLabel=QtGui.QLabel(self)
        self.iconLabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)

        self.shotsViewerVLayout.addWidget(self.iconLabel)
        
        self.shothorizontalLayout.addLayout(self.shotsViewerVLayout)
        
        self.shotsGrpVLayout = QtGui.QVBoxLayout()
        self.shotsGrpVLayout.setObjectName("shotsGrpVLayout")
        self.seqSelection = QtGui.QComboBox(self.shotsTab)
        self.shotsGrpVLayout.addWidget(self.seqSelection)
        
        #shotsButtons
        shotBtns = [
            ["getAssetData", self.getAssetData],
            #["Open In Shotgun", self.openShotgunShotPage],
        ]
        for btn in shotBtns:
            pushBtn = QtGui.QPushButton(self.shotsTab)
            pushBtn.setText(btn[0])
            pushBtn.clicked.connect(btn[1])
            self.shotsGrpVLayout.addWidget(pushBtn)

        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.shotsGrpVLayout.addItem(spacerItem1)
        self.shothorizontalLayout.addLayout(self.shotsGrpVLayout)
        self.topTabWidget.addTab(self.shotsTab,"shots") 
        self.mainGridLayout.addWidget(self.vSplitter, 0, 0, 1, 1)
        self.getAssetData()
        self.setupTable()
        

    def getAssetData(self,*args):
        import tank
        import shotgun_api3 as shotgun

        SHOT=tank.platform.current_engine().context.entity
        print SHOT
        # Get handle to Asset Manager tank application
        assetmgr = tank.platform.current_engine().apps["psy-multi-assetmanager"]
        # Grab updated publish data from shotgun
        publish_directory = assetmgr.publish_directory.find_publish_entity(SHOT)
        #this will iterate over all publishes for a shot, can add
        for publish in list(publish_directory.all_publishes):
            if 'lighting' in publish.path:
                name=publish.name.split(" ")[3]
                renderType=name.split("_")[-1]
                layer="_".join(name.split("_")[:2])
                if not renderType in self.columns:
                    self.columns.append(renderType)
                if not layer in self.rows:
                    self.rows.append(layer)
                if not name in self.assetData.keys():
                    self.assetData[name]=[]
                self.assetData[name].append(publish.version)
       
        print self.assetData
        
    def setupTable(self,*args):
    
        self.shotTable.setColumnCount(len(self.columns))
        colCount=0
        self.columns.sort()
        self.rows.sort()
        for y,c in enumerate(self.columns):  
            self.shotTable.setColumnCount(y+1)
            item = QtGui.QTableWidgetItem()
            item.setText(c)
            self.shotTable.setHorizontalHeaderItem(y, item)
        for x,r in enumerate(self.rows):
            rowNum=self.shotTable.rowCount()
            self.shotTable.insertRow(rowNum)
            self.shotTable.setRowHeight(rowNum, 15)
            for y,c in enumerate(self.columns):  
                for k in self.assetData.keys():
                    if r in k and c in k:
                            item=QtGui.QTableWidgetItem()
                            item.setText(k)
                            self.shotTable.setItem(x,y,item)
    

        
class TableSwitcher(QtGui.QTableWidget):
    def dropEvent(self, dropEvent):
        item_src = self.selectedItems()[0]
        item_dest = self.itemAt(dropEvent.pos())
        print item_dest.row()
        if item_dest:
            item_take = self.takeItem(item_dest.row(),item_dest.column())
            src_row = item_src.row()
            src_col = item_src.column()
            #dest_value = item_dest
            super(TableSwitcher,self).dropEvent(dropEvent)
            self.setItem(src_row,src_col, item_take)
