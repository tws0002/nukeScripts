from __future__ import with_statement
import nuke,os,sys,nukescripts
import cryptomatte_utilities as cu

#set root to search for gizmos relative to this file
assetGizmos=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))+'/assetGizmos'
nuke.pluginAddPath(assetGizmos)

print assetGizmos

def getAssets():
    selectedAssets=[]
    class TestPanel(nukescripts.PythonPanel):
        def __init__(self):
            super(TestPanel,self).__init__('select assetGizmos to import' )

            #list of assets
            assets=os.listdir(assetGizmos)
            assets.sort()
            for asset in assets:
                b=nuke.Boolean_Knob(asset)
                b.setFlag(nuke.STARTLINE)
                self.addKnob(b) 
            self._makeOkCancelButton()

        
    p = TestPanel()
    result=p.showModalDialog()

    if result:
        for k in p.knobs():
            if p.knobs()[k].Class()=='Boolean_Knob':
                if p.knobs()[k].value():
                    selectedAssets.append(k)
    return selectedAssets
                    
                    

def main():
    for grp in nuke.selectedNodes('Group'):
        if 'addAssetGizmos' in grp.knobs():
            with grp:
                addAssets(grp)


def addAssets(grp):
    nuke.selectAll() 
    nuke.invertSelection() 
    addedGizmos=[]
    selected=getAssets()
    for n in nuke.allNodes('NoOp'):
        if n.name().endswith("_OUT"):
            aov=n.name().split("_OUT")[0]
            gizmos= findAssetGizmos(aov,grp,selected)
            lastNode=n.dependencies()[0]
            addedGizmos.extend(gizmos)
            for g in gizmos:
                lastNode.setSelected(True)
                giz=nuke.createNode(g,inpanel=False)
                nuke.selectAll() 
                nuke.invertSelection() 
                giz.setInput(0,lastNode)
                giz.setXYpos(lastNode.xpos(),lastNode.ypos()+30)
                lastNode=giz
            n.setInput(0,lastNode)
    if len(addedGizmos):
        nuke.message('ADDING ASSETS:\n'+"\n".join(addedGizmos))

def findAssetGizmos(aov,grp,selectedAssets):
    foundGizmos=[]
    missingGizmos=[]
    assets=[]
    assetDirs=os.listdir(assetGizmos)



    
    
    foundAssets=[]
    for asset in selectedAssets:
        for assetDir in assetDirs:
            if assetDir == asset:
                if not assetDir in foundAssets:
                    foundAssets.append(assetDir)
                
    for asset in foundAssets:
        if asset+"_"+aov+".gizmo" in os.listdir(assetGizmos+'/'+asset):
            foundGizmos.append(asset+"_"+aov)
    for fg in foundGizmos:
        if len(nuke.allNodes(fg))==0:
            missingGizmos.append(fg)
    
    print 'foundAssets',foundAssets
    print 'foundgizmos',foundGizmos
    print 'missingGizmos',missingGizmos
    return missingGizmos