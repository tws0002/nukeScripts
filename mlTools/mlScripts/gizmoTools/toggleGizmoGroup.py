from __future__ import with_statement
import nuke
import os, shutil
import datetime


def main():
    switch=1
    while switch:
        if nuke.selectedNode().Class()=='Group' and switch:
            print 'test'
            groupToGizmo()
            break
            
        if not nuke.selectedNode().Class()=='Group' and switch:
            print 'adfs'
            gizmoToGroup()
            break
        break
        
def groupToGizmo():
    grp= nuke.thisGroup()
    stamp=str(datetime.datetime.now()).split(".")[0].replace("-","_").replace(":","_")
    filePath = nuke.getFilename('select Gizmo File to update', '*.gizmo')
    fileName=filePath.split("/")[-1]
    dir = os.path.dirname( filePath ) 
    try: 
        newDir= dir+'/_backup/'+stamp 
        os.makedirs(newDir)  
    except: 
        pass
    shutil.move(filePath,newDir+'/'+fileName)
    os.rename(newDir+'/'+fileName,newDir+'/'+fileName.replace("gizmo","gizno"))

    n=nuke.selectedNode().setName(fileName.split('.')[0])
    nuke.nodeCopy(filePath)

    fileObject=open(filePath,"r")
    contents=fileObject.read()
    fileObject.close()
    newContents=''
    for line in contents.split('\n'):
        line=line.replace('Group {','Gizmo {')
        if not "cut_paste_input" in line:
            if not "version" in line:
                if not "selected" in line:
                    newContents+=line+'\n'
    fileObject=open(filePath,"w")
    fileObject.write(newContents)
    fileObject.close()
    

    nuke.pluginAddPath(dir)
    n=nuke.selectedNode()
    c =nuke.createNode(fileName.split(".")[0])
    #c['tile_color'].setValue(16711935) 
    replaceNode(n,c,grp)  
    c.setName(fileName.split(".")[0])

def gizmoToGroup():
    grp= nuke.thisGroup()
    if not grp.Class()=='root':
        with grp:
            n=nuke.selectedNode()
            nPos=[n.xpos(),n.ypos()]
            nName=n.name()
            c = n.makeGroup()
    nuke.nodeCopy('%clipboard%')
    with grp:
        c=nuke.nodePaste('%clipboard%')
        nuke.delete(n)
        c.setXYpos(nPos[0],nPos[1])
        c.setName(nName)
        #c['tile_color'].setValue(4278190335L) 
        #replaceNode(n,c,grp)   
        

def replaceNode(old,new,grp): 
    with grp:
        n=old
        # remove any previous selections to avoid unwanted wiring of the new node 
        nuke.selectAll() 
        nuke.invertSelection() 
        # create a new node of the replacement Class 
        c = new
        c.setXYpos(n.xpos(), n.ypos()) 
        # connect inputs 
        for i in range(n.inputs()): 
            c.setInput(i,n.input(i)) 
        # connect outputs 
        for d in n.dependent(nuke.INPUTS,forceEvaluate=False): 
            for input in [i for i in range(d.inputs()) if d.input(i) == n]: 
                d.setInput(input,c) 
        name=n.name()
        #delete original 
        nuke.delete(n) 
        #c['name'].setValue(name)
    