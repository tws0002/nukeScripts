from __future__ import with_statement
import nuke

def main():
    n=start=nuke.selectedNode()

    mattes=[]
    names=""
    for ch in n.channels():
        if "m_" in ch:
            name=ch.split("_")[1]
            if not ch.split(".")[0] in mattes:
                mattes.append(ch.split(".")[0])
            if not name in names:
                names+="_"+name
      
            
    keeps=[]

    n.setSelected(False)
    grp=nuke.collapseToGroup()
    with grp:
        n=nuke.toNode('Input1')
        for t in range(len(mattes)):
            #for every 4 channels, create a remove node
            if t%4==0:
                k=nuke.nodes.Remove()
                k.setInput(0,n)
                keeps.append(k)
                k['operation'].setValue("keep")
                k['channels'].setValue(mattes[t])
            if t%4==1:
                k['channels2'].setValue(mattes[t])
            if t%4==2:
                k['channels3'].setValue(mattes[t])
            if t%4==3:
                k['channels4'].setValue(mattes[t])

        #merge all together
        m=nuke.nodes.Merge2()
        m['also_merge'].setValue('all')
        m['output'].setValue('none')
        for x,keep in enumerate(keeps):
            if x>1:#avoid mask input
                x+=1
            m.setInput(x,keep)
        
        lay=nuke.nodes.LayerContactSheet()
        lay['showLayerNames'].setValue(1)
        lay.setInput(0,m)

        o=nuke.toNode('Output1')
        o.setInput(0,lay)

        
    grp['name'].setValue("viewMattes"+names)
    grp.setInput(0,start)