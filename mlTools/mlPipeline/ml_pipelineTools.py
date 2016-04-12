from __future__ import with_statement
import nuke
import os,re,sys
import nukescripts
import versionTools
import cryptomatte_utilities as cu

omitRenders=['single_scatter','_raw','sss_mix','Arnold_','_depthRemapped','_grunge','_pixelGrid','uAutoAsset','uAutoMaterial','uAutoObject','Z','backlight']
publishPath='output/render/'


#set root to search for gizmos relative to this file
assetGizmos=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))+'/assetGizmos'
nuke.pluginAddPath(assetGizmos)



    
def versionUp():
    node=nuke.thisNode()
    path=node['file'].value()
    renderString=path.split(publishPath)[-1].split('/')[0]
    with node:
        nuke.selectAll()
        nuke.invertSelection()
        for n in nuke.allNodes('Read'):
            if renderString in n['file'].value():
                n.setSelected(1)
        versionTools.version_up()


def versionDown():
    node=nuke.thisNode()
    path=node['file'].value()
    renderString=path.split(publishPath)[-1].split('/')[0]
    with node:
        nuke.selectAll()
        nuke.invertSelection()
        for n in nuke.allNodes('Read'):
            if renderString in n['file'].value():
                n.setSelected(1)
        versionTools.version_down()

def matchAovs():
    node=nuke.thisNode()
    filenames=''
    for i in range(node.inputs()):
        #path=node[string+'_file'].value()
        path=node.input(i)['file'].value()
        #first=node[string+'first'].value()
        first=node.input(i)['first'].value()
        #last=node[string+'last'].value()
        last=node.input(i)['last'].value()
        renderString=path.split(publishPath)[-1].split('/')[0]
        filepath=path.split('/')[-1]
        filenames+=filepath.split('.')[0]+'\n'
        #parent='/'.join(path.split('/')[:-1])#old folder structure
        parent='/'.join(path.split('/')[:-2])#refactor
        dirs=os.listdir(parent)
        if i==1 and "diffuse_color" in dirs:#if utils, ignore diffuse color from utils
            dirs.remove("diffuse_color")
        print filepath,parent,dirs,i
        with node:
            nuke.selectAll()
            nuke.invertSelection()
            for n in nuke.allNodes('Read'):
                if n.name() in dirs:
                    n['file'].setValue(parent+'/'+n.name()+'/'+filepath.replace('beauty',n.name()))
                    n['first'].setValue(first)
                    n['last'].setValue(last)
        node['label'].setValue('[lindex [split [lindex [split [value input0.file] /] end] .] 0]\n[lindex [split [lindex [split [value input1.file] /] end] .] 0]')
        nodeName="_".join(filepath.split('_')[:-3])+"_REBUILD"
        print nodeName
        #try:
        #    node['name'].setValue(nodeName)
        #except:
        #    continue
def addAssetGizmos(*args):
    global assetGizmos
    if len(args):
        assetGizmos=assetGizmos+'/'+args[0]
    nuke.selectAll() 
    nuke.invertSelection() 
    node=nuke.thisNode()
    addedGizmos=[]
    assetMetadata=getMetadata('Asset')

    with node:
        for n in nuke.allNodes('NoOp'):
            if n.name().endswith("_OUT"):
                aov=n.name().split("_OUT")[0]
                gizmos= findAssetGizmos(aov,assetMetadata)
                lastNode=n.dependencies()[0]
                addedGizmos.extend(gizmos)
                for g in gizmos:
                    lastNode.setSelected(True)
                    giz=nuke.createNode(g,inpanel=False)
                    nuke.selectAll() 
                    nuke.invertSelection() 
                    giz.setInput(0,lastNode)
                    giz.setXYpos(lastNode.xpos(),lastNode.ypos()+30)
                    giz['tile_color'].setValue(16711935) 
                    lastNode=giz
                n.setInput(0,lastNode)
    if len(addedGizmos):
        nuke.message('ADDING ASSETS:\n'+"\n".join(addedGizmos))
        #show data
        aList='Assets:\n'
        for data in getMetadata2("Asset",node):
            aList+=data+'\n'
        node['assetList'].setValue(aList)
        mList='Materials:\n'
        for data in getMetadata2("Material",node):
            mList+=data+'\n'
        node['matList'].setValue(mList)
        eList='Existing:\n'
        for assetGizmo in getAssetGizmos2(node):
            eList+=assetGizmo+'\n'
        node['existList'].setValue(eList)
            
def findAssetGizmos(aov,assetMetadata):
    foundGizmos=[]
    missingGizmos=[]
    assets=[]
    assetDirs=os.listdir(assetGizmos)

    #metadataAssets=[]
    #for k, v in grp.metadata().iteritems():
    #    if 'manifest' in k:
    #        metadataAssets.append(v)

    #id_name_pairs = cu.parse_metadata(grp)
    #metadataAssets = [x[1] for x in id_name_pairs]

    
    
    foundAssets=[]
    for asset in assetMetadata:
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
    
    #print 'foundAssets',foundAssets
    #print 'foundgizmos',foundGizmos
    #print 'missingGizmos',missingGizmos
    return missingGizmos

def getMetadata(level):
    node=nuke.thisNode()
    data=[]
    with node:
        crypto=nuke.toNode('uCrypto'+level)
        if crypto:
            if 'exr/cryptoManifest' in crypto.metadata().keys():
                md= crypto.metadata()['exr/cryptoManifest'].split('<name>')
                for m in md[1:]:
                    data.append(m.split('<hash>')[0])
    return data
    
def getMetadata2(level,node):
    data=[]
    with node:
        crypto=nuke.toNode('uCrypto'+level)
        if crypto:
            md= crypto.metadata()['exr/cryptoManifest'].split('<name>')
            for m in md[1:]:
                data.append(m.split('<hash>')[0])
    return data
    
def showData():
    node=nuke.thisNode()
    aList='Assets:\n'
    for data in getMetadata2("Asset",node):
        aList+=data+'\n'
    node['assetList'].setValue(aList)
    mList='Materials:\n'
    for data in getMetadata2("Material",node):
        mList+=data+'\n'
    node['matList'].setValue(mList)
    eList='Existing:\n'
    for assetGizmo in getAssetGizmos2(node):
        eList+=assetGizmo+'\n'
    node['existList'].setValue(eList)
    
def printMetadata(level):
    msg=''
    for data in getMetadata(level):
        msg+=data+'\n'
    nuke.message(msg)

        
def getAssetGizmos():
    node=nuke.thisNode()
    thisAssetGizmos=[]
    with node:
        for n in nuke.allNodes():
            try:
                path=n.filename()
                if 'assetGizmos' in path:
                    thisAssetGizmos.append(n.Class())
            except:
                pass
    return thisAssetGizmos
    
def getAssetGizmos2(node):
    thisAssetGizmos=[]
    with node:
        for n in nuke.allNodes():
            try:
                path=n.filename()
                if 'assetGizmos' in path:
                    thisAssetGizmos.append(n.Class())
            except:
                pass
    thisAssetGizmos.sort()
    return thisAssetGizmos
def printAssetGizmos():
    for assetGizmo in getAssetGizmos():
        print assetGizmo
        
def updateLatest():
    node=nuke.thisNode()
    with node:
        for n in nuke.allNodes('Read'):
            n.setSelected(1)
        mlScripts.utils.version.version_latest()
        print 'updated'
    file=node['file'].value()
    fName=file.split('/')[-1].split('.')[0]
    regex = re.compile("v[0-9]{2,9}")
    vers=regex.findall(file)[0]
    #node['label'].setValue(fName+'\n'+vers)
    checkForNewAovs(node)


def toggleAovs():
    grp=nuke.thisNode()
    with grp:
        for n in nuke.allNodes('NoOp'):
            if n.name().endswith("_OUT"):
                print n.name()
                nodes=[n]
                switch=1
                for t in nodes:
                    for x in range(t.inputs()):
                        if not 'IN' in t.input(x).name():
                            thisNode=t.input(x)
                            nodes.append(thisNode)
                            if not 'aov' in thisNode.knobs():
                                if not thisNode['disable'].value():
                                    switch=0
                m=nuke.toNode(n.name().replace("OUT","MERGE"))
                if m:
                    print m.name()
                    m['disable'].setValue(switch)

def toggleAllAovs():
    for n in nuke.allNodes('NoOp'):
        if n.name().endswith("_OUT"):
            print n.name()
            nodes=[n]
            switch=1
            for t in nodes:
                for x in range(t.inputs()):
                    if not 'IN' in t.input(x).name():
                        thisNode=t.input(x)
                        nodes.append(thisNode)
                        if not 'aov' in thisNode.knobs():
                            if not thisNode['disable'].value():
                                switch=0
            
            if m:
                print m.name()
                m['disable'].setValue(switch)
                
def toggleThisAov():
    n=nuke.thisNode()
    aov=n['aov'].value()
    aovNode=nuke.toNode(aov+"_OUT")
    nodes=[aovNode]
    switch=1
    for t in nodes:
        for x in range(t.inputs()):
            if not 'IN' in t.input(x).name():
                thisNode=t.input(x)
                nodes.append(thisNode)
                if not 'aov' in thisNode.knobs():
                    if not thisNode['disable'].value():
                        switch=0
                        break
    aovMerge=nuke.toNode(aovNode.name().replace("OUT","MERGE"))
    if aovMerge:
        print aovMerge.name()
        aovMerge['disable'].setValue(switch)
