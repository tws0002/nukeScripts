import nuke

def mainOLD():
    bds=nuke.allNodes('BackdropNode')
    layers=[]
    for bd in bds:
        if 'layer' in bd.knobs():
            lay=bd['layer'].value()
            if not lay in layers:
                layers.append(lay)

    for layer in layers:
        bds=[]
        for bd in nuke.allNodes("BackdropNode"):
            if "_BACKDROP" in bd.name() and bd['layer'].value()==layer:
                bds.append(bd)



        bdMin = max([bd['bdheight'].value() for bd in bds]) 

        for bd in bds:
            bd['bdheight'].setValue(bdMin)
            stamp=nuke.toNode(bd['stamp'].value())
            m=nuke.toNode(bd['merge'].value())
        
            stampX=bd.xpos()+20
            stampY=bd.ypos()+bd['bdheight'].value()-120
            stamp.setXYpos(stampX,stampY)
        
            mX=bd.xpos()+20
            mY=bd.ypos()+bd['bdheight'].value()-30
            m.setXYpos(mX,mY)
            
            
            
def main():
    recentBd=nuke.toNode(nuke.root()['recentBD'].value())
    rbdHeight=recentBd['bdheight'].value()
    for bd in nuke.allNodes("BackdropNode"):
        if "_BACKDROP" in bd.name():
            bd['bdheight'].setValue(rbdHeight)
            noOp=nuke.toNode(bd['noOp'].value())
            m=nuke.toNode(bd['merge'].value())
        
            noOpX=bd.xpos()+20
            noOpY=bd.ypos()+bd['bdheight'].value()-120
            noOp.setXYpos(noOpX,noOpY)
        
            mX=bd.xpos()+20
            mY=bd.ypos()+bd['bdheight'].value()-30
            m.setXYpos(mX,mY)




