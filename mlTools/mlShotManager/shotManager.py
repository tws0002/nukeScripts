import nuke
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
from nukescripts import panels
import nukescripts
import os,re,sys,shutil
import collections
import string
import subprocess
from collections import defaultdict
import json

from functools import partial



#todo:
#check for missing frames in publishedSeqs


from methods import sgMethods
reload(sgMethods)
from methods import qubeMethods
reload(qubeMethods)
from methods import rvMethods
reload(rvMethods)

#determine sequences root
localGizmoDir=''
for p in sys.path:
    if 'nuke' in p and 'scripts' in p and 'projects' in p:
        localGizmoDir= p.replace('\\','/')
projectName=localGizmoDir.split('/')[2]

#globalVariables
PM_ROOT='P:/projects/PROJNAME/code/primary/addons/nuke'.replace('PROJNAME',projectName)
PROJECT_ID=0





class NukeTestWindow(QtGui.QWidget):
    def __init__(self, parent=None):

        #classGlobalValues
        self.statusColor = {'cmpt':QtGui.QColor(0,100,0),'rev':QtGui.QColor(100,100,0),'fkd':QtGui.QColor(100,0,0),'ip':QtGui.QColor(0,0,100)}
        self.seqDir='P:/projects/'+projectName+'/sequences'
        self.shotDir=self.seqDir+'/sequenceName'
        self.template_nukeScriptPath=self.shotDir+'/shotNum/composite/work/nuke'
        self.template_3dPath=self.shotDir+'/shotNum/lighting/output/render'
        self.template_2dPath=self.shotDir+'/shotNum/composite/output/render'
        self.rendersPath=self.template_3dPath
        self.nukeScriptsPath=""
        self.projectManagerRoot=os.path.dirname(__file__)
        self.projectData=PM_ROOT+'/projectData.txt'
        self.publishRendersData=PM_ROOT+'/publishes.txt'
        self.shotData=PM_ROOT+'/shotData.txt'
        self.notesData=PM_ROOT+'/notes.txt'
        self.userData=PM_ROOT+'/userData.txt'
        self.recentSeq=self.getUserData()
        self.thumbsPath=PM_ROOT+'/thumbs'
        self.shotgunNotes={}
        self.shotgunShotData={}
        self.shotgunPublishes={}
        self.shotgunAssetData={}
        self.qubeStatus={}
        self.tabs=["Renders_In","Renders_Out","Notes"]
        self.searchDir=""
        self.fileFilterText="_comp_"
        self.selSeq=""
        self.selShot=""
        self.selScript=""
        
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
        #shotgun menu
        self.menuSG = QtGui.QMenu(self.menubar)
        self.menuSG.setTitle("&Shotgun")
        self.menubar.addAction(self.menuSG.menuAction())
        #Qube menu
        self.menuQube = QtGui.QMenu(self.menubar)
        self.menuQube.setTitle("&Qube")
        self.menubar.addAction(self.menuQube.menuAction())
        
        menuItems = [
            ["Status Report", self.menuTasks, self.statusReport],
            ["Find New Renders_All", self.menuTasks, self.findAllShotsNewRenders_all],
            ["Find New Renders_thisSequence", self.menuTasks, self.findAllShotsNewRenders_thisSequence],
            ["Clear Shot Alerts", self.menuTasks, self.clearSequenceAlerts],
            ["Flood comp_v001", self.menuTasks, self.floodComps],
            ["importSelectedShotSequences", self.menuTasks, self.importSelectedNukeScriptSeqs],
            ["Show Assets", self.menuEdit, self.createAssetsTab],
            ["Add Column", self.menuEdit, self.addColumn],
            ["Remove Column", self.menuEdit, self.removeColumn],
            ["update thumbnails", self.menuEdit, self.updateAllShotThumbnails],
            ["remove Old Comps", self.menuEdit, self.removeOldRenders],
            ["remove List Renders", self.menuEdit, self.removeListRenders],
            ["remove renders Data", self.menuEdit, self.removeRendersData],
            ["update Shot Assigns", self.menuSG, self.updateShotAssigns],
            ["showQubeStatus", self.menuQube, self.createQubeTab],
            ["submitShot", self.menuQube, self.submitShot],
            ["submitSequence", self.menuQube, self.submitSequence],
            #["update Shot Assigns", self.menuTasks, self.openScriptFile],
            #["reset composite status", self.menuSG, partial(sgMethods.resetCompStatus,PROJECT_ID,SEQUENCES)]
        ]
        for itm in menuItems:
            menuAction = QtGui.QAction(self.mainGridLayout)
            menuAction.setText(itm[0])
            itm[1].addAction(menuAction)
            menuAction.triggered.connect(itm[2])
            

        
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
        self.shotTable = QtGui.QTableWidget(self.shotsTab)
        self.shotTable.setObjectName("shotTable")
        self.shotTable.verticalHeader().hide()
        #self.shotTable.horizontalHeader().hide()
        self.shotTable.setColumnCount(6)
        item = QtGui.QTableWidgetItem()
        item.setText("Shot")
        self.shotTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        item.setText("Assigned")
        self.shotTable.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        item.setText("CompStatus")
        self.shotTable.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        item.setText("LightStatus")
        self.shotTable.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        item.setText("NewRenders")
        self.shotTable.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        item.setText("Notes")
        self.shotTable.setHorizontalHeaderItem(5, item)
        self.shotTable.setAlternatingRowColors(True)
        self.shotTable.setSortingEnabled(False)
        self.shotTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.shotTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
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
            ["UpdateTable", self.refreshTable],
            #["Open In Shotgun", self.openShotgunShotPage],
        ]
        for btn in shotBtns:
            pushBtn = QtGui.QPushButton(self.shotsTab)
            pushBtn.setText(btn[0])
            pushBtn.clicked.connect(btn[1])
            self.shotsGrpVLayout.addWidget(pushBtn)
            
        self.updatedText=QtGui.QLabel(self.shotsTab)
        self.updatedText.setText("last updated:\n30 mins ago")
        self.shotsGrpVLayout.addWidget(self.updatedText)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.shotsGrpVLayout.addItem(spacerItem1)
        self.shothorizontalLayout.addLayout(self.shotsGrpVLayout)
        self.topTabWidget.addTab(self.shotsTab,"shots")        
        
        ####midTab
        self.midTabWidget = QtGui.QTabWidget(self.vSplitter)
        self.midTabWidget.setObjectName("midTabWidget")
        
        #filesTab
        self.filesTab = QtGui.QWidget()
        self.filesTab.setObjectName("filesTab")

        #List Layout
        self.fileshorizontalLayout = QtGui.QHBoxLayout(self.filesTab)
        self.fileshorizontalLayout.setObjectName("fileshorizontalLayout")
        
        #List
        self.filesList = QtGui.QListWidget(self.filesTab)
        self.filesList.setObjectName("filesList")
        self.filesList.setAlternatingRowColors(True)
        self.filesList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        
        self.fileshorizontalLayout.addWidget(self.filesList)
        self.filesGrpVLayout = QtGui.QVBoxLayout()
        
        self.fileFilter= QtGui.QLineEdit(self.filesTab)
        self.fileFilter.setMaximumWidth(120)
        self.fileFilter.setText(self.fileFilterText)
        self.filesGrpVLayout.addWidget(self.fileFilter)
        
        fileListBtns = [
            ["open script", [self.openScriptFile]],
            ["version up", [self.versionUpFile,self.listNukeFiles]],
            ["open directory", [self.openInExplorer]],
            ["open In Shotgun", [self.openShotgunShotPage]],
            ["switch script", [self.switchOpenScriptFile]],
        ]
        for btn in fileListBtns:
            pushBtn = QtGui.QPushButton(self.filesTab)
            pushBtn.setText(btn[0])
            for func in btn[1]:
                pushBtn.clicked.connect(func)
            self.filesGrpVLayout.addWidget(pushBtn)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.filesGrpVLayout.addItem(spacerItem)
        self.fileshorizontalLayout.addLayout(self.filesGrpVLayout)

        
        
        self.midTabWidget.addTab(self.filesTab,"files")

        ####Bottom Tab
        self.bottomTab = QtGui.QTabWidget(self.vSplitter)
        self.bottomTab.setObjectName("bottomTab")
        
        #RendersIN TAB
        self.RendersInTab = QtGui.QWidget()
        self.RendersInTab.setObjectName("RendersInTab")
        self.RendersInHLayout = QtGui.QHBoxLayout(self.RendersInTab)
        #TreeA_Buttons
        self.RendersInVLayoutA = QtGui.QVBoxLayout()
        RendersInTreeABtns = [
            ["update Script to Latest", self.updateShotToLatest],
            #["replace selected Renders", self.replaceRendersFromSelections],
            ["expandTrees", self.expandTrees],
        ]
        for btn in RendersInTreeABtns:
            pushBtn = QtGui.QPushButton(self.bottomTab)
            pushBtn.setText(btn[0])
            pushBtn.clicked.connect(btn[1])
            self.RendersInVLayoutA.addWidget(pushBtn)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.RendersInVLayoutA.addItem(spacerItem)
        self.RendersInHLayout.addLayout(self.RendersInVLayoutA)
        
        #NukeScriptRendersTree
        self.RendersInTreeA = QtGui.QTreeWidget()
        self.RendersInTreeA.setMinimumHeight(200)
        self.RendersInTreeA.setObjectName("RendersInTreeA")
        item=QtGui.QTreeWidgetItem()
        item.setText(0,"Renders in selected script:")
        self.RendersInTreeA.setHeaderItem(item)
        self.RendersInHLayout.addWidget(self.RendersInTreeA)
        #ServerRendersTree
        self.RendersInTreeB = QtGui.QTreeWidget()
        self.RendersInTreeB.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.RendersInTreeB.setObjectName("RendersInTreeB")
        item=QtGui.QTreeWidgetItem()
        item.setText(0,"Renders in selected shot:")
        item.setText(1,"frames:")
        item.setText(2,"width:")
        self.RendersInTreeB.setHeaderItem(item)
        self.RendersInTreeB.setColumnCount(3)
        self.RendersInTreeB.resizeColumnToContents(0)
        self.RendersInTreeB.resizeColumnToContents(1)
        self.RendersInHLayout.addWidget(self.RendersInTreeB)
        #TreeB_Buttons
        self.RendersInVLayoutB = QtGui.QVBoxLayout()
        RendersInTreeBBtns = [
            ["printFilePaths", self.printFilePaths],
            ["FrameCycler Render", self.sendRenderToFrameCycler],
            ["Remove Renders", self.remove3dRenders],
            ["omitSelectedRenders", self.setSelSeqsOmit],
            ["show dependencies", self.showDependencies],
            ["select highlighted", self.selectHighlighted],
        ]
        for btn in RendersInTreeBBtns:
            pushBtn = QtGui.QPushButton(self.bottomTab)
            pushBtn.setText(btn[0])
            pushBtn.clicked.connect(btn[1])
            self.RendersInVLayoutB.addWidget(pushBtn)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.RendersInVLayoutB.addItem(spacerItem)
        self.RendersInHLayout.addLayout(self.RendersInVLayoutB)

        
        #RendersOUT TAB
        self.RendersOutTab = QtGui.QWidget()
        self.RendersOutTab.setObjectName("RendersOutTab")
        self.RendersOutHLayout = QtGui.QHBoxLayout(self.RendersOutTab)
        #TreeA_Buttons
        self.RendersOutVLayoutA = QtGui.QVBoxLayout()
        RendersOutTreeABtns = [
            #["writeMovToDailies", self.writeToDailies],
            ["makeRenderCurrent", self.makeRenderOutCurrentSubprocess],
            #["expandTrees", self.expandTrees],
        ]
        for btn in RendersOutTreeABtns:
            pushBtn = QtGui.QPushButton(self.bottomTab)
            pushBtn.setText(btn[0])
            pushBtn.clicked.connect(btn[1])
            self.RendersOutVLayoutA.addWidget(pushBtn)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.RendersOutVLayoutA.addItem(spacerItem)
        self.RendersOutHLayout.addLayout(self.RendersOutVLayoutA)
        #NukeScriptRendersTree
        self.RendersOutTreeA = QtGui.QTreeWidget()
        self.RendersOutTreeA.setMinimumHeight(200)
        self.RendersOutTreeA.setObjectName("RendersOutTreeA")
        item=QtGui.QTreeWidgetItem()
        item.setText(0,"Renders in selected script:")
        self.RendersOutTreeA.setHeaderItem(item)
        self.RendersOutHLayout.addWidget(self.RendersOutTreeA)
        #ServerRendersTree
        self.RendersOutTreeB = QtGui.QTreeWidget()
        self.RendersOutTreeB.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.RendersOutTreeB.setObjectName("RendersOutTreeB")
        item=QtGui.QTreeWidgetItem()
        item.setText(0,"Renders in selected shot:")
        item.setText(1,"frames:")
        self.RendersOutTreeB.setHeaderItem(item)
        self.RendersOutTreeB.setColumnCount(2)
        self.RendersOutTreeB.resizeColumnToContents(0)
        self.RendersOutTreeB.resizeColumnToContents(1)
        self.RendersOutHLayout.addWidget(self.RendersOutTreeB)
        #TreeB_Buttons
        self.RendersOutVLayoutB = QtGui.QVBoxLayout()
        RendersOutTreeBBtns = [
            ["uploadThumbnail", self.uploadThumbnail],
            ["FrameCycler Render", self.sendRenderToFrameCycler],
            ["removeCompRenders", self.remove2dRenders],
            ["openInExplorer", self.openRenderDirectory],
            ["setVersionsClip",self.setVersionsClip],
        ]
        for btn in RendersOutTreeBBtns:
            pushBtn = QtGui.QPushButton(self.bottomTab)
            pushBtn.setText(btn[0])
            pushBtn.clicked.connect(btn[1])
            self.RendersOutVLayoutB.addWidget(pushBtn)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.RendersOutVLayoutB.addItem(spacerItem)
        self.RendersOutHLayout.addLayout(self.RendersOutVLayoutB)
        

        

        ###NOTES TAB
        self.notesTab = QtGui.QWidget()
        self.notesTab.setObjectName("notesTab")
        
        self.notesHLayout = QtGui.QHBoxLayout(self.notesTab)
        #Notes_ButtonsA
        self.notesButtonsAVLayout = QtGui.QVBoxLayout()
        self.notesHLayout.addLayout(self.notesButtonsAVLayout)
        notesBtnsA = [
            ["refreshShotgunNotes", self.getShotgunNotes],
            ["closeNote", self.closeNote],
        ]
        for btn in notesBtnsA:
            pushBtn = QtGui.QPushButton(self.bottomTab)
            pushBtn.setText(btn[0])
            pushBtn.clicked.connect(btn[1])
            self.notesButtonsAVLayout.addWidget(pushBtn)
            
        self.notesShowCompOnlyChbox= QtGui.QCheckBox(self.notesTab)
        self.notesShowCompOnlyChbox.setText("show Comp only")
        self.notesShowCompOnlyChbox.setChecked(True)
        self.notesButtonsAVLayout.addWidget(self.notesShowCompOnlyChbox)
        self.notesShowClosedChbox= QtGui.QCheckBox(self.notesTab)
        self.notesShowClosedChbox.setText("hide Closed")
        self.notesShowClosedChbox.setChecked(True)
        self.notesButtonsAVLayout.addWidget(self.notesShowClosedChbox)
        #spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.notesButtonsAVLayout.addItem(spacerItem)
        #notesTable
        self.notesTable = QtGui.QTableWidget(self.notesTab)
        self.notesTable.setObjectName("notesTable")
        self.notesTable.verticalHeader().hide()
        #self.notesTable.horizontalHeader().hide()
        self.notesTable.setColumnCount(6)
        item = QtGui.QTableWidgetItem()
        item.setText("Note")
        self.notesTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        item.setText("Status")
        self.notesTable.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        item.setText("Author")
        self.notesTable.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        item.setText("Task")
        self.notesTable.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        item.setText("DateCreated")
        self.notesTable.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        item.setText("id")
        self.notesTable.setHorizontalHeaderItem(5, item)
        self.notesTable.setAlternatingRowColors(True)
        self.notesTable.setSortingEnabled(True)
        self.notesTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.notesTable.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.notesTable.horizontalHeader().setStretchLastSection(1) 
        self.notesTable.horizontalHeader().resizeSection(0, 300)
        self.notesHLayout.addWidget(self.notesTable)
        #notesTextEdit
        self.notesTextEdit = QtGui.QTextEdit(self.notesTab)
        self.notesTextEdit.setObjectName("notesTextEdit")
        self.notesHLayout.addWidget(self.notesTextEdit)
        #Notes_ButtonsB
        self.notesButtonsBVLayout = QtGui.QVBoxLayout()
        self.notesHLayout.addLayout(self.notesButtonsBVLayout)
        self.sendTaskCombo = QtGui.QComboBox(self.notesTab)
        self.sendTaskCombo.setObjectName("sendTask")
        self.notesButtonsBVLayout.addWidget(self.sendTaskCombo)
        notesBtnsB = [
            #["writeMovToDailies", self.writeToDailies],
            ["createShotgunNote", self.createShotgunNote],
            #["expandTrees", self.expandTrees],
        ]
        for btn in notesBtnsB:
            pushBtn = QtGui.QPushButton(self.bottomTab)
            pushBtn.setText(btn[0])
            pushBtn.clicked.connect(btn[1])
            self.notesButtonsBVLayout.addWidget(pushBtn)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.notesButtonsBVLayout.addItem(spacerItem)

        
        
        ###add tabs
        self.bottomTab.addTab(self.RendersInTab,"Renders_In")
        self.bottomTab.addTab(self.RendersOutTab,"Renders_Out")
        self.bottomTab.addTab(self.notesTab,"Notes")
        
        self.mainGridLayout.addWidget(self.vSplitter, 0, 0, 1, 1)

        #init definitions
        self.setupSignals()
        self.setupSequenceComboBox()
        self.selectTab()
        self.shotgunNotes=self.initializeNotes()
        self.shotgunShotData=self.initializeShotData()
        self.shotgunPublishes=self.initializePublishes()
        self.tableShots()

    def setupSignals(self,*args):
        import tank
        PROJECT_ID=tank.platform.current_engine().context.project['id']

        self.filesList.itemSelectionChanged.connect(self.selectScript)
        self.fileFilter.textChanged.connect(self.updateFileFilter)
        self.shotTable.itemSelectionChanged.connect(self.selectShot)
        self.shotTable.itemChanged.connect(self.updateprojectData)
        
        self.seqSelection.currentIndexChanged.connect(self.changeSequence)
        self.RendersInTreeB.itemSelectionChanged.connect(self.expandServerTree)
        self.RendersOutTreeB.itemSelectionChanged.connect(self.expandServerTree)
        #self.bottomTab.currentChanged.connect(self.buildTreeB)
        self.bottomTab.currentChanged.connect(self.selectTab)
        self.notesTable.itemSelectionChanged.connect(self.showNotesText)
        self.notesShowCompOnlyChbox.clicked.connect(self.updateNotesTable)
        self.notesShowClosedChbox.clicked.connect(self.updateNotesTable)
        
        #self.notesBtn1.clicked.connect(self.closeNotes)
        #self.sendNotesBtn.clicked.connect(self.createShotgunNote)
        
    ###Task Menubar functions
    def updateTime(self,*args):
        import time,datetime
        timeText=str(time.ctime(os.path.getmtime(self.publishRendersData)))
        self.updatedText.setText("last updated:\n"+timeText[:-5])
    
    def refreshTable(self,*args):
        try:
            self.shotgunShotData=self.getShotgunData()
        except:
            pass
        self.shotgunPublishes=self.getShotgunPublishes()
        self.tableShots()
        self.updateSequenceNofications() 

    def submitShot(self,*args):
        if self.selShot and self.selScript:
            nukeFile=self.nukeScriptsPath+"/"+self.selScript
            writes=self.getWriteNames()
            p = nuke.Panel('selectWrites')
            for wr in writes:
                p.addBooleanCheckBox(wr, False)
            ret = p.show()
            if ret:
                for wr in writes:
                    if p.value(wr):
                        qubeMethods.submitToQube(nukeFile,wr,1,1)

    def submitSequence(self,*args):
        task = nuke.ProgressTask('submitting sequence shots')
        for r in range(self.shotTable.rowCount()):
            shot=self.shotTable.item(r,0).text()
            task.setMessage( 'shot:' + shot)
            nukeFiles=[]
            if os.path.exists(self.template_nukeScriptPath.replace("shotNum",shot)):
                scriptFiles=os.listdir(self.template_nukeScriptPath.replace("shotNum",shot))
                for sfile in scriptFiles:
                    if sfile.endswith(".nk") and self.fileFilterText in sfile:
                        nukeFiles.append(self.template_nukeScriptPath.replace("shotNum",shot)+"/"+sfile)
                if len(nukeFiles)>0:                  
                    #select latest project file
                    nukeFile=self.getLatestFile(nukeFiles)
                    qubeMethods.submitToQube(nukeFile,'comp',1,1)
            task.setProgress( int( float(r) / float(self.shotTable.rowCount()) *100) )
        del(task)

    def createRvConform(self,*args):
        print sgMethods.getShotgunFramerange(PROJECT_ID,self.selShot)

    def clearSequenceAlerts(self,*args):
        self.updateSequenceNofications()
        
        
        
    ###SequenceComboBox
    def setupSequenceComboBox(self,*args):
        availSequences=[]
        existingSequences=os.listdir(self.seqDir)
        for seq in existingSequences:
            if os.path.exists(self.seqDir+'/'+seq):
                availSequences.append(seq)
        for seq in availSequences:
            self.seqSelection.addItem(seq)
        self.setCurrentSequence()

    def setCurrentSequence(self,*args):
        self.seqSelection.setCurrentIndex(int(self.recentSeq))
        currentSeq=self.seqSelection.currentText()
        self.shotDir=self.seqDir+'/sequenceName'.replace('sequenceName',self.seqSelection.currentText())
        self.template_nukeScriptPath=self.shotDir+'/shotNum/composite/work/nuke'

    def changeSequence(self,*args):
        currentSeq=self.seqSelection.currentText()
        self.shotDir=self.seqDir+'/sequenceName'.replace('sequenceName',self.seqSelection.currentText())
        self.template_nukeScriptPath=self.shotDir+'/shotNum/composite/work/nuke'
        self.template_3dPath=self.shotDir+'/shotNum/lighting/output/render'
        self.template_2dPath=self.shotDir+'/shotNum/composite/output/render'
        self.searchDir2D=self.template_2dPath.replace("shotNum",self.selShot)
        self.searchDir3D=self.template_3dPath.replace("shotNum",self.selShot)
        self.selShot=""
        self.selScript=""
        self.tableShots()
        if not self.recentSeq==currentSeq:
            self.writeUserData()

        
    ###PROJECT TABLE FUNCTIONS
    
    def selectShot(self,*args):
        self.selShot=self.shotTable.selectedItems()[0].text()
        self.selScript=""
        self.searchDir2D=self.template_2dPath.replace("shotNum",self.selShot)
        self.searchDir3D=self.template_3dPath.replace("shotNum",self.selShot)
        self.nukeScriptsPath=self.template_nukeScriptPath.replace("shotNum",self.selShot)
        self.updateShotThumbnail()
        self.listNukeFiles()
        self.RendersInTreeA.clear()
        self.RendersOutTreeA.clear()
        self.buildTreeB()
        if self.bottomTab.currentWidget().objectName()=="notesTab":
            self.updateNotesTable()
        if self.bottomTab.currentWidget().objectName()=="qubeTab":
            self.findQubeItems()
        if self.bottomTab.currentWidget().objectName()=="assetsTab":
            self.showShotAssets()

        #latestItem= self.filesList.findItems(latestFile,QtCore.Qt.MatchFlags(QtCore.Qt.MatchContains))[0]
        #self.filesList.setCurrentItem(self.filesList.item(0))
        #self.compareRenders()
        #self.compareRenders()
        
    def updateFileFilter(self,*args):
        print "test"
        print self.fileFilter.text()
        self.fileFilterText=self.fileFilter.text()
    
    def tableShots(self,*args):
        self.updateTime()
        self.shotsTableListen=False
        shots=self.getValidShots()
        shots.sort()

        data=self.getprojectData()

        for c in range(self.shotTable.columnCount())[6:]:
            self.shotTable.removeColumn(self.shotTable.columnCount()-1)  
        for r in range(self.shotTable.rowCount()):
            self.shotTable.removeRow(0)   

        #add columns from self.projectData
        if data:
            for newCol in data['headers']:
                if not newCol == "":
                    self.shotTable.setColumnCount(self.shotTable.columnCount()+1)
                    item = QtGui.QTableWidgetItem()
                    item.setText(newCol)
                    self.shotTable.setHorizontalHeaderItem(self.shotTable.columnCount()-1, item)

        #add shots from shot folder
        for i,shot in enumerate(shots):
            rowNum=self.shotTable.rowCount()
            self.shotTable.insertRow(rowNum)
            self.shotTable.setRowHeight(rowNum, 15)
            item=QtGui.QTableWidgetItem()
            item.setText(shot)
            self.shotTable.setItem(i,0,item)

            if shot in self.shotgunShotData.keys():
                print shot
                #assigned
                assigned=self.shotgunShotData[shot]['tasks']['comp']['users'][0].split(":")[0]
                if assigned:
                    item=QtGui.QTableWidgetItem()
                    item.setText(assigned)
                    self.shotTable.setItem(i,1,item)
                    
                #compStatus
                item=QtGui.QTableWidgetItem()
                if 'comp' in self.shotgunShotData[shot]['tasks'].keys():
                    status=self.shotgunShotData[shot]['tasks']['comp']['status']
                    item.setText(status)
                    if status in self.statusColor.keys():
                        item.setBackground(self.statusColor[status])
                self.shotTable.setItem(i,2,item)
                #lightStatus
                item=QtGui.QTableWidgetItem()
                if 'lighting' in self.shotgunShotData[shot]['tasks'].keys():
                    status=self.shotgunShotData[shot]['tasks']['lighting']['status']
                    item.setText(status)
                    if status in self.statusColor.keys():
                        item.setBackground(self.statusColor[status])
                self.shotTable.setItem(i,3,item)
                

            
            
            #apply userProject data per shot
            if shot in data.keys():
                shotData=data[shot].split(',')[1:]
                for c in range(len(shotData)):
                    item=QtGui.QTableWidgetItem()
                    item.setText(shotData[c])
                    if "update" in item.text() and c==0:
                        color=QtGui.QColor(200,0,0)
                        item.setBackground(color)
                    self.shotTable.setItem(i,c+4,item)
            if shot in self.shotgunNotes.keys():
                #count comp notes
                noteCount=0
                for note in self.shotgunNotes[shot]:
                    columns=note.split("<,>")
                    status=columns[2]
                    task=columns[4]
                    if status=='opn' and 'comp' in task:
                        noteCount+=1
                #count number of notes in shotgun
                if noteCount>0:
                    color=QtGui.QColor(0,0,200)
                    noteItem=QtGui.QTableWidgetItem()
                    noteItem.setBackground(color)
                    noteItem.setText(str(noteCount))
                    self.shotTable.setItem(i,5,noteItem)
                

        #self.shotTable.sortItems(0,QtCore.Qt.AscendingOrder)
        self.shotsTableListen=True
        #self.updateSequenceNofications()    

    def getValidShots(self,*args):
        shots=[]
        for shot in os.listdir(self.shotDir):
            #add shot if nuke files found in shot directory
            shotFiles= self.template_nukeScriptPath.replace("shotNum",shot)
            if os.path.exists(shotFiles):
                for sf in os.listdir(shotFiles):
                    if self.fileFilterText in sf and not shot in shots:
                        shots.append(shot)
        return shots

    
        
    def createAssetsTab(self,*args):
        ###Assets TAB
        self.AssetsTab = QtGui.QWidget()
        self.AssetsTab.setObjectName("assetsTab")

        #Assets Layout
        self.AssetshorizontalLayout = QtGui.QHBoxLayout(self.AssetsTab)
        self.AssetshorizontalLayout.setObjectName("AssetshorizontalLayout")


        #AssetsTable
        self.AssetsTable = QtGui.QTableWidget(self.AssetsTab)
        self.AssetsTable.setObjectName("AssetsTable")
        self.AssetsTable.verticalHeader().hide()
        #self.AssetsTable.horizontalHeader().hide()
        self.AssetsTable.setColumnCount(2)
        item = QtGui.QTableWidgetItem()
        item.setText("name")
        self.AssetsTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()

        self.AssetsTable.setAlternatingRowColors(True)
        self.AssetsTable.setSortingEnabled(True)
        self.AssetsTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.AssetsTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.AssetsTable.horizontalHeader().stretchLastSection() 
        self.AssetshorizontalLayout.addWidget(self.AssetsTable)   
        self.getAssetData()
        self.bottomTab.addTab(self.AssetsTab,"assetsTab")
        self.tabs.append("assetsTab")
        self.bottomTab.setCurrentIndex(self.tabs.index("assetsTab"))
        
    def getAssetData(self,*args):
        import tank
        import shotgun_api3 as shotgun
        SERVER_PATH = "https://psyop.shotgunstudio.com"
        SCRIPT_USER = "mlTools"
        SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
        sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
        # Get handle to Asset Manager tank application
        assetmgr = tank.platform.current_engine().apps["tk-multi-assetmanager"]
        PROJECT_ID=tank.platform.current_engine().context.project['id']

        # Grab updated publish data from shotgun
        publish_directory = assetmgr.publish_directory
        publish_directory.update(async=False)

        for shot in self.getValidShots():
            sgShot=shot[:3]+"_"+shot[3:]
            print sgShot
            fields = ['id', 'code', 'sg_status_list']
            filters = [['project','is', {'type':'Project','id':PROJECT_ID}],['code', 'is',sgShot]]
            entity = sg.find_one('Shot',filters,fields)
            try:
                # Iterate over each published lighting render layer for the shot
                sgAssets = publish_directory.find_publish_type(entity, "cache/animation")
                shotAssets=[]
                for asset in sgAssets.components:
                    shotAssets.append(asset.component_name)
                if not shot in self.shotgunAssetData.keys():
                    self.shotgunAssetData[shot]=[]
                self.shotgunAssetData[shot]=shotAssets
            except:
                pass
        print self.shotgunAssetData

    def showShotAssets(self,*args):
        for r in range(self.AssetsTable.rowCount()):
            self.AssetsTable.removeRow(0) 
        if self.selShot in self.shotgunAssetData.keys():
            assets=self.shotgunAssetData[self.selShot]
            assets.sort()
            for asset in assets:
                rowNum=self.AssetsTable.rowCount()
                self.AssetsTable.insertRow(rowNum)
                self.AssetsTable.setRowHeight(rowNum, 15)
                #set itemName
                item=QtGui.QTableWidgetItem()
                item.setText(asset)
                self.AssetsTable.setItem(rowNum,0,item)
                #set itemStatus
                #item=QtGui.QTableWidgetItem()
                #item.setText(qubeJob['status'])
                #self.qubeTable.setItem(rowNum,1,item)
        
    def createQubeTab(self,*args):
        ###QUBE TAB
        self.QubeTab = QtGui.QWidget()
        self.QubeTab.setObjectName("qubeTab")
        self.bottomTab.addTab(self.QubeTab,"QubeStatus")
        self.tabs.append("qubeTab")

        #qube Layout
        self.qubehorizontalLayout = QtGui.QHBoxLayout(self.QubeTab)
        self.qubehorizontalLayout.setObjectName("qubehorizontalLayout")
        self.qubeButtonsVLayout = QtGui.QVBoxLayout()
        self.qubehorizontalLayout.addLayout(self.qubeButtonsVLayout)

        #dateTimeEdit
        self.qubeDateTimeEdit= QtGui.QDateTimeEdit(self.QubeTab)
        now = QtCore.QDateTime.currentDateTime()
        yesterday=now.addDays(-1)
        yesterday.setTime(QtCore.QTime(17, 00))#set 5pm
        self.qubeDateTimeEdit.setDateTime(yesterday)
        self.qubeButtonsVLayout.addWidget(self.qubeDateTimeEdit)

        qubeBtns = [
            ["refresh", self.getQubeStatus],
            #["findShotItems", self.findQubeItems],
        ]
        for btn in qubeBtns:
            pushBtn = QtGui.QPushButton(self.QubeTab)
            pushBtn.setText(btn[0])
            pushBtn.clicked.connect(btn[1])
            self.qubeButtonsVLayout.addWidget(pushBtn)

        self.qubeGroupCombo = QtGui.QComboBox(self.QubeTab)
        self.qubeGroupCombo.addItems(["maya","houdini"])
        self.qubeButtonsVLayout.addWidget(self.qubeGroupCombo)
            
        self.qubeShotChbox= QtGui.QCheckBox(self.QubeTab)
        self.qubeShotChbox.setText("hideOtherShots")
        self.qubeShotChbox.setChecked(True)
        self.qubeButtonsVLayout.addWidget(self.qubeShotChbox)
        self.qubeCompleteChbox= QtGui.QCheckBox(self.QubeTab)
        self.qubeCompleteChbox.setText("hideCompleted")
        self.qubeCompleteChbox.setChecked(False)
        self.qubeButtonsVLayout.addWidget(self.qubeCompleteChbox)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.qubeButtonsVLayout.addItem(spacerItem)
        #qubeTable
        self.qubeTable = QtGui.QTableWidget(self.QubeTab)
        self.qubeTable.setObjectName("qubeTable")
        self.qubeTable.verticalHeader().hide()
        #self.qubeTable.horizontalHeader().hide()
        self.qubeTable.setColumnCount(4)
        item = QtGui.QTableWidgetItem()
        item.setText("name")
        self.qubeTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        item.setText("status")
        self.qubeTable.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        item.setText("progress")
        self.qubeTable.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        item.setText("timeCompleted")
        self.qubeTable.setHorizontalHeaderItem(3, item)

        self.qubeTable.setAlternatingRowColors(True)
        self.qubeTable.setSortingEnabled(True)
        self.qubeTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.qubeTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.qubeTable.horizontalHeader().stretchLastSection() 
        self.qubehorizontalLayout.addWidget(self.qubeTable)        
        
        #self.showQubeStatus()

        self.qubeShotChbox.clicked.connect(self.findQubeItems)
        self.qubeCompleteChbox.clicked.connect(self.findQubeItems)
        self.qubeGroupCombo.currentIndexChanged.connect(self.findQubeItems)
        self.qubeDateTimeEdit.dateTimeChanged.connect(self.showDateTime)
        self.bottomTab.setCurrentIndex(self.tabs.index("qubeTab"))

        
    def showQubeStatus(self,*args):
        import datetime
        self.getQubeStatus()
        #add qubeStatus column
        self.shotTable.setColumnCount(self.shotTable.columnCount()+1)
        item = QtGui.QTableWidgetItem()
        item.setText('qubeStatus')
        self.shotTable.setHorizontalHeaderItem(self.shotTable.columnCount()-1, item) 
        
        for r in range(self.shotTable.rowCount()):
            shot=self.shotTable.item(r,0).text()
            runningFound=0
            mostRecent=0
            for k in self.qubeStatus.keys():
                if shot in k:
                    if 'running' in self.qubeStatus[k]['status']:
                        runningFound=1
                    if 'complete' in self.qubeStatus[k]['status']:
                        if self.qubeStatus[k]['timecomplete']>mostRecent:
                            mostRecent=self.qubeStatus[k]['timecomplete']
                            
            item=QtGui.QTableWidgetItem()
            if mostRecent:
                date = datetime.datetime.fromtimestamp(mostRecent)
                item.setText('Completed:'+date.strftime("%m/%d %I:%M%p"))
            if runningFound:
                item.setText('Running')
            self.shotTable.setItem(r,self.shotTable.columnCount()-1,item) 
            
    def getQubeStatus(self,*args):
        currentJob=projectName
        currentSeq=self.seqSelection.currentText()
        import sys
        sys.path.append("C:\\Program Files\\pfx\\qube\\api\\python\\")
        import qb
        jobinfo = qb.jobinfo(fields=['name'], filters={'groups':['maya', 'houdini'],'cluster':['/3D/'+currentJob]})
        for j in jobinfo:
            name= j['name']
            id=j['id']
            job=name.split('/')[0]
            seq,shot=name.split(job+'/')[-1].split(': ')
            if not id in self.qubeStatus.keys():
                self.qubeStatus[id]={}
                self.qubeStatus[id]['name']=shot
                self.qubeStatus[id]['seq']=seq
                self.qubeStatus[id]['status']=j['status']
                self.qubeStatus[id]['todo']=j['todo']
                self.qubeStatus[id]['todotally']=j['todotally']
                self.qubeStatus[id]['timecomplete']=j['timecomplete']
                self.qubeStatus[id]['groups']=j['groups']

        self.findQubeItems()

    def showDateTime(self,*args):
        print self.qubeDateTimeEdit.dateTime()
        print self.qubeDateTimeEdit.dateTime().toPython()
        self.findQubeItems()
        
    def findQubeItems(self,*args):
        import datetime
        self.qubeTable.setSortingEnabled(False)
        omit=['killed','failed','blocked']
        if self.qubeCompleteChbox.isChecked():
            omit.append('complete')
        #reset table
        for r in range(self.qubeTable.rowCount()):
            self.qubeTable.removeRow(0) 

        for k in self.qubeStatus.keys():
            qubeJob=self.qubeStatus[k]
            if self.seqSelection.currentText() in qubeJob['seq']:
                if not qubeJob['status'] in omit:
                    if self.qubeGroupCombo.currentText() in qubeJob['groups']:
                        if not self.qubeShotChbox.checkState() or self.selShot in qubeJob['name']:
                            if datetime.datetime.fromtimestamp(qubeJob['timecomplete']) > self.qubeDateTimeEdit.dateTime().toPython() or qubeJob['timecomplete']==946702800:
                                self.qubeDateTimeEdit.dateTime().toPython()
                                rowNum=self.qubeTable.rowCount()
                                self.qubeTable.insertRow(rowNum)
                                self.qubeTable.setRowHeight(rowNum, 15)
                                #set itemName
                                item=QtGui.QTableWidgetItem()
                                item.setText(qubeJob['name'])
                                self.qubeTable.setItem(rowNum,0,item)
                                #set itemStatus
                                item=QtGui.QTableWidgetItem()
                                item.setText(qubeJob['status'])
                                self.qubeTable.setItem(rowNum,1,item)
                                #set percentage
                                item=QtGui.QTableWidgetItem()
                                progBar=QtGui.QProgressBar()
                                progBar.setMaximum(int(qubeJob['todo']))
                                
                                progBar.setValue(int(qubeJob['todotally']['complete']))
                                #item.addWidget(progBar)
                                #item.setText(str(qubeJob['todo']))
                                self.qubeTable.setCellWidget(rowNum,2,progBar)
                                if qubeJob['status']=='complete':
                                    #set complete time
                                    item=QtGui.QTableWidgetItem()
                                    date = datetime.datetime.fromtimestamp(qubeJob['timecomplete'])
                                    item.setText(date.strftime("%m/%d %I:%M%p"))
                                    self.qubeTable.setItem(rowNum,3,item)
        self.qubeTable.setSortingEnabled(True)
                
    def updateAllShotThumbnails(self,*args):
        for s in range(self.seqSelection.count()):
            task = nuke.ProgressTask('finding exrs')
            self.seqSelection.setCurrentIndex(s)
            self.changeSequence()
            for r in range(self.shotTable.rowCount()):
                shot=self.shotTable.item(r,0).text()
                self.shotDir=self.seqDir+'/sequenceName'.replace('sequenceName',self.seqSelection.currentText())
                self.template_2dPath=self.shotDir+'/shotNum/composite/output/render'.replace('shotNum',shot)
                print shot
                treeSel=self.RendersOutTreeB
                self.selShot=shot
                self.buildTreeB()
                versions=[]
                for c in range(treeSel.topLevelItemCount()):
                    compVersion= treeSel.topLevelItem(c).text(0)
                    if 'composite' in compVersion:
                        regex = re.compile("v[0-9]{2,9}")
                        vers=regex.findall(compVersion)[0]
                        versions.append(vers)
                if versions:
                    latest=max(versions)
                    import math
                    path=self.template_2dPath+'/'+shot+'_composite_'+latest+'/comp/exr/'
                    files= nuke.getFileNameList(path)
                    print files
                    if files:
                        try:
                            filename,frames=files[0].split(' ')
                            first,last=frames.split('-')
                            mid=str(int(math.floor((float(first)+float(last))/2))).zfill(4)
                            thumbpath=path+'/'+filename.replace('####',mid)

                            
                            #write to thumbsdir
                            nuke.selectAll() 
                            nuke.invertSelection() 
                            thumbsDir=self.thumbsPath
                            frm=nuke.frame()
                            read=nuke.nodes.Read()
                            read['file'].setValue(thumbpath)
                            
                            rf=nuke.nodes.Reformat()
                            rf.setInput(0,read)
                            rf['type'].setValue(1)
                            rf['box_width'].setValue(256)
                            rf['box_height'].setValue(144)
                            rf['box_fixed'].setValue(1)
                            #rf['scale'].setValue(.2)

                            w=nuke.nodes.Write()
                            w.setInput(0,rf)
                            w['file'].setValue(thumbsDir+'/'+shot+'.jpg')
                            w['views'].setValue(nuke.views()[0])
                            w['file_type'].setValue('jpeg')
                            #w['colorspace'].setValue('sRGB')
                            nuke.execute(w,frm,frm)

                            nuke.delete(w)
                            nuke.delete(rf)
                            nuke.delete(read)

                            #upload to SG
                            sgMethods.uploadThumbnail(PROJECT_ID,shot,thumbsDir+'/'+shot+'.jpg')
                        except:
                            pass
                    
          
    def removeRendersData(self,*args):
        self.bottomTab.setCurrentIndex(0)
        for s in range(self.seqSelection.count()):
            self.seqSelection.setCurrentIndex(s)
            self.changeSequence()
            for r in range(self.shotTable.rowCount()):
                if os.path.exists(self.nukeScriptsPath):
                    publishFile=self.nukeScriptsPath+"/rendersData.txt"  
                    os.remove(publishFile)

    def floodComps(self,*args):
        self.bottomTab.setCurrentIndex(0)
        for s in range(self.seqSelection.count()):
            self.seqSelection.setCurrentIndex(s)
            self.changeSequence()
            self.shotDir=self.seqDir+'/sequenceName'.replace('sequenceName',self.seqSelection.currentText())
            for shot in os.listdir(self.shotDir):
                self.template_2dPath=self.shotDir+'/shotNum/composite/work/nuke'.replace('shotNum',shot)
                compFile=self.template_2dPath+"/"+shot+"_comp_v001.nk"
                if os.path.exists(self.template_2dPath):
                    if not os.path.exists(compFile):
                        fileObject=open(compFile,"w")
                        fileObject.write("Root {"+"\n"+" name "+compFile+"\n"+"}")
                        fileObject.close() 
                        print "created", compFile
    def findAllShotsNewRenders_all(self,*args):
        self.bottomTab.setCurrentIndex(0)
        for s in range(self.seqSelection.count()):
            task = nuke.ProgressTask('finding exrs')
            self.seqSelection.setCurrentIndex(s)
            self.changeSequence()
            for r in range(self.shotTable.rowCount()):
                shot=self.shotTable.item(r,0).text()
                task.setMessage( 'processing shot:' + shot)
                task.setProgress( int( float(r) / float(self.shotTable.rowCount()) *100) )
                self.updatePublishedFileForSelectedShot(shot) 
            del(task)
            self.updateSequenceNofications()

    def findAllShotsNewRenders_thisSequence(self,*args):
        self.bottomTab.setCurrentIndex(0)
        task = nuke.ProgressTask('finding exrs')
        for r in range(self.shotTable.rowCount()):
            shot=self.shotTable.item(r,0).text()
            task.setMessage( 'processing shot:' + shot)
            task.setProgress( int( float(r) / float(self.shotTable.rowCount()) *100) )
            self.updatePublishedFileForSelectedShot(shot) 
        del(task)
        self.updateSequenceNofications()
            
    def statusReport(self,*args):
        report={}

        taskWin = nuke.ProgressTask('updating table')
        for r in range(self.shotTable.rowCount()):
            self.shotTable.setCurrentCell(r,0)
            taskWin.setMessage( 'shot:' + self.selShot)
            
            notes=[]
            if self.selShot in self.shotgunNotes.keys():
                for note in self.shotgunNotes[self.selShot]:
                    columns=note.split("<,>")
                    noteText=columns[1]
                    status=columns[2]
                    task=columns[4]
                    if status=="opn" and "comp" in task:
                        notes.append(noteText)
                
                #get new renders
                nukeFiles=[]
                if os.path.exists(self.template_nukeScriptPath.replace("shotNum",self.selShot)):
                    scriptFiles=os.listdir(self.template_nukeScriptPath.replace("shotNum",self.selShot))
                    for sfile in scriptFiles:
                        if sfile.endswith(".nk") and self.fileFilterText in sfile:
                            nukeFiles.append(self.template_nukeScriptPath.replace("shotNum",self.selShot)+"/"+sfile)
                    if len(nukeFiles)>0:                  
                        #select latest project file
                        latest=self.getLatestFile(nukeFiles)
                        self.selScript=latest.split("/")[-1]
                        self.buildTreeB()
                        self.resetTreeBColors()
                        self.buildTreeA()
                        found,renderLayers=self.compareRenders()
                        if found:
                            notes.append("update Renders: "+",".join(renderLayers))
                        
                user=self.shotTable.item(r,1)
                if user:
                    user=user.text()
                    if user=='':
                        user='unassigned'
                    if not user in report.keys():
                        report[user]={}
                    report[user][self.selShot]=notes
            
            taskWin.setProgress( int( float(r) / float(self.shotTable.rowCount()) *100) )
        del(taskWin)      
        print report
        

        reportMessage=''
        fileObject=open('Z:/.nuke/shotTasks.txt',"w")
        for userName in report.keys():
            #reportMessage+=userName+'\n'
            fileObject.write(userName+'\n')
            userKeys=report[userName].keys()
            userKeys.sort()
            for shot in userKeys:
                #reportMessage+='\t'+shot+'\n\t\t'
                if len(report[userName][shot]):
                    fileObject.write('\t'+shot+'\n\t\t')
                    renders=report[userName][shot]
                    #print renders
                    #reportMessage+='\n\t\t'.join(renders)+'\n'
                    fileObject.write('\n\t\t'.join(renders)+'\n')
            #reportMessage+='\n'
            fileObject.write('\n')
        #nuke.message(reportMessage)
        fileObject.close()
        
    def updateSequenceNofications(self,*args):
        self.bottomTab.setCurrentIndex(0)
        task = nuke.ProgressTask('updating table')
        for r in range(self.shotTable.rowCount()):
            self.shotTable.setCurrentCell(r,0)
            task.setMessage( 'shot:' + self.selShot)
            nukeFiles=[]
            if os.path.exists(self.template_nukeScriptPath.replace("shotNum",self.selShot)):
                scriptFiles=os.listdir(self.template_nukeScriptPath.replace("shotNum",self.selShot))
                for sfile in scriptFiles:
                    if sfile.endswith(".nk") and self.fileFilterText in sfile:
                        nukeFiles.append(self.template_nukeScriptPath.replace("shotNum",self.selShot)+"/"+sfile)
                if len(nukeFiles)>0:                  
                    #select latest project file
                    latest=self.getLatestFile(nukeFiles)
                    self.selScript=latest.split("/")[-1]
                    self.buildTreeB()
                    self.resetTreeBColors()
                    self.buildTreeA()
                    found,renderLayers=self.compareRenders()
                    if found:
                        color=QtGui.QColor(200,0,0)
                        item=QtGui.QTableWidgetItem()
                        item.setBackground(color)
                        item.setText("update "+str(len(renderLayers)))
                        self.shotTable.setItem(r,4,item)
                    if not found:
                        item=QtGui.QTableWidgetItem()
                        self.shotTable.setItem(r,4,item)
            task.setProgress( int( float(r) / float(self.shotTable.rowCount()) *100) )
        del(task)
        
            
    def getLatestFile(self,nukeFiles,*args):
        latest=""
        timeVal=0.0
        for nk in nukeFiles:
            dirModTime=os.path.getmtime(nk)
            if dirModTime>timeVal:
                if 'composite' in nk:
                    latest=nk
                    timeVal=dirModTime
        return latest
        
    def updateprojectData(self,*args):
        if self.shotsTableListen:
            self.writeprojectData()
   
   
    def writeprojectData(self,*args):
        ignoreHeaders=['qubeStatus','compSize','lightingSize','Notes']
        shotSequence=self.shotDir.split('/')[-1]
        fileObject=open(self.projectData,"r")
        contents=fileObject.read()
        fileObject.close()
        seqStrings=contents.split("\n")
        for seqString in seqStrings:
            if seqString.startswith(shotSequence):
                seqStrings.remove(seqString)
        
        #print seqStrings
        #write custom columns
        extraColumns=[]
        seqData={}
        
        msg=''
        for c in range(self.shotTable.columnCount())[5:]:
            headerLabel=str(self.shotTable.horizontalHeaderItem(c).text())
	    if not headerLabel in ignoreHeaders:
		extraColumns.append(headerLabel)

        seqData['headers']=extraColumns
        #write shots data
        for r in range(self.shotTable.rowCount()):
            shotName=str(self.shotTable.item(r,0).text())
            shotData=[shotName]
            for c in range(self.shotTable.columnCount())[4:]:
                item=self.shotTable.item(r,c)
                data=""
                if self.shotTable.item(r,c) is not None:
                    data=str(item.text())
                shotData.append(data)
                
            seqData[shotName]=",".join(shotData)
        
        seqStrings.append(shotSequence+'###'+str(seqData))
        fileObject=open(self.projectData,"w")  
        fileObject.write("\n".join(seqStrings))
        fileObject.close()

    def getUserData(self,*args):
        import socket
        hostName=socket.gethostname()
        if not os.path.exists(self.userData):
            fileObject=open(self.userData,"w")
            fileObject.close()
        fileObject=open(self.userData,"r")
        contents=fileObject.read()
        fileObject.close()
        userSeqs=contents.split("\n")
        recentSequence='0'
        for seq in userSeqs:
            if hostName in seq:
                recentSequence=seq.split('###')[-1]
        return recentSequence

    def updateShotAssigns(self,*args):
        import tank
        PROJECT_ID=tank.platform.current_engine().context.project['id']
        import shotgun_api3 as shotgun
        SERVER_PATH = "https://psyop.shotgunstudio.com"
        SCRIPT_USER = "mlTools"
        SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
        sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
            
        for r in range(self.shotTable.rowCount()):
            shot=str(self.shotTable.item(r,0).text())
            userName=''
            if self.shotTable.item(r,1):
                userName=str(self.shotTable.item(r,1).text())

            fields = ['id', 'name','login']
            filters = [['name', 'is',userName]]
            userReturn = sg.find_one('HumanUser',filters,fields)
            if userReturn:
                print userReturn,'found'
                if shot in self.shotgunShotData.keys():
                    if self.shotgunShotData[shot]['tasks']['comp']['users'][0].split(":")[0]!=userName:
                        taskId=self.shotgunShotData[shot]['tasks']['comp']['id']
                        sg.update('Task', int(taskId), {'task_assignees': [userReturn]})
                        
    def writeUserData(self,*args):
        import socket
        hostName=socket.gethostname()
        currentIdx=str(self.seqSelection.currentIndex())
        fileObject=open(self.userData,"r")
        contents=fileObject.read()
        fileObject.close()
        userSeqs=contents.split("\n")
        found=0
        for i,seq in enumerate(userSeqs):
            if hostName in seq:
                userSeqs[i]=hostName+'###'+currentIdx
                found=1
        if not found:
            userSeqs.append(hostName+'###'+currentIdx)
        fileObject=open(self.userData,"w")  
        fileObject.write("\n".join(userSeqs))
        fileObject.close()

    def writeLightingProgress(self,*args):
        seq=self.seqSelection.currentText()
        fileObject=open(self.lightingData,"r")
        contents=fileObject.read()
        fileObject.close()
        seqStrings=contents.split("\n")
        for seqString in seqStrings:
            if seqString.startswith(seq):
                seqStrings.remove(seqString)

        import shotgun_api3 as shotgun
        SERVER_PATH = "https://psyop.shotgunstudio.com"
        SCRIPT_USER = "mlTools"
        SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
        sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

        #get shot
        fields = ['id', 'code','shots']
        filters = [['project','is', {'type':'Project','id':PROJECT_ID}],['code', 'is',seq]]
        sq = sg.find_one('Sequence',filters,fields)
        seqData={}
        
        task = nuke.ProgressTask("updatingLighting")
        
                
        for i,shot in enumerate(sq['shots']):
            task.setMessage( 'processing %s' % shot['name'])
            task.setProgress( int( float(i) / len(sq['shots']) *100) )
            #get tasks
            fields = ['id', 'code', 'sg_status_list']
            filters = [ ['entity','is',{'type':'Shot','id':shot['id']}] ,  ['content','is', 'Lighting' ]]
            compTaskId = sg.find_one('Task',filters,fields)
            seqData[shot['name']]=compTaskId['sg_status_list']
        
        print seq,str(seqData)
        seqStrings.append(seq+'###'+str(seqData))
        fileObject=open(self.lightingData,"w")  
        fileObject.write("\n".join(seqStrings))
        fileObject.close()
        del(task)

    def getShotgunPublishes(self,*args):
        import tank
        import shotgun_api3 as shotgun

        #P:\global\code\pipeline\bootstrap\tank\install\frameworks\manual\psy-framework-publish\v0.2.0\python\wrappers.py
        PROJECT_ID=tank.platform.current_engine().context.project['id']
        SERVER_PATH = "https://psyop.shotgunstudio.com"
        SCRIPT_USER = "mlTools"
        SCRIPT_KEY = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
        sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

        # Get handle to Asset Manager tank application
        assetmgr = tank.platform.current_engine().apps["psy-multi-assetmanager"]

        # Grab updated publish data from shotgun
        publish_directory = assetmgr.publish_directory
        publish_directory.update(async=False)
        
        # list image/lighting render publishes
        paths=[]
        for publish in list(publish_directory.all_publishes):
            if publish.component_type=='image/render' and 'sequences' in publish.path:
                if 'lighting' in publish.path or 'fx' in publish.path:
                    paths.append(publish.path.replace("\\","/")+" "+str(publish.start_frame)+"-"+str(publish.end_frame)+" "+str(publish.width))

        #update publishRendersData for offline
        fileObject=open(self.publishRendersData,"w")
        fileObject.write("\n".join(paths))
        fileObject.close()
        # store in dict based on shot
        data={}
        for path in paths:
            shot=path.split("/")[5]
            if not shot in data.keys():
                data[shot]=[]
            data[shot].append(path)
        return data



    def initializePublishes(self,*args):
        if not os.path.exists(self.publishRendersData):
            fileObject=open(self.publishRendersData,"w")
            fileObject.close()
        fileObject=open(self.publishRendersData,"r")
        contents=fileObject.read()
        fileObject.close()
        paths=contents.split("\n")
        data={}
        if len(paths)>1:
            for path in paths:
                shot=path.split("/")[5]
                if not shot in data.keys():
                    data[shot]=[]
                data[shot].append(path)
        return data
        
    def getprojectData(self,*args):
        shotSequence=self.shotDir.split('/')[-1]
        if not os.path.exists(self.projectData):
            fileObject=open(self.projectData,"w")
            fileObject.close()
        fileObject=open(self.projectData,"r")
        contents=fileObject.read()
        fileObject.close()
        seqStrings=contents.split("\n")
        seqData={}
        for seqString in seqStrings:
            if seqString.startswith(shotSequence):
                seqStrData=seqString.split('###')[-1]
                json_acceptable_string = seqStrData.replace("'", "\"")
                seqData = json.loads(json_acceptable_string)
        return seqData

    def addColumn(self,*args):
        label=nuke.getInput("new column label:")
        if label!="":
            self.shotTable.setColumnCount(self.shotTable.columnCount()+1)
            item = QtGui.QTableWidgetItem()
            item.setText(label)
            self.shotTable.setHorizontalHeaderItem(self.shotTable.columnCount()-1, item)
            
    def removeColumn(self,*args):
        p = nuke.Panel('remove column:')
        columns=[]
        for c in range(self.shotTable.columnCount())[4:]:
            columns.append(self.shotTable.horizontalHeaderItem(c).text())
        p.addEnumerationPulldown('columns:', " ".join(columns))
        ret = p.show()
        if ret:
            col=p.value('columns:')
            for c in range(self.shotTable.columnCount()):
                if col in self.shotTable.horizontalHeaderItem(c).text():
                    self.shotTable.removeColumn(c)
            self.writeself.projectData()
    
    ###FILES TABLE FUNCTIONS
    
    def selectScript(self,*args):
        if len(self.filesList.selectedItems()):
            self.selScript=self.filesList.selectedItems()[0].text()
        self.buildTreeA()
        self.resetTreeBColors()
        self.compareRenders()
    
    def listNukeFiles(self,*args):
        self.filesList.clear()
        scriptFiles=os.listdir(self.nukeScriptsPath)
        nukeFiles=[]
        for sfile in scriptFiles:
            if sfile.endswith(".nk") and self.fileFilterText in sfile:
                self.filesList.addItem(sfile)
                if 'comp' in sfile:
                    nukeFiles.append(sfile)
        self.filesList.sortItems(QtCore.Qt.DescendingOrder)
        latestFile=max(nukeFiles)
        #latestItem= self.filesList.findItems(latestFile,QtCore.Qt.MatchFlags(QtCore.Qt.MatchContains))[0]
        #self.filesList.setCurrentItem(latestItem)
        #self.compareRenders()
        
   
    def updateShotThumbnail(self,*args):
        if not os.path.exists(self.thumbsPath):
            os.makedirs(self.thumbsPath)
        availthumbs=os.listdir(self.thumbsPath)
        if self.selShot+".jpg" in availthumbs:
            self.iconLabel.setPixmap(QtGui.QPixmap(self.thumbsPath+'/'+self.selShot+'.jpg'))
        else:
            self.iconLabel.setPixmap('')
   
    def versionUpFile(self,*args):
        import shutil
        projectPath=self.nukeScriptsPath
        nukeFile=projectPath+"/"+self.selScript
        #copy file
        shutil.copyfile(nukeFile, versionUpFilename(nukeFile))

    def openInExplorer(self,*args):
        shotDir=self.nukeScriptsPath
        import subprocess
        f="\\".join(shotDir.split("/"))
        subprocess.Popen('explorer '+f)
        
    #TREE FUNCTIONS

    def selectTab(self,*args):
        print self.bottomTab.currentWidget().objectName()
        if self.bottomTab.currentIndex()==0:
            self.rendersPath=self.template_3dPath
        if self.bottomTab.currentIndex()==1:
            self.rendersPath=self.template_2dPath  

        self.buildTreeB()

    def makeRenderOutCurrentSubprocess(self,*args):
        shotRenderPath=self.template_2dPath.replace("shotNum",self.selShot)
        output=self.getSelectionFromNukeTreeRendersOut()[0]

        task = nuke.ProgressTask("getRenders")
        path= shotRenderPath+"/"+output
        print "former",path

        regex = re.compile("v[0-9]{2,9}")
        vers=regex.findall(path)
        newPath=path
        for ver in vers:
            newPath=newPath.replace(ver,"current")
            newDir="/".join(newPath.split("/")[:-1])
        try:
            os.makedirs(newPath)
        except:
            pass
        print "new",newPath
        import subprocess    
        pyFile=PM_ROOT+'/makeSeqCurrentDuplicate.py'
        process=subprocess.Popen('python '+pyFile+' '+path+' '+newPath+' '+ver,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        nuke.message("making "+path+" current")
        
    def makeRenderOutCurrent(self,*args):
        shotRenderPath=self.template_2dPath.replace("shotNum",self.selShot)
        output=self.getSelectionFromNukeTreeRendersOut()[0]
        print "former",output
        output=unFilterPath(output)
        task = nuke.ProgressTask("getRenders")
        path= shotRenderPath+"/"+output
        print "new",path
        regex = re.compile("v[0-9]{2,9}")
        vers=regex.findall(path)
        newPath=path
        for ver in vers:
            newPath=newPath.replace(ver,"current")
            newDir="/".join(newPath.split("/")[:-1])
        try:
            os.makedirs(newDir)
        except:
            pass
        parentDir="/".join(path.split("/")[:-1])
        try:
            len(os.listdir(parentDir))
        except WindowsError:
            nuke.message("directory empty")
            return
        length=len(os.listdir(parentDir))
        for i,file in enumerate(os.listdir(parentDir)):
            if not file.startswith('.'):
                task.setMessage( 'copying %s' % file )
                vers=regex.findall(file)
                newFile=file
                for ver in vers:
                    newFile=newFile.replace(ver,"current")
                shutil.copy(parentDir+"/"+file,newDir+"/"+newFile)
                task.setProgress( int( float(i) / length *100) )
        del(task)
        
    def expandServerTree(self,*args):
        if self.bottomTab.currentIndex()==0:
            tree=self.RendersInTreeB
        if self.bottomTab.currentIndex()==1:
            tree=self.RendersOutTreeB
        tree.resizeColumnToContents(0)
        tree.resizeColumnToContents(1)
        
    def expandTrees(self,*args):
        it = QtGui.QTreeWidgetItemIterator(self.RendersInTreeA)
        for i in it:
            if i.value().parent() is None:
                self.RendersInTreeA.expandItem(i.value())
        it = QtGui.QTreeWidgetItemIterator(self.RendersInTreeB)
        for i in it:
            if i.value().parent() is None:
                self.RendersInTreeB.expandItem(i.value())
    
    def removeListRenders(self,*args):
        fileObject=open('C:/.nuke/rendersToRemove.txt',"r")
        content=fileObject.read().split('\n')
        task = nuke.ProgressTask("getRenders")

        for i,line in enumerate(content):
            task.setMessage(line)
            task.setProgress( int( float(i) / len(content) *100) )
            print line
            for root, dirs, files in os.walk(line, topdown=False):
                for name in files:
                    try:
                        os.remove(os.path.join(root, name))
                    except:
                        pass
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except:
                        pass
                try:
                    os.rmdir(root)
                except:
                    pass
        del(task)
    
    def remove3dRenders(self,*args):
        serverSeqs=self.getSelectionFromServerTree()
        treeSel=self.RendersInTreeB.selectedItems()
        fileObject=open('Z:/.nuke/rendersToRemove.txt',"a")

        for sel in treeSel:
            selectedText=self.getTreePathFromItem(sel)
            top= self.searchDir3D+'/'+selectedText
            fileObject.write(top+'\n')
            
            # for root, dirs, files in os.walk(top, topdown=False):
                # for name in files:
                    # try:
                        # os.remove(os.path.join(root, name))
                    # except:
                        # pass
                # for name in dirs:
                    # try:
                        # os.rmdir(os.path.join(root, name))
                    # except:
                        # pass
                # try:
                    # os.rmdir(root)
                # except:
                    # pass
                    
        fileObject.close()
                        
    def selectHighlighted(self,*args):
        it = QtGui.QTreeWidgetItemIterator(self.RendersInTreeB)
        for i in it:
            if i.value().foreground(0).color().rgb()==4294901760 and 'v0' in i.value().text(0) and not 'exr' in i.value().text(0):
                i.value().setSelected(1)
    
    def buildTreeA(self,*args):
        if self.selShot and self.selScript:
            tree=''
            if self.bottomTab.currentIndex()==0:
                tree=self.RendersInTreeA
            if self.bottomTab.currentIndex()==1:
                tree=self.RendersOutTreeA
            if self.bottomTab.currentIndex()<2:    
                tree.clear()
                
                projectPath=self.template_nukeScriptPath.replace("shotNum",self.selShot)
                nukeFile=projectPath+"/"+self.selScript
                seqs=getNukeScriptSeqs(nukeFile,self.searchDir3D)
                #remove incoming from paths
                pathsOnly=[]
                for seq in seqs:
                    #only list beauty files
                    #if "beauty" in seq:
                    pathsOnly.append(filterPath(seq,self.searchDir3D))

                pathTree=buildTreeFromPaths(pathsOnly)
                #build Tree
                dicts=[[pathTree,tree]]
                for dict,parent in dicts:
                    for k in dict.keys():
                        item=QtGui.QTreeWidgetItem()
                        item.setText(0,k)
                        if type(parent) is QtGui.QTreeWidget:
                            if not item.text(0)=='<files>':
                                tree.insertTopLevelItem(0,item)
                        if type(parent) is QtGui.QTreeWidgetItem:
                            if not item.text(0)=='<files>':
                                parent.addChild(item)
                        if type(dict[k]) is collections.defaultdict:
                            dicts.append([dict[k],item])
                            #print "found dict",k
                        if type(dict[k]) is list and type(parent) is not QtGui.QTreeWidget:
                            for i in dict[k]:
                                item=QtGui.QTreeWidgetItem()
                                item.setText(0,i)
                                parent.addChild(item)
                tree.sortItems(0,QtCore.Qt.AscendingOrder)

    def importSelectedNukeScriptSeqs(self,*args):
        tree=self.RendersInTreeB
        if self.bottomTab.currentIndex()==0:
            tree=self.RendersInTreeA
        if self.bottomTab.currentIndex()==1:
            tree=self.RendersOutTreeA
        tree.clear()
        
        projectPath=self.nukeScriptsPath
        nukeFile=projectPath+"/"+self.selScript
        seqs=getNukeScriptSeqs(nukeFile,self.searchDir3D)
        #remove incoming from paths
        pathsOnly=[]
        for seq in seqs:
            #only list beauty files
            if "beauty" in seq:
                print seq
                parent=os.path.dirname(seq)
                print parent
                fileList=nuke.getFileNameList(parent)
                for fl in fileList:
                    if '####' in fl:
                        fl=fl.replace('-',' ')
                        file,first,last=fl.split(' ')
                        r=nuke.nodes.Read()
                        r['file'].setValue(parent+'/'+file)
                        r['first'].setValue(int(first))
                        r['last'].setValue(int(last))

    def setSelSeqsOmit(self,*args):
        import tank
        import shotgun_api3 as shotgun

        PROJECT_ID=tank.platform.current_engine().context.project['id']
        SERVER_PATH = "https://psyop.shotgunstudio.com"
        SCRIPT_USER = "mlTools"
        SCRIPT_KEY = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
        sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

        '''
        publishFile=self.nukeScriptsPath+"/rendersData.txt"
        selSeq=self.getSelectionFromServerTree()[0].text(0)
        print selSeq
        toOmit=[]
        if os.path.exists(publishFile):
            fileObject=open(publishFile,"r")
            contents=fileObject.read()
            fileObject.close()
            seqs=contents.split("\n")
            for seq in seqs:
                if selSeq in seq:
                    toOmit.append(seq)
            for to in toOmit:
                contents=contents.replace(to,to+' omit')
            fileObject=open(publishFile,"w")
            fileObject.write(contents)
            fileObject.close()
        self.buildTreeB()
        '''
        for seq in self.getSelectionFromServerTree():
            pubseq=seq.text(0)
            print seq.text(0)
            fields = ['id', 'code', 'sg_status_list']
            filters = [
                ['code','is',pubseq],
                ['project','is',{'type':'Project','id':PROJECT_ID}],
                ['sg_format','is','exr'],
                ]
            seqSel=sg.find("PublishedFile",filters,fields)
            sg.update('PublishedFile', seqSel[0]['id'], {'sg_status_list': 'omt'})
            parent=seq.parent()
            #parent.removeChild(seq)
            color=QtGui.QColor(255,255,0)
            seq.setForeground(0,color)

        
    def buildTreeB(self,*args):
        tree=self.RendersInTreeB
        seqs=[]
        if self.bottomTab.currentIndex()==0:
            tree=self.RendersInTreeB
            tree.clear()

            if self.selShot in self.shotgunPublishes.keys():
                seqs=self.shotgunPublishes[self.selShot]
            #remove incoming from paths, ignore omit in file
            pathsOnly=[]
            for seq in seqs:
                if not 'omit' in seq:
                    pathsOnly.append(filterPath(seq,self.searchDir3D))
                
            pathTree=buildTreeFromPaths(pathsOnly)
            #build Tree
            dicts=[[pathTree,tree]]
            for dict,parent in dicts:
                for k in dict.keys():
                    item=QtGui.QTreeWidgetItem()
                    item.setText(0,k)
                    if type(parent) is QtGui.QTreeWidget:
                        if not item.text(0)=='<files>':
                            tree.insertTopLevelItem(0,item)
                    if type(parent) is QtGui.QTreeWidgetItem:
                        if not item.text(0)=='<files>':
                            parent.addChild(item)
                    if type(dict[k]) is collections.defaultdict:
                        dicts.append([dict[k],item])
                        #print "found dict",k
                    if type(dict[k]) is list and type(parent) is not QtGui.QTreeWidget:
                        for i in dict[k]:
                            item=QtGui.QTreeWidgetItem()
                            if len(i.split(" "))>1:
                                item.setText(0,i.split(" ")[0])
                                item.setText(1,i.split(" ")[1])
                                item.setText(2,i.split(" ")[2])
                            parent.addChild(item)
                            #parent.setText(1,i.split(" ")[1].split(":")[0])
                            #parent.parent().setText(1,i.split(" ")[1].split(":")[0])
                            parent.parent().parent().setText(1,i.split(" ")[1])
                            parent.parent().parent().setText(2,i.split(" ")[2])
            tree.sortItems(0,QtCore.Qt.AscendingOrder)
            
        if self.bottomTab.currentIndex()==1:
            tree=self.RendersOutTreeB
            tree.clear()
            '''
            dirs=os.listdir(self.searchDir2D)   
            for d in dirs:
                if not 'current' in d:
                    if os.path.exists(self.searchDir2D+'/'+d+'/comp/exr') or os.path.exists(self.searchDir2D+'/'+d+'/comp/jpeg'):
                        item=QtGui.QTreeWidgetItem()
                        item.setText(0,d)
                        tree.insertTopLevelItem(0,item)
            '''
            renders={}
            for dir in os.listdir(self.searchDir2D):
                if os.path.isdir(self.searchDir2D+'/'+dir):
                    for sub in os.listdir(self.searchDir2D+'/'+dir):
                        if os.path.isdir(self.searchDir2D+'/'+dir+'/'+sub):
                            if not dir in renders.keys():
                                renders[dir]=[]
                            contents=os.listdir(self.searchDir2D+'/'+dir+'/'+sub)
                            for item in contents:
                                if item.startswith("."):
                                    contents.remove(item)
                            renders[dir].append([sub,",".join(contents)])
            for k in renders.keys():
                item=QtGui.QTreeWidgetItem()
                item.setText(0,k)
                tree.insertTopLevelItem(0,item)
                for render in renders[k]:
                    subitem=QtGui.QTreeWidgetItem()
                    subitem.setText(0,render[0])
                    subitem.setText(1,render[1])
                    item.addChild(subitem)
    
            
            
    def remove2dRenders(self,*args):
        serverSeqs=self.getSelectionFromServerTree()
        #ask=nuke.ask("are you sure?")
        treeSel=self.RendersOutTreeB.selectedItems()
        for tr in treeSel:
            
            print self.searchDir2D,tr.text(0),tr.parent().text(0)

	ask=1
        if ask:
	    for sel in treeSel:
		top= self.searchDir2D+'/'+sel.text(0)
		for root, dirs, files in os.walk(top, topdown=False):
		    for name in files:
			if '_comp_' in name:
			    try:
				os.remove(os.path.join(root, name))
			    except:
				pass
		    for name in dirs:
			if '/comp/' in root:
			    try:
				os.rmdir(os.path.join(root, name))
			    except:
				pass
		print top
	    self.buildTreeB()

        
    def openRenderDirectory(self,*args):
        serverSeqs=self.getSelectionFromServerTree()
        #ask=nuke.ask("are you sure?")
        treeSel=self.RendersOutTreeB.selectedItems()
        import subprocess
        for tr in treeSel:
            #dir=self.searchDir2D+'/'+tr.text(0)+'/'+tr.parent().text(0)
            dir=self.searchDir2D+'/'+tr.parent().text(0)+'/'+tr.text(0)
            f="\\".join(dir.split("/"))
            subprocess.Popen('explorer '+f)
            
    def removeOldRenders(self,*args):
        self.bottomTab.setCurrentIndex(1)
        task = nuke.ProgressTask('removing Renders:')

        for r in range(self.shotTable.rowCount()):
            self.shotTable.setCurrentCell(r,0)
            self.buildTreeB()
            it = QtGui.QTreeWidgetItemIterator(self.RendersOutTreeB)
            comps=[]
            for i in it:
                if '_composite_' in i.value().text(0):
                    comps.append(i.value().text(0))
            comps.sort()
            for i,c in enumerate(comps[:-3]):
                print c
                task.setMessage('removing:'+c)
                task.setProgress( int( float(i) / (len(comps)-3) *100) )
                top= self.searchDir2D+'/'+c
                print top
                for root, dirs, files in os.walk(top, topdown=False):
                    for name in files:
                        if '_comp_' in name:
                            try:
                                os.remove(os.path.join(root, name))
                            except:
                                pass
                    for name in dirs:
                        if '/comp/' in root:
                            try:
                                os.rmdir(os.path.join(root, name))
                            except:
                                pass

    def uploadThumbnail(self,*args):
        serverSeqs=self.getSelectionFromServerTree()
        treeSel=self.RendersOutTreeB.selectedItems()
        print treeSel
        import math
        if len(treeSel)==1:
            #path=self.searchDir2D+'/'+treeSel[0].text(0)+'/comp/exr/'
            #path=self.searchDir2D+'/'+treeSel[0].text(0)+'/comp/jpeg/'
            path=self.searchDir2D+'/'+treeSel[0].parent().text(0)+'/'+treeSel[0].text(0)+'/'+treeSel[0].text(1)
            print path
            files= nuke.getFileNameList(path)[0]
            filename,frames=files.split(' ')
            first,last=frames.split('-')
            mid=str(int(math.floor((float(first)+float(last))/2))).zfill(4)
            thumbpath=path+'/'+filename.replace(".#.",".####.").replace('####',mid)
            print thumbpath

            
            #write to thumbsdir
            nuke.selectAll() 
            nuke.invertSelection() 
            thumbsDir=self.thumbsPath
            frm=nuke.frame()
            read=nuke.nodes.Read()
            read['file'].setValue(thumbpath)
            read['on_error'].setValue(3)
            
            rf=nuke.nodes.Reformat()
            rf.setInput(0,read)
            rf['type'].setValue(1)
            rf['box_width'].setValue(256)
            rf['box_height'].setValue(144)
            rf['box_fixed'].setValue(1)

            w=nuke.nodes.Write()
            w.setInput(0,rf)
            w['file'].setValue(thumbsDir+'/'+self.selShot+'.jpg')
            w['views'].setValue(nuke.views()[0])
            w['file_type'].setValue('jpeg')
            #w['colorspace'].setValue('sRGB')
            nuke.execute(w,frm,frm)

            nuke.delete(w)
            nuke.delete(rf)
            nuke.delete(read)
            
            
            #send to shotgun
            import shotgun_api3 as shotgun
            SERVER_PATH = "https://psyop.shotgunstudio.com"
            SCRIPT_USER = "mlTools"
            SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
            sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
            fields = ['id', 'code', 'sg_status_list']
            filters = [
                ['project','is',{'type':'Project','id':PROJECT_ID}],
                ['code','is',self.selShot]
                ]
            asset= sg.find_one("Shot",filters,fields)
            id=asset['id']
            result = sg.upload_thumbnail("Shot",id,thumbsDir+'/'+self.selShot+'.jpg')
            print thumbsDir+'/'+self.selShot+'.jpg','successfully uploaded'

        else:
            nuke.message('select only one Render')

    def openShotgunShotPage(self,*args):
        id=self.shotgunShotData[self.selShot]['shotId']
        import webbrowser
        webbrowser.open_new('https://psyop.shotgunstudio.com/detail/Shot/'+str(id))
        
    def openScriptFile(self,*args):
        nukeFile=self.nukeScriptsPath+"/"+self.selScript
        nuke.scriptOpen(nukeFile)
        #ask to set comp status
	'''
        switch=nuke.ask('opening: '+self.selShot+'\nset composite status to: in progress?')
        if switch:
            import tank
            PROJECT_ID=tank.platform.current_engine().context.project['id']
            import shotgun_api3 as shotgun
            SERVER_PATH = "https://psyop.shotgunstudio.com"
            SCRIPT_USER = "mlTools"
            SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
            sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

            try:
                shotName=self.selShot.split('_')[0]
                #get shot
                fields = ['id', 'code', 'sg_status_list']
                filters = [['project','is', {'type':'Project','id':PROJECT_ID}],['code', 'is',shotName]]
                shot = sg.find_one('Shot',filters,fields)
                #get tasks
                fields = ['id', 'code', 'sg_status_list']
                filters = [ ['entity','is',{'type':'Shot','id':shot['id']}] ,  ['content','is', 'Composite' ]]
                taskID = sg.find_one('Task',filters,fields)
                #sg.update('Task', precompID['id'], {'sg_status_list': 'cmpt'})
                sg.update('Task', taskID['id'], {'sg_status_list': 'ip'})
            except:
                pass
	'''
    
    def switchOpenScriptFile(self,*args):
        nukeFile=self.nukeScriptsPath+"/"+self.selScript
        nuke.scriptSave()
        nuke.scriptClear()
        nuke.scriptOpen(nukeFile)
        
    def compareRenders(self,*args):
        #create array of nukeSeqs
        renderLayers=[]
        found=0
        fileTreeItems=[]
        it = QtGui.QTreeWidgetItemIterator(self.RendersInTreeA)
        for i in it:
            fileTreeItems.append(self.getTreePathFromItem(i.value()))
        #loop thru array of serverSeqs
        it = QtGui.QTreeWidgetItemIterator(self.RendersInTreeB)
        for i in it:
            #if doesnt exist in nuke renders and is the latest version
            if not self.getTreePathFromItem(i.value()) in fileTreeItems:
                #turns all items above red
                color=QtGui.QColor(255,0,0)
                i.value().setForeground(0,color)
                if self.latestVersionTreeItem(i.value()):
                    if i.value().parent() is not None:
                        i.value().parent().setForeground(0,color)  
        it = QtGui.QTreeWidgetItemIterator(self.RendersInTreeB)
        for i in it:
            #if doesnt exist in nuke renders
            if not self.getTreePathFromItem(i.value()) in fileTreeItems:
                if i.value().parent() is None:
                    #turns all items above black
                    color=QtGui.QColor(0,0,0)
                    i.value().setForeground(0,color)
		
        it = QtGui.QTreeWidgetItemIterator(self.RendersInTreeB)        
        for i in it:
            if i.value().parent() is None:
                #if text color red or black
                if i.value().foreground(0).color().rgb()==4294901760 or i.value().foreground(0).color().rgb()==4278190080 and not "deep" in i.value().text(0) and not "Deep" in i.value().text(0):
                    found=1
                    renderLayers.append(i.value().text(0))
        #print renderLayers
        return found,renderLayers

    def resetTreeBColors(self,*args):
        color=QtGui.QColor(200,200,200)
        it = QtGui.QTreeWidgetItemIterator(self.RendersInTreeB)
        for i in it:
            i.value().setForeground(0,color)
        
    def latestVersionTreeItem(self,item):
        par=item.parent()
        if par is not None:
            numChildren=par.childCount()
            if par.indexOfChild(item)==numChildren-1:
                if item.childCount()>0:
                    return True
            else:
                return False
        
    def getTreePathFromItem(self,item):
        path=item.text(0)
        while item.parent() is not None:
            path=item.parent().text(0)+"/"+path
            item=item.parent()
        return path
        
    def addSelectedItemsToNukeScript(self,*args):
        incomingPath=self.template_3dPath.replace("shotNum",self.selShot)
        nukeFile=self.nukeScriptsPath+"/"+self.selScript
        #if selected is version or single imgseq and not mainFolder
        if self.RendersInTreeB.selectedItems()[0].parent() is not None:
            addRendersToNukeScript(nukeFile,self.getSelectionFromServerTree(),incomingPath)
            nuke.message(self.RendersInTreeB.selectedItems()[0].text(0)+" added to "+nukeFile)
            #update display
            self.buildTreeA()
            self.resetTreeBColors()
            self.compareRenders()
        else:
            nuke.message("select version or individual Render to be added")
        
    def copyFirstMiddleLast(self,*args):
        if len(args)==0:
            print ""
        else:
            self.selShot=args[0]
            self.selScript=args[1]
            
        tree=self.RendersInTreeB
        if self.bottomTab.currentIndex()==0:
            tree=self.RendersInTreeA
        if self.bottomTab.currentIndex()==1:
            tree=self.RendersOutTreeA
        tree.clear()
        
        nukeFile=self.nukeScriptsPath+"/"+self.selScript
        seqs=getNukeScriptSeqs(nukeFile,"P:/projects/samgalaxyfifa_6464P")
        start,end=scriptFirstLastFrames(nukeFile)
        dif=int(float(end-start)/2)
        for seq in seqs:
            seq=seq.replace("%04d","####")
            newDir="/".join(seq.replace("P:","C:").split("/")[:-1])
            try:
                os.makedirs(newDir)
            except:
                pass
            if "####" in seq:
                for fr in [start,start+dif,end]:
                    file=seq.replace("####",str(fr).zfill(4))
                    if os.path.exists(file):
                        if not os.path.exists(file.replace("P:","C:")):
                            shutil.copy(file,file.replace("P:","C:"))
            else:
                if os.path.exists(seq):
                    if not os.path.exists(seq.replace("P:","C:")):
                        shutil.copy(seq,seq.replace("P:","C:"))
                
    def showDependencies(self,*args):
        selSeqs= self.getSelectionFromNukeTree()
        msg=''
        if selSeqs:
            selSeq=self.template_3dPath.replace("shotNum",self.selShot)+'/'+selSeqs[0]
            msg+="ORIGIN SCENE:\n"
            msg+=get_publish_metadata_value(selSeq, "origin_scene")+'\n'
            #pprint (get_publish_metadata_value(selSeq, "origin_scene"))
            refs=get_publish_metadata_value(selSeq, "references")
            maFiles=[]
            abcFiles=[]
            for ref in refs:
                if '.mb' in ref or '.ma' in ref:
                    maFiles.append(ref.replace('\\','/'))
                if '.abc' in ref:
                    abcFiles.append(ref.replace('\\','/'))
            msg+="\n"        
            msg+="Alembic Cache References:\n"
            for abc in abcFiles:
                msg+=abc+'\n'
            msg+="\n"  
            msg+="Maya File References:\n"
            for ma in maFiles:
                msg+=ma+'\n'
            #pprint (get_publish_metadata_value(selSeq, "published_from"))
            #pprint (get_publish_metadata_value(selSeq, "aovs"))
            #pprint (get_publish_metadata_value(selSeq, "unpublished_aov"))
            nuke.message(msg)
                   
    def getSelectionFromServerTree(self,*args):
        selection=[]
        if self.bottomTab.currentIndex()==0:
            treeSel=self.RendersInTreeB.selectedItems()[0]
        if self.bottomTab.currentIndex()==1:
            treeSel=self.RendersOutTreeB.selectedItems()[0]
        selection.append(treeSel)
        for c in range(treeSel.childCount()):
            selection.append(treeSel.child(c))
        seqs=[]
        for sel in selection:
            if sel.childCount()==0:
                seqs.append(sel)
        return seqs
        
    def getSelectionFromNukeTree(self,*args):
        selection=[]
        treeSel=self.RendersInTreeA.selectedItems()[0]
        selection.append(treeSel)
        for c in range(treeSel.childCount()):
            selection.append(treeSel.child(c))
        seqs=[]
        for sel in selection:
            if sel.childCount()==0:
                seqs.append(self.getTreePathFromItem(sel))
        return seqs
        
    def getSelectionFromNukeTreeRendersOut(self,*args):
        selection=[]
        treeSel=self.RendersOutTreeB.selectedItems()[0]
        selection.append(treeSel)
        for c in range(treeSel.childCount()):
            selection.append(treeSel.child(c))
        seqs=[]
        for sel in selection:
            if sel.childCount()==0:
                seqs.append(self.getTreePathFromItem(sel))
        return seqs

    def replaceRendersFromSelections(self,*args):
        incomingPath=self.template_3dPath.replace("shotNum",self.selShot)
        nukeFile=self.nukeScriptsPath+"/"+self.selScript
        seqASel=self.RendersInTreeA.selectedItems()
        seqBSel=self.RendersInTreeB.selectedItems()
        #if selection made
        if len(seqASel)>0 and len(seqBSel)>0:
            #if not mainDirectory
            if seqASel[0].parent() is not None and seqBSel[0].parent() is not None:
                regex = re.compile("v[0-9]{2,9}")
                #get version from serverSelection
                serverSel=self.getTreePathFromItem(self.RendersInTreeB.selectedItems()[0])
                newVersion=regex.findall(serverSel)[0]
                #get version from nukeSelection
                nukeSel=self.getTreePathFromItem(self.RendersInTreeA.selectedItems()[0])
                oldVersion=regex.findall(nukeSel)[0]
                #get all nukeRenders Selection
                nukeSeqs=self.getSelectionFromNukeTree()
                
                #replace within nukeScript
                fileObject=open(nukeFile,"r")
                contents=fileObject.read()
                fileObject.close()
                for seq in nukeSeqs:
                    oldPath=seq
                    newPath=seq.replace(oldVersion,newVersion)
                    contents=contents.replace(oldPath,newPath)
                fileObject=open(nukeFile,"w")
                fileObject.write(contents)
                fileObject.close()
                nuke.message(nukeSel+" replaced with "+serverSel)
                #then test if any new Renders not found in older version
                serverSeqs=self.getSelectionFromServerTree()
                #update version in nukeSeq list to test against serverSeqs
                nukeSeqs=[ns.replace(oldVersion,newVersion) for ns in nukeSeqs]
                newSeqs=[]
                for servSeq in serverSeqs:
                    if not servSeq in nukeSeqs:
                        newSeqs.append(servSeq)
                #if new seqs found, ask to add to nukescript
                if len(newSeqs)>0:
                    displayString="\n".join(newSeqs)
                    if nuke.ask(str(len(newSeqs))+" new Renders found in selection:\n"+displayString+"\n add to nuke script?"):
                        addRendersToNukeScript(nukeFile,newSeqs,incomingPath)
                #update display
                self.buildTreeA()
                self.resetTreeBColors()
                self.compareRenders()
            else:
                nuke.message("select version or individual Renders")
        else:
            nuke.message("select Renders to find and replace")
        
    def revealWindowsDirectory(self,*args):
        print "opening window for file location"
        
    def updatePublishedFileForSelectedShot(self,*args):
        if os.path.exists(self.searchDir3D):
            publishFile=self.nukeScriptsPath+"/rendersData.txt"
            print publishFile
            if not os.path.exists(publishFile):
                fileObject=open(publishFile,"w")
                fileObject.close()
            #get published seqs   
            fileObject=open(publishFile,"r")
            contents=fileObject.read()
            fileObject.close()
            existingSeqs=contents.split("\n")
            existingDirs=[]
            for exSeq in existingSeqs:
                existingDirs.append("/".join(exSeq.split("/")[:-1]))
            #compare seq to published
            newSeqs=[]
            seqsFound,flag= findImgsFromDirectoryTask(self.searchDir3D,existingDirs,4)
            #seqsFound=findPublishedRendersFromShotgun(self.selShot)
            for seq in seqsFound:
                if not seq in existingSeqs:
                    newSeqs.append(seq)
            #write to publish file    
            if len(newSeqs)>0:
                fileObject=open(publishFile,"a")
                for ns in newSeqs:
                    fileObject.write(ns+"\n")
                fileObject.close()
                
                
        #update display    
        self.buildTreeB()

    def printFilePaths(self,*args):
	treeSel=self.RendersInTreeB.selectedItems()
	for sel in treeSel:
	    print self.searchDir3D+'/'+self.getTreePathFromItem(sel)+" "+sel.text(1)
	    #print sel.text(1)
	#for seq in self.getTreePathFromItem():
        #    pubseq=seq.text(0)+" "+seq.text(1)	
	#    print pubseq
       
    def sendRenderToFrameCycler(self,*args):
        if self.bottomTab.currentIndex()==0:
            tree=self.RendersInTreeB
        if self.bottomTab.currentIndex()==1:
            tree=self.RendersOutTreeB
        
        seqBSel=tree.selectedItems()[0]
        if seqBSel.childCount()==0:
            fRange=seqBSel.text(1).split("-")
            path=self.getTreePathFromItem(seqBSel)
            w=nuke.nodes.Write()
            w['file'].setValue(self.searchDir+'/'+path)
            nukescripts.framecycler_this(w,fRange[0],fRange[1], 1,nuke.views()[0])
            nuke.delete(w)
        else:
            nuke.message("select Render to preview")
            
    def getWriteNames(self,*args):
        nukeFile=self.nukeScriptsPath+"/"+self.selScript

        fileObject=open(nukeFile,"r")
        contents=fileObject.read()
        fileObject.close()

        #update writeVersion
        regex = re.compile("v[0-9]{2,9}")
        writeStarts=contents.split('Write {')
        writes=[]
        for ws in writeStarts:
            nodeData= ws.split('}')[0].split('\n')
            if len(nodeData)<15:
                for line in nodeData:
                    if 'name' in line:
                        writes.append(line.split(" ")[-1])
        return writes
        
    def updateShotWriteExtension(self,*args):
        tree=self.RendersInTreeB
        nukeFile=self.nukeScriptsPath+"/"+self.selScript

        fileObject=open(nukeFile,"r")
        contents=fileObject.read()
        fileObject.close()

        #update writeVersion
        regex = re.compile("v[0-9]{2,9}")
        writeStarts=contents.split('Write {')
        for ws in writeStarts:
            nodeData= ws.split('}')[0].split('\n')
            if len(nodeData)<15:
                for line in nodeData:
                    if '/comp/' in line:
                        newline=line
                        newline=newline.replace('.jpg','.exr')
                        newline=newline.replace('/jpeg/','/exr/')
                        contents=contents.replace(line,newline)
                        print 'updatedWriteNode',newline
                    if 'file_type' in line:
                        contents=contents.replace(line,'file_type exr')
                    if 'channels' in line:
                        contents=contents.replace(line,'channels rgba')
        #writeFile
        fileObject=open(nukeFile,"w")
        fileObject.write(contents)
        fileObject.close()
        nuke.message('updated: '+nukeFile)
        #update display
        self.listNukeFiles()
        self.buildTreeA()
        self.resetTreeBColors()
        self.compareRenders()
            
    def updateShotToLatest(self,*args):
        tree=self.RendersInTreeB
        nukeFile=self.nukeScriptsPath+"/"+self.selScript
        seqsA=getNukeScriptSeqs(nukeFile,self.searchDir3D)
        
        fixedSeqsA=[]
        for seq in seqsA:
            seq=seq.replace('%04d','####')
            fixedSeqsA.append(seq)
        updatedSeqs=[]
        for seq in fixedSeqsA:
            updatedSeq=findLatest(seq)
            if updatedSeq:
                if not updatedSeq in fixedSeqsA:
                    print updatedSeq
                    updatedSeqs.append([seq,updatedSeq])
        if len(updatedSeqs):
            res=nuke.ask('found new renders, updated?')
            if res:
                #copy file
                newVersion=versionUpFilename(nukeFile)
                shutil.copyfile(nukeFile,newVersion)
                #replace within nukeScript
                fileObject=open(newVersion,"r")
                contents=fileObject.read()
                fileObject.close()
                for paths in updatedSeqs:
                    old,new=paths
                    contents=contents.replace(old,new)
                    contents=contents.replace(old.replace('####','%04d'),new)
                    
                #update writeVersion
                regex = re.compile("v[0-9]{2,9}")
                writeStarts=contents.split('Write {')
                for ws in writeStarts:
                    nodeData= ws.split('}')[0].split('\n')
                    if len(nodeData)<15:
                        for line in nodeData:
                            if '_comp/' in line:
                                lineVer= regex.findall(line)[-1]
                                shotVer= regex.findall(newVersion)[-1]
                                contents=contents.replace(line,line.replace(lineVer,shotVer))
                                print 'updatedWriteNode',lineVer,shotVer
                #writeFile
                fileObject=open(newVersion,"w")
                fileObject.write(contents)
                fileObject.close()
                nuke.message('updated: '+newVersion)
                #update display
                self.listNukeFiles()
                self.buildTreeA()
                self.resetTreeBColors()
                self.compareRenders()


    #NOTES FUNCTIONS
    def updateNotesTable(self,*args):
        for i in range(self.sendTaskCombo.count()):
            #self.sendTaskCombo.addItems(["Composite","Lighting","Animation",])
            self.sendTaskCombo.removeItem(0)
        tasks=self.shotgunShotData[self.selShot]['tasks'].keys()
        self.sendTaskCombo.addItems(tasks)
        self.sendTaskCombo.setCurrentIndex(tasks.index("comp"))
        self.notesTable.clearContents()
        self.notesTable.setRowCount(0)
        self.notesTable.setSortingEnabled(False)
        #for r in range(self.notesTable.rowCount()):
        #    self.notesTable.removeRow(0)   
        if self.selShot in self.shotgunNotes.keys():
            for note in self.shotgunNotes[self.selShot]:
                columns=note.split("<,>")
                status=columns[2]
                task=columns[4]
                valid=1
                if self.notesShowClosedChbox.checkState() and "clsd" in status:
                    valid=0
                if self.notesShowCompOnlyChbox.checkState() and not "comp" in task:
                    valid=0
                if valid:
                    rowNum=self.notesTable.rowCount()
                    self.notesTable.insertRow(rowNum)
                    self.notesTable.setRowHeight(rowNum, 15)
                    for i,col in enumerate(columns[1:]):
                        item=QtGui.QTableWidgetItem()
                        item.setText(col)
                        self.notesTable.setItem(rowNum,i,item)
        self.notesTable.setSortingEnabled(True)

    def showNotesText(self,*args):
        selNotes=self.notesTable.selectedItems()
        rows=[]
        for sn in selNotes:
            if not sn.row() in rows:
                rows.append(sn.row())
        notesText=''
        for r in rows:
            notesText+=self.notesTable.item(r,0).text()+'\n'
        self.notesTextEdit.clear()
        if notesText:
            self.notesTextEdit.setText(notesText)
                
    def showNotes(self,*args):
        while self.checksVLayout.count():
            child = self.checksVLayout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clearLayout(child.layout())
        #self.notesTextEdit.setPlainText("")
        if self.selShot in self.shotgunNotes.keys():
            for note in self.shotgunNotes[self.selShot]:
                nId,noteContent=note.split('###')
                #self.notesTextEdit.insertPlainText(note+"\n")
                self.notesCheck = QtGui.QCheckBox(noteContent,self.notesTab)
                self.notesCheck.setObjectName(nId)
                self.checksVLayout.addWidget(self.notesCheck)

    def closeNote(self,*args):
        import tank
        PROJECT_ID=tank.platform.current_engine().context.project['id']
        import shotgun_api3 as shotgun
        SERVER_PATH = "https://psyop.shotgunstudio.com"
        SCRIPT_USER = "mlTools"
        SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
        sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
        
        selNotes=self.notesTable.selectedItems()
        rows=[]
        for sn in selNotes:
            if not sn.row() in rows:
                rows.append(sn.row())
        for r in rows:
            noteId=self.notesTable.item(r,5).text()
            sg.update('Note', int(noteId), {'sg_status_list': 'clsd'})
        self.getShotgunNotes()
        #self.shotgunShotData=self.getShotgunData()

    def initializeShotData(self,*args):
        if not os.path.exists(self.shotData):
            fileObject=open(self.shotData,"w")
            fileObject.close()
        fileObject=open(self.shotData,"r")
        contents=fileObject.read()
        fileObject.close()
        shotDataText=contents.split("\n")
        
        if len(shotDataText)<2:
            print len(shotDataText)
            shotDataText=self.getShotgunData()
        shotsData={}
        for shot in shotDataText[:-1]:
            tasks=shot.split("<TASK>")
            info=tasks[0]
            tasks=tasks[1:]
            shotName,id,sgName=info.split(",")
            shotDict={}
            shotDict['name']=shotName
            shotDict['shotId']=id
            shotDict['sgName']=sgName
            tasksDicts={}
            for task in tasks:
                taskDict={}
                taskType,taskStatus,taskId,TaskUser=task.split(",")
                taskDict['type']=taskType
                taskDict['status']=taskStatus
                taskDict['id']=taskId
                taskDict['users']=TaskUser.split("<USER>")
                tasksDicts[taskType]=taskDict
            shotDict['tasks']=tasksDicts
            shotsData[shotName]=shotDict
        return shotsData

    def getShotgunData(self,*args):
        import tank
        PROJECT_ID=tank.platform.current_engine().context.project['id']
        import shotgun_api3 as shotgun
        SERVER_PATH = "https://psyop.shotgunstudio.com"
        SCRIPT_USER = "mlTools"
        SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
        sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

        fields = ['id', 'code','name','tasks']
        filters = [['project','is', {'type':'Project','id':PROJECT_ID}]]
        shotsReturn = sg.find('Shot',filters,fields)
        shots=[]
        for sr in shotsReturn:
            tasks=[]
            for  t in sr['tasks']:
                tasks.append(t['id'])
            shots.append([sr['code'].replace("_",""),sr['id'],sr['code'],tasks])


        fields = ['id','code', 'sg_status_list','task_assignees','content']
        filters = [
            ['project', 'is', {"type": 'Project', 'id': PROJECT_ID}],
            ]
        tasks = sg.find('Task',filters,fields)

        for sh in shots:
            for t in tasks:
                if t['id'] in sh[3]:
                    idx=sh[3].index(t['id'])
                    users=[]
                    for us in t['task_assignees']:
                        users.append(us['name']+":"+str(us['id']))
                    users="<USER>".join(users)
                    sh[3][idx]= [t['content'],t['sg_status_list'],str(t['id']),users]

        shotDataText=""
        for sh in shots:
            taskDataText=[]
            for tasks in sh[3]:
                if tasks[0]:#if task has name
                    taskDataText.append(",".join(tasks))
            shotDataText+=sh[0]+","+str(sh[1])+","+sh[2]+"<TASK>"+"<TASK>".join(taskDataText)+"\n"

        #update notesData for offline
        fileObject=open(self.shotData,"w")
        fileObject.write(shotDataText)
        fileObject.close()
            
        shotsData={}
        for shot in shotDataText.split("\n")[:-1]:
            tasks=shot.split("<TASK>")
            info=tasks[0]
            tasks=tasks[1:]
            shotName,id,sgName=info.split(",")
            shotDict={}
            shotDict['name']=shotName
            shotDict['shotId']=id
            shotDict['sgName']=sgName
            tasksDicts={}
            for task in tasks:
                taskDict={}
                taskType,taskStatus,taskId,TaskUser=task.split(",")
                taskDict['type']=taskType
                taskDict['status']=taskStatus
                taskDict['id']=taskId
                taskDict['users']=TaskUser.split("<USER>")
                tasksDicts[taskType]=taskDict
            shotDict['tasks']=tasksDicts
            shotsData[shotName]=shotDict
        return shotsData
        
    def getShotgunDataOLD(self,*args):
        import tank
        PROJECT_ID=tank.platform.current_engine().context.project['id']
        import shotgun_api3 as shotgun
        SERVER_PATH = "https://psyop.shotgunstudio.com"
        SCRIPT_USER = "mlTools"
        SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
        sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
        fields = ['id', 'entity', 'code', 'sg_status_list','open_notes','task_assignees','content']
        filters = [
            ['project', 'is', {"type": 'Project', 'id': PROJECT_ID}],
                {
                "filter_operator": "any",
                "filters": [
                    ['content','is', 'Composite'],
                    ['content','is', 'Lighting']
                ]
                }
            ]
        tasks = sg.find('Task',filters,fields)
        shotNotes={}
        shotData={}
        for t in tasks:
            name=t['entity']['name']
            name=name.replace("_","")#fix underscore in shotnames from sg
            if not name in shotData.keys():
                shotData[name]=['','','','']
            if t['content']=='Composite':
                if len(t['task_assignees']):
                     shotData[name][0]=t['task_assignees'][0]['name']
                shotData[name][1]=t['sg_status_list']
            if t['content']=='Lighting':
                if len(t['task_assignees']):
                    shotData[name][2]=t['task_assignees'][0]['name']
                shotData[name][3]=t['sg_status_list']
            #only keep comp notes
            if t['content']=='Composite':
                notes= t['open_notes']
                for note in notes:
                    if not name in shotNotes.keys():
                        shotNotes[name]=[]
                    nt=note['name']
                    noteFormatted=str(note['id'])+'###'+nt.decode("ascii","ignore")
                    if not noteFormatted in shotNotes[name]:
                        shotNotes[name].append(noteFormatted)
                    
        return shotData
        
        
    def createShotgunNote(self,*args):
        import tank
        PROJECT_ID=tank.platform.current_engine().context.project['id']
        import shotgun_api3 as shotgun
        SERVER_PATH = "https://psyop.shotgunstudio.com"
        SCRIPT_USER = "mlTools"
        SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
        sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
        import getpass
        user=getpass.getuser()
        fields = ['id', 'name','login']
        filters = [['login', 'is',user]]
        userReturn = sg.find_one('HumanUser',filters,fields)

        task=self.sendTaskCombo.currentText()

        taskID =self.shotgunShotData[self.selShot]['tasks'][task]['id']
        content=self.notesTextEdit.toPlainText()
        for line in content.split('\n'):
            # enter data here for a note to create
            data = {'subject':task+' Note','content':line,'user':userReturn,'sg_note_type':'Internal','project': {"type":"Project","id": PROJECT_ID},'note_links':[{'type': 'Shot', 'id': int(self.shotgunShotData[self.selShot]['shotId']), 'name':self.shotgunShotData[self.selShot]['sgName']}],'tasks': [{'type': 'Task', 'id': int(taskID), 'name': task}]}
            # create the note
            noteID = sg.create('Note',data)
        self.notesTextEdit.setPlainText("")
        #self.shotgunNotes,self.shotgunShotData=sgMethods.getShotgunData(PROJECT_ID)


            
    def getShotgunNotes(self,*args):
        import tank
        PROJECT_ID=tank.platform.current_engine().context.project['id']
        import shotgun_api3 as shotgun
        SERVER_PATH = "https://psyop.shotgunstudio.com"
        SCRIPT_USER = "mlTools"
        SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
        sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
        fields = ['id', 'entity', 'sg_status_list','note_links','content','user','created_at','tasks']
        filters = [
            ['project', 'is', {"type": 'Project', 'id': PROJECT_ID}],
            ]
        notes = sg.find('Note',filters,fields)

        sgNotes=""
        for n in notes:
            for nl in n['note_links']:
                if "Shot" in nl['type']:
                    shot=nl['name'].replace("_","")
                    tasks=[]
                    for t in n['tasks']:
                        tasks.append(t['name'])
                    tasks="#".join(tasks)
                    sgNotes+=shot+"<,>"+str(n['content'])+"<,>"+str(n['sg_status_list'])+"<,>"+str(n['user']['name'])+"<,>"+tasks+"<,>"+str(n['created_at'])+"<,>"+str(n['id'])+"##ENDNOTE##\n"
        
        #update notesData for offline
        fileObject=open(self.notesData,"w")
        fileObject.write(sgNotes)
        fileObject.close()
        
        sgNotes=sgNotes.split("##ENDNOTE##\n")

        data={}
        for nd in sgNotes:
            shot=nd.split("<,>")[0]
            if not shot in data.keys():
                data[shot]=[]
            data[shot].append(nd)
        self.shotgunNotes= data
        self.updateNotesTable()

    def initializeNotes(self,*args):
        if not os.path.exists(self.notesData):
            fileObject=open(self.notesData,"w")
            fileObject.close()
        fileObject=open(self.notesData,"r")
        contents=fileObject.read()
        fileObject.close()
        notesData=contents.split("##ENDNOTE##\n")
        data={}
        for nd in notesData:
            shot=nd.split("<,>")[0]
            if not shot in data.keys():
                data[shot]=[]
            data[shot].append(nd)
        return data 
        
    def setVersionsClip(self,*args):
        regex = re.compile("v[0-9]{2,9}")
        treeSel=self.RendersOutTreeB.selectedItems()
        sels=[]
        for tr in treeSel:
            path=self.searchDir2D+'/'+tr.text(0)+'/'+tr.parent().text(0)+'/'+tr.text(1)
            list=[f for f in os.listdir(path) if not f.startswith('.')]
            first=min(list).split(".")[1]
            last=max(list).split(".")[1]
            ext=min(list).split(".")[2]
            filename=min(list).split(".")[0]
            duration=int(last)-int(first)
            pathData=path.replace("P:/","//psyop/pfs/")+'/'+filename+'.['+first+'-'+last+'].'+ext
            sels.append([pathData,duration])
        writeVersionsClip(self.searchDir2D,sels)

def writeVersionsClip(writePath,selection):
    regex = re.compile("v[0-9]{2,9}")
    f = open(writePath+"/composite.clip", "w")
    versionCurrent=regex.findall(selection[0][0])[0].replace("v","")
    clipFileHeaderFix=clipFileHeader.replace("$$$",versionCurrent)
    f.write(clipFileHeaderFix)
    for sel in selection:
        versionString=regex.findall(sel[0])[0]
        versionVal=versionString.replace("v","")
        clipFilePathFix=clipFilePath.replace("$$$",versionVal).replace("&&",str(sel[1])).replace("<path></path>","<path>"+sel[0]+"</path>")
        f.write(clipFilePathFix)
    clipFilePathsEndFix=clipFilePathsEnd.replace("$$$",versionCurrent)
    f.write(clipFilePathsEndFix)
    for sel in selection:
        versionString=regex.findall(sel[0])[0]
        versionVal=versionString.replace("v","")
        clipFileVersionFix=clipFileVersion.replace("$$$",versionVal)
        f.write(clipFileVersionFix)
    f.write(clipFileEnd)
    f.close()            
	
def attach(branch, trunk):
    FILE_MARKER = '<files>'
    '''
    Insert a branch of directories on its trunk.
    '''
    parts = branch.split('/', 1)
    if len(parts) == 1:  # branch is a file
        trunk[FILE_MARKER].append(parts[0])
    else:
        node, others = parts
        if node not in trunk:
            trunk[node] = defaultdict(dict, ((FILE_MARKER, []),))
        attach(others, trunk[node])

def buildTreeFromPaths(paths):
    FILE_MARKER = '<files>'
    main_dict = defaultdict(dict, ((FILE_MARKER, []),))
    for line in paths:
        attach(line, main_dict)
    return main_dict

def getNukeScriptSeqs(file,imagesDir):
    fileObject=open(file,"r")
    contents=fileObject.read()
    fileObject.close()
    seqs=[]
    for line in contents.split("\n"):
        fixedPath=fixFilePath(line.decode('utf-8'))
        if imagesDir in fixedPath or imagesDir.replace("lighting","fx") in fixedPath:
            seqs.append(fixedPath.split(" ")[-1])
    return seqs
    

def fixFilePaths(seqs):
    newSeqs=[]
    for seq in seqs:
        newSeqs.append(seq.replace('//','/'))
    return newSeqs

def fixFilePath(seq):
    return seq.replace('//','/')
    
def scriptFirstLastFrames(nukescript):
    fileObject=open(nukescript,"r")
    contents=fileObject.read()
    fileObject.close()
    contents=contents.split("Root {")[-1].split("\n}")[0]
    lines=contents.split("\n")
    first=0
    last=0
    for l in lines:
        if "first_frame" in l:
            first=int(l.split("first_frame ")[-1])
        if "last_frame" in l:
            last=int(l.split("last_frame ")[-1])
    return first,last

    
def getTopLeftNodePosition(nukescript):
    fileObject=open(nukescript,"r")
    contents=fileObject.read()
    fileObject.close()
    lines=contents.split("\n")
    x=0
    y=0
    for l in lines:
        if "xpos" in l:
            val=int(l.split("xpos ")[-1])
            if val<x:
                x=val
        if "ypos" in l:
            val=int(l.split("ypos ")[-1])
            if val<y:
                y=val
    return x,y

def addRendersToNukeScript(script,Renders,incomingPath):
    xpos,ypos=getTopLeftNodePosition(script)
    first,last=scriptFirstLastFrames(script)
    #for each in selection, add to nukescript file
    fileObject=open(script,"r")
    contents=fileObject.read()
    fileObject.close()
    for i,seq in enumerate(Renders):
        path=incomingPath+"/"+seq
        contents+=readEntry.replace("nnn","scriptImported_"+str(i)+"_"+seq.split("/")[-1]).replace("filepath",path).replace("fff",str(first)).replace("lll",str(last)).replace("xxx",str(xpos+i*100)).replace("yyy",str(ypos-200))
    fileObject=open(script,"w")
    fileObject.write(contents)
    fileObject.close()

def findPublishedLatestRendersFromShotgun(shotName):
    import tank
    import shotgun_api3 as shotgun
    SERVER_PATH = "https://psyop.shotgunstudio.com"
    SCRIPT_USER = "mlTools"
    SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
    sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
    # Get handle to Asset Manager tank application
    assetmgr = tank.platform.current_engine().apps["tk-multi-assetmanager"]

    task = nuke.ProgressTask("getRenders")
    task.setMessage( 'processing %s' % shotName )

    # Grab updated publish data from shotgun
    publish_directory = assetmgr.publish_directory
    publish_directory.update(async=False)

    #get shot
    fields = ['id', 'code', 'sg_status_list']
    filters = [['project','is', {'type':'Project','id':PROJECT_ID}],['code', 'is',shotName]]
    entity = sg.find_one('Shot',filters,fields)

    seqs=[]
    # Iterate over each published lighting render layer for the shot
    shot_renders = publish_directory.find_publish_type(entity, "image/lighting")
    for render_layer in shot_renders.components:
        # Get latest publish for this render layer
        latest = render_layer.latest_version
        # to get other available published formats.
        latest_exrs = latest.find_publish_format("exr")
        for aov in latest_exrs.aovs:
            seqs.append(aov.path)
            
    del(task)
    return seqs
    
def findPublishedRendersFromShotgun(shotName):
    import tank
    import shotgun_api3 as shotgun
    SERVER_PATH = "https://psyop.shotgunstudio.com"
    SCRIPT_USER = "mlTools"
    SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
    sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
    # Get handle to Asset Manager tank application
    assetmgr = tank.platform.current_engine().apps["tk-multi-assetmanager"]

    task = nuke.ProgressTask("getRenders")
    task.setMessage( 'processing %s' % shotName )

    # Grab updated publish data from shotgun
    publish_directory = assetmgr.publish_directory
    publish_directory.update(async=False)

    #get shot
    fields = ['id', 'code', 'sg_status_list']
    filters = [['project','is', {'type':'Project','id':PROJECT_ID}],['code', 'is',shotName]]
    entity = sg.find_one('Shot',filters,fields)

    seqs=[]
    # Iterate over each published lighting render layer for the shot
    shot_renders = publish_directory.find_publish_type(entity, "image/lighting")
    for render_layer in shot_renders.components:
        for version in render_layer.versions:
            exrs = version.find_publish_format("exr")
            for aov in exrs.aovs:
                if 'beauty' in aov.path:
                    seqs.append(aov.path.replace('%04d','####'))
    del(task)
    return seqs
    
def findImgsFromDirectoryTask(searchRoot,alreadyExisting,levelNum):
    flag=0
    seqs=[]
    exists=[]
    topDirs=os.listdir(searchRoot)
    dirLength=len(topDirs)
    task = nuke.ProgressTask("getRenders")
    switch=0
    tops=[]
    self.searchDirs=[searchRoot+'::0']
    for dir in self.searchDirs:
        directory=dir.split('::')[0]
        level=int(dir.split('::')[1])+1
        if level==1:
            tops=os.listdir(directory)
        for i,d in enumerate(tops):
            if d in directory:
                task.setMessage( 'processing %s' % d )
                task.setProgress( int( float(i) / len(tops) *100) )
        if level<=levelNum:
            found=0
            for file in os.listdir(directory):
                if os.path.isdir(directory+'/'+file):
                    self.searchDirs.append(directory+'/'+file+'::'+str(level))
                if '_beauty_' in file:
                    found=1
            if found and not directory in alreadyExisting:
                fList= nuke.getFileNameList(directory,True)
                for item in fList:
                    item=item.replace('exrsl','')
                    if 'exr' in item:
                        #if 'beauty_beauty' in item or 'utility_beauty' in item:
                        if '_beauty_' in item:
                            foundPath=directory+'/'+item
                            regex = re.compile("[.][0-9]*[.]")
                            pad=regex.findall(foundPath)
                            for p in pad:
                                foundPath=foundPath.replace(str(p),".####.")
                            fileOnly=foundPath.split(' ')[0]
                            if not fileOnly in exists:
                                exists.append(fileOnly)
                                seqs.append(foundPath.replace('\\','/').replace('//','/'))

    del(task)
    return seqs,flag
    
def versionUpFilename(filename):
    regex = re.compile("v[0-9]{2,9}")
    versionString=regex.findall(filename)[0]
    val=versionString[1:]
    length=len(val)
    newVal=int(val)+1
    newVersion=versionString[0]+str(newVal).zfill(length)
    return filename.replace(versionString,newVersion)
 
def findLatest(origPath):
    import re,os
    regex = re.compile("v[0-9]{2,9}")
    vers=regex.findall(origPath)
    for i in range(1,10)[::-1]:
        path=origPath
        up=int(i)
        for ver in vers:
            numsOnly=ver[1:]
            pad=len(numsOnly)
            val=int(numsOnly)
            newVer='v'+str((val+up)).zfill(pad)
            path=path.replace(ver,newVer)
        dirPath='/'.join(path.split('/')[:-1])
        if os.path.exists(dirPath):
            return path
 
def getUserProjectSequenceRoot():
    import socket
    hostName=socket.gethostname()
    userSettingsFile=PM_ROOT+"/userSettings.txt"
    if not os.path.exists(userSettingsFile):
        fileObject=open(userSettingsFile,"w")
        fileObject.close()
    fileObject=open(userSettingsFile,"r")
    contents=fileObject.read().split("\n")
    fileObject.close()
    found=0
    for line in contents:
        if hostName in line:
            project=line.split("#:#")[-1]
            found=1
            return project
            break
    if found==0:
        fileObject=open(userSettingsFile,"a")
        folder=nuke.getFilename('get project shots sequence root')
        folderPath="/".join(folder.split('/')[:-1])
        fileObject.write(hostName+"#:#"+folderPath+"\n")
        fileObject.close()
        return folderPath
    
def filterPath(path,searchDir):
    path=path.replace(searchDir+"/","").replace("//","/")
    searchDir=searchDir.replace("lighting","fx")
    path=path.replace(searchDir+"/","").replace("//","/")
    return path
    
def unFilterPath(path):
    regex = re.compile("v[0-9]{2,9}")
    parts=path.split('/')
    found=""
    idx=0
    #get version folder
    for i,p in enumerate(parts):
        if regex.findall(p):
            found=p
            idx=i
            break
   
    if not found=="":
        path="/".join(parts[:idx-1])+"/"+parts[idx]+"/"+parts[idx-1]+"/"+"/".join(parts[idx+1:])
        if path.startswith("/"):
            path=path[1:]
        
    return path
    
readEntry='''
Read {
 inputs 0
 file filepath
 first fff
 last lll
 name nnn
 xpos xxx
 ypos yyy
}
'''

clipFileHeader='''
<?xml version="1.0" encoding="UTF-8"?>
<clip type="clip" version="3">
    <name>comp</name>
    <tracks type="tracks">
        <track type="track" uid="beauty">
            <trackType>video</trackType>
            <name>beauty</name>
            <feeds currentVersion="$$$" type="feeds">'''

clipFilePath='''
                <feed type="feed" uid="$$$" vuid="$$$">
                    <spans type="spans" version="3">
                        <span type="span" version="3">
                            <duration>&&</duration>
                            <path></path>
                        </span>
                    </spans>
                </feed>'''
clipFilePathsEnd='''
            </feeds>
        </track>
    </tracks>
    <versions currentVersion="$$$" type="versions">'''
clipFileVersion='''
        <version type="version" uid="$$$">
            <name>$$$</name>
        </version>'''

clipFileEnd='''
    </versions>
</clip>'''

try:
    import tank
    from pprint import pprint

    def get_publish_metadata(img_path):
        img_dir = img_path if os.path.isdir(img_path) else os.path.dirname(img_path)
        engine = tank.platform.current_engine()
        tkinst = engine.tank
        pipeline_cfg = tkinst.pipeline_configuration
        publish_type = pipeline_cfg.get_published_file_entity_type()
        context = tkinst.context_from_path(img_dir)
        template_name = "%s_publish" % (context.entity['type'].lower())
        publish_template = engine.get_template_by_name(template_name)
        fields = publish_template.get_fields(img_dir)

        filters = [
        ["entity",            "is", context.entity],
        ["sg_component_name", "is", fields['publish_name']],
        ["sg_component_type", "is", "image/lighting"],
        ["version_number",    "is", fields['version']],
        ]

        try:
            results = tkinst.shotgun.find(publish_type, filters, ["sg_metadata"])[0]
            metadata = eval(results.get('sg_metadata', '{}'))
        except:
            metadata = {}
        return metadata
        
    def get_publish_metadata_value(img_path, key):
        return get_publish_metadata(img_path).get(key)
        
        
    def get_origin_scene(img_path):
        return get_publish_metadata_value(img_path, "origin_scene")
        
except:
    pass