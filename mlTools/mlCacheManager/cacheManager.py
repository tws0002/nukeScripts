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
win=panels.registerWidgetAsPanel('cacheManager.NukeTestWindow', 'cacheManager', 'farts', True)



pane = nuke.getPaneFor('Properties.1')
#pane = nuke.getPaneFor('DAG.1')
#win.show()
win.addToPane(pane)
'''



class NukeTestWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        self.publishData={}
        self.publishItems=[]
        self.selection=[]
        self.localDrive="D:"
    
        QtGui.QWidget.__init__(self, parent)
        #TreeA_Buttons
        self.PublishesHLayout = QtGui.QHBoxLayout()
        self.setLayout(self.PublishesHLayout)
        self.PublishesButtonsVLayout=QtGui.QVBoxLayout()
        #ServerRendersTree
        self.publishesTree = QtGui.QTreeWidget()
        self.publishesTree.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.publishesTree.setObjectName("publishesTree")
        item=QtGui.QTreeWidgetItem()
        item.setText(0,"Publishes:")
        item.setText(1,"serverFrames:")
        item.setText(2,"localFrames:")
        self.publishesTree.setHeaderItem(item)
        self.publishesTree.setColumnCount(3)
        self.publishesTree.resizeColumnToContents(0)
        self.publishesTree.resizeColumnToContents(1)
        self.PublishesHLayout.addWidget(self.publishesTree)
        #frame widgets
        self.renderLocation = QtGui.QComboBox()
        self.renderLocation.insertItems(0,["server","local"])
        self.PublishesButtonsVLayout.addWidget(self.renderLocation)
        self.frameNthSize=QtGui.QLineEdit()
        self.frameNthSize.setText("10")
        self.PublishesButtonsVLayout.addWidget(self.frameNthSize)
        self.frameRange=QtGui.QLineEdit()
        self.frameRange.setText("")
        self.PublishesButtonsVLayout.addWidget(self.frameRange)
        self.phoneLabel = QtGui.QLabel()
        self.phoneLabel.setText("chunkSize")
        self.phoneLabel.setBuddy(self.frameNthSize)
        self.frameNthSize.setMaximumWidth(100)
        self.frameRange.setMaximumWidth(100)
        #TreeB_Buttons
        publishesTreeBtns = [
            ["print path", self.printPaths],
            ["copy local", self.copyLocal],
            ["printDependents", self.printDependentAovs],
            ["compareFiles", self.compareFiles],
            ["copyAllNodes", self.copyAllNodes],
        ]
        for btn in publishesTreeBtns:
            pushBtn = QtGui.QPushButton()
            pushBtn.setText(btn[0])
            pushBtn.clicked.connect(btn[1])
            self.PublishesButtonsVLayout.addWidget(pushBtn)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.PublishesButtonsVLayout.addItem(spacerItem)
        self.PublishesHLayout.addLayout(self.PublishesButtonsVLayout)
        
        self.getShotgunPublishes()
        self.buildTree()
        self.renderLocation.currentIndexChanged.connect(self.switchFilepaths)
        
    def getShotgunPublishes(self,*args):
        import tank
        import shotgun_api3 as shotgun

        PROJECT_ID=tank.platform.current_engine().context.project['id']
        SERVER_PATH = "https://psyop.shotgunstudio.com"
        SCRIPT_USER = "mlTools"
        SCRIPT_KEY = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
        sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

        # Get handle to Asset Manager tank application
        assetmgr = tank.platform.current_engine().apps["tk-multi-assetmanager"]

        # Grab updated publish data from shotgun
        publish_directory = assetmgr.publish_directory
        publish_directory.update(async=False)

        # list image/lighting render publishes
        paths=[]
        for publish in list(publish_directory.all_publishes):
            if publish.component_type=='image/lighting' and 'sequences' in publish.path:
                meta=[]
                for key in publish.metadata['aovs']:
                    meta.append( publish.metadata['aovs'][key].replace("\\","/"))
                aovs=publish.metadata['aovs']
                path=publish.path.replace("\\","/")
                parts=path.split("/")
                newPath="/".join([parts[4],parts[6],parts[10],parts[11],parts[-1]])
                verPath="/".join([parts[4],parts[6],parts[10],parts[11]])
                paths.append(newPath)
                self.publishData[verPath]=meta
        self.publishItems=paths

        

        
    def getTreeSelection(self,*args):
        selection=[]
        treeSel=self.publishesTree.selectedItems()
        for ts in treeSel:
            item=ts
            parentSelected=0
            while ts.parent() is not None:
                if ts.parent().isSelected():
                    parentSelected=1
                ts=ts.parent()
            if not parentSelected:
                selection.append(item)
        self.selection=selection

    def printPaths(self,*args):
        self.getTreeSelection()
        for s in self.selection:
            print self.getTreePathFromItem(s)
            print self.convertTreePathToServerPath(self.getTreePathFromItem(s))
        
    def getTreePathFromItem(self,item):
        path=item.text(0)
        while item.parent() is not None:
            path=item.parent().text(0)+"/"+path
            item=item.parent()
        return path
        
    def buildTree(self,*args):
        pathTree=buildTreeFromPaths(self.publishItems)
        #build Tree
        dicts=[[pathTree,self.publishesTree]]
        for dict,parent in dicts:
            for k in dict.keys():
                item=QtGui.QTreeWidgetItem()
                item.setText(0,k)
                if type(parent) is QtGui.QTreeWidget:
                    if not item.text(0)=='<files>':
                        self.publishesTree.insertTopLevelItem(0,item)
                if type(parent) is QtGui.QTreeWidgetItem:
                    if not item.text(0)=='<files>':
                        parent.addChild(item)
                if type(dict[k]) is collections.defaultdict:
                    dicts.append([dict[k],item])
                    #print "found dict",k
                if type(dict[k]) is list and type(parent) is not QtGui.QTreeWidget:
                    for i in dict[k]:
                        #add frames to parent
                        parent.setText(1,i.split(" ")[-1])
        self.publishesTree.sortItems(0,QtCore.Qt.AscendingOrder)
        
    def convertTreePathToServerPath(self,path):
        #get current project name
        localGizmoDir=''
        for p in sys.path:
            if 'nuke' in p and 'scripts' in p and 'projects' in p:
                localGizmoDir= p.replace('\\','/')
        projectName=localGizmoDir.split('/')[2]
        parts=path.split("/")
        serverPath="P:/projects/"+projectName+"/sequences/"
        if len(parts):
            serverPath+=parts[0]
        if len(parts)>1:
            serverPath+="/shots/"+parts[1]
        if len(parts)>2:
            serverPath+="/publish/image/lighting/"+parts[2]
        if len(parts)>3:
            serverPath+="/"+parts[3]
        return serverPath

    def getSelectionDependents(self,*args):
        self.getTreeSelection()
        children=[]
        treeSel=self.selection
        for ts in treeSel:
            if ts.childCount()==0:
                children.append(ts)
            for i in range(ts.childCount()):
                treeSel.append(ts.child(i))
        self.dependents=children
        

    def printDependentAovs(self,*args):
        self.getSelectionDependents()
        for d in self.dependents:
            for aov in self.publishData[self.getTreePathFromItem(d)]:
                rootPath=self.convertTreePathToServerPath(self.getTreePathFromItem(d))
                print rootPath,aov

    def compareFiles(self,*args):
        color=QtGui.QColor(255,0,0)
        it = QtGui.QTreeWidgetItemIterator(self.publishesTree)
        for i in it:
            if i.value().childCount()==0:
                serverPath=self.convertTreePathToServerPath(self.getTreePathFromItem(i.value()))
                localPath=serverPath.replace("P:",self.localDrive)
                frames=[]
                if os.path.exists(localPath):
                    for file in os.listdir(localPath+'/exr'):
                        if os.path.isfile(localPath+'/exr/'+file):
                            print file
                            frames.append(str(int(file.split(".")[1])))
                    frames.sort()
                    i.value().setForeground(0,color)
                    i.value().setText(2,",".join(frames))
                
            
    def copyLocal(self,*args):
        self.getSelectionDependents()
        task = nuke.ProgressTask("getRenders")
        for d in self.dependents:
            rootPath=self.convertTreePathToServerPath(self.getTreePathFromItem(d))
            aovData=self.publishData[self.getTreePathFromItem(d)]
            for i,aov in enumerate(aovData):
                path,frameRange=aov.split(" ")
                start,end=frameRange.split("-")
                serverPath=rootPath+"/exr/"+path
                localPath=serverPath.replace("P:",self.localDrive)
                dirPath=os.path.dirname(localPath)
                task.setMessage( 'processing %s' % path )
                task.setProgress( int( float(i) / len(aovData) *100) )
                try:
                    os.makedirs(dirPath)
                except:
                    pass
                incr=int(self.frameNthSize.text())
                for i in range(int(start),int(end))[::incr]:
                    serverPath=rootPath+"/exr/"+path
                    localPath=serverPath.replace("P:",self.localDrive)
                    serverFramePath=serverPath.replace("%04d",str(i).zfill(4))
                    localFramePath=localPath.replace("%04d",str(i).zfill(4))
                    print serverFramePath,localFramePath
                    if os.path.exists(serverFramePath) and not os.path.exists(localFramePath):
                        print "copying",serverFramePath
                        shutil.copy(serverFramePath,localFramePath)
        del(task)
            
    def switchFilepaths(self,*args):
        grps=nuke.allNodes("Group")
        reads=nuke.allNodes("Read")
        for grp in grps:
            for n in grp.nodes():
                if n.Class()=="Group":
                    grps.append(n)
                if n.Class()=="Read":
                    reads.append(n)
        if self.renderLocation.currentText()=="server":
            print "server"
            for r in reads:
                path=r['file'].value()
                path=path.replace(self.localDrive,"P:")
                r['file'].setValue(path)
                r['on_error'].setValue(0)
                r['cacheLocal'].setValue('auto')
                
        if self.renderLocation.currentText()=="local":
            print "local"
            for r in reads:
                path=r['file'].value()
                path=path.replace("P:",self.localDrive)
                parentDir="/".join(path.split("/")[:-1])

                if os.path.exists(parentDir):
                    print parentDir
                    r['file'].setValue(path)
                    r['on_error'].setValue(3)
                    r['cacheLocal'].setValue('never')
                    
    def copyAllNodes(self,*args):
        grps=nuke.allNodes("Group")
        reads=nuke.allNodes("Read")
        start=nuke.root()['first_frame'].value()
        end=nuke.root()['last_frame'].value()
        for grp in grps:
            for n in grp.nodes():
                if n.Class()=="Group":
                    grps.append(n)
                if n.Class()=="Read":
                    reads.append(n)
        task = nuke.ProgressTask("getRenders")
        for i,r in enumerate(reads):
            serverPath=r['file'].value()
            localPath=serverPath.replace("P:",self.localDrive)
            dirPath=os.path.dirname(localPath)
            task.setMessage( 'processing %s' % dirPath )
            task.setProgress( int( float(i) / len(reads) *100) )
            try:
                os.makedirs(dirPath)
            except:
                pass
            incr=int(self.frameNthSize.text())
            for i in range(int(start),int(end))[::incr]:
                serverFramePath=serverPath.replace("%04d",str(i).zfill(4))
                localFramePath=localPath.replace("%04d",str(i).zfill(4))
                print serverFramePath,localFramePath
                if os.path.exists(serverFramePath) and not os.path.exists(localFramePath):
                    print "copying",serverFramePath
                    shutil.copy(serverFramePath,localFramePath)
        del(task)
        
def buildTreeFromPaths(paths):
    FILE_MARKER = '<files>'
    main_dict = defaultdict(dict, ((FILE_MARKER, []),))
    for line in paths:
        attach(line, main_dict)
    return main_dict
        
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