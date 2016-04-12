from __future__ import with_statement
import nuke,os,sys,nukescripts
import cryptomatte_utilities as cu

#set root to search for gizmos relative to this file
assetGizmos=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))+'/assetGizmos'
nuke.pluginAddPath(assetGizmos)

def allNodesAllGroups(NodeClass):
    found=[]
    for grp in nuke.allNodes('Group'):
        with grp:
            for n in nuke.allNodes(NodeClass):
                found.append(n)
    return found


def main():
    nuke.toNode(nuke.root().name())
    addAssets()
    for grp in nuke.allNodes('Group'):
        with grp:
            addAssets()


def addAssets():
    nuke.selectAll() 
    nuke.invertSelection() 
    addedGizmos=[]
    for n in nuke.allNodes('NoOp'):
        if n.name().endswith("_OUT"):
            aov=n.name().split("_OUT")[0]
            gizmos= findAssetGizmos(aov)
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

def findAssetGizmos(aov):
    foundGizmos=[]
    missingGizmos=[]
    assets=[]
    assetDirs=os.listdir(assetMattesPath)

    for chan in nuke.channels():
        ch=chan.split("_")
        if "m" in ch:
            if not ch[1] in assets:
                assets.append(ch[1])
    for asset in assets:
        if asset in assetDirs:
            if asset+"_"+aov+".gizmo" in os.listdir(assetMattesPath+'/'+asset):
                foundGizmos.append(asset+"_"+aov)
    for fg in foundGizmos:
        if len(nuke.allNodes(fg))==0:
            missingGizmos.append(fg)
    return missingGizmos
