from __future__ import with_statement
   
import nuke,os,sys
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
    for grp in nuke.allNodes('Group'):
        if 'addAssetGizmos' in n.knobs():
            with grp:
                addAssets(grp)


def addAssets(grp):
    nuke.selectAll() 
    nuke.invertSelection() 
    addedGizmos=[]
    for n in nuke.allNodes('NoOp'):
        if n.name().endswith("_OUT"):
            aov=n.name().split("_OUT")[0]
            gizmos= findAssetGizmos(aov,grp)
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

def findAssetGizmos(aov,grp):
    foundGizmos=[]
    missingGizmos=[]
    assets=[]
    assetDirs=os.listdir(assetGizmos)

    #metadataAssets=[]
    #for k, v in grp.metadata().iteritems():
    #    if 'manifest' in k:
    #        metadataAssets.append(v)

    id_name_pairs = cu.parse_metadata(grp)
    metadataAssets = [x[1] for x in id_name_pairs]
    
    
    foundAssets=[]
    for asset in metadataAssets:
        for assetDir in assetDirs:
            if assetDir in asset:
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

