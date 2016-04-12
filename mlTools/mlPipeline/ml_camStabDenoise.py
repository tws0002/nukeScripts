from __future__ import with_statement
import nuke
import os,re,sys
import nukescripts




def setupDenoise():
    cam=nuke.thisNode().input(1)

    color=nuke.toNode("PositionToColor")
    rot=nuke.toNode("ColorMatrix")
    screen=nuke.toNode("screenSpace")
    color2=nuke.toNode("PositionToColor2")
    rot2=nuke.toNode("ColorMatrix2")
    screen2=nuke.toNode("screenSpace2")
    frmBlnd=nuke.toNode("FrameBlend")
    frmBlnd2=nuke.toNode("FrameBlend2")
    
    start=int(nuke.root()['first_frame'].value())
    end=int(nuke.root()['last_frame'].value())
    chunk=nuke.thisNode()['chunkSize'].value()
    
    color['color'].clearAnimated()
    screen['focal'].clearAnimated()
    screen['h_apert'].clearAnimated()
    screen['v_apert'].clearAnimated()
    rot['matrix'].clearAnimated()
    frmBlnd['startframe'].clearAnimated()
    frmBlnd['endframe'].clearAnimated()
    
    color2['color'].clearAnimated()
    screen2['focal'].clearAnimated()
    screen2['h_apert'].clearAnimated()
    screen2['v_apert'].clearAnimated()
    rot2['matrix'].clearAnimated()
    frmBlnd2['startframe'].clearAnimated()
    frmBlnd2['endframe'].clearAnimated()
    
    color['color'].setAnimated()
    screen['focal'].setAnimated()
    screen['h_apert'].setAnimated()
    screen['v_apert'].setAnimated()
    rot['matrix'].setAnimated()
    frmBlnd['startframe'].setAnimated()
    frmBlnd['endframe'].setAnimated()
    
    color2['color'].setAnimated()
    screen2['focal'].setAnimated()
    screen2['h_apert'].setAnimated()
    screen2['v_apert'].setAnimated()
    rot2['matrix'].setAnimated()
    frmBlnd2['startframe'].setAnimated()
    frmBlnd2['endframe'].setAnimated()
    
    halfChunk=chunk*0.5
    nuke.toNode("Dissolve")['chunk'].setValue(halfChunk)
    for i in range(start,end+1):
        
        
        frm= i-((i)%chunk)+halfChunk
        frm2=i-((i+halfChunk)%chunk)+halfChunk
        
        print frm,frm2

        camMatrix=cam['world_matrix'].getValueAt(frm)
        camMatrix2=cam['world_matrix'].getValueAt(frm2)
        focal=cam['focal'].getValueAt(frm)
        hap=cam['haperture'].getValueAt(frm)
        vap=cam['vaperture'].getValueAt(frm)
        
        focal2=cam['focal'].getValueAt(frm2)
        hap2=cam['haperture'].getValueAt(frm2)
        vap2=cam['vaperture'].getValueAt(frm2)
        
        color['color'].setValueAt(camMatrix[3],i,0)
        color['color'].setValueAt(camMatrix[7],i,1)
        color['color'].setValueAt(camMatrix[11],i,2)
        
        color2['color'].setValueAt(camMatrix2[3],i,0)
        color2['color'].setValueAt(camMatrix2[7],i,1)
        color2['color'].setValueAt(camMatrix2[11],i,2)
        
        screen['focal'].setValueAt(focal,i)
        screen['h_apert'].setValueAt(hap,i)
        screen['v_apert'].setValueAt(vap,i)
        
        screen2['focal'].setValueAt(focal2,i)
        screen2['h_apert'].setValueAt(hap2,i)
        screen2['v_apert'].setValueAt(vap2,i)
        
        rot['matrix'].setValueAt(camMatrix[0],i,0)
        rot['matrix'].setValueAt(camMatrix[1],i,1)
        rot['matrix'].setValueAt(camMatrix[2],i,2)
        rot['matrix'].setValueAt(camMatrix[4],i,3)
        rot['matrix'].setValueAt(camMatrix[5],i,4)
        rot['matrix'].setValueAt(camMatrix[6],i,5)
        rot['matrix'].setValueAt(camMatrix[8],i,6)
        rot['matrix'].setValueAt(camMatrix[9],i,7)
        rot['matrix'].setValueAt(camMatrix[10],i,8)
        
        rot2['matrix'].setValueAt(camMatrix2[0],i,0)
        rot2['matrix'].setValueAt(camMatrix2[1],i,1)
        rot2['matrix'].setValueAt(camMatrix2[2],i,2)
        rot2['matrix'].setValueAt(camMatrix2[4],i,3)
        rot2['matrix'].setValueAt(camMatrix2[5],i,4)
        rot2['matrix'].setValueAt(camMatrix2[6],i,5)
        rot2['matrix'].setValueAt(camMatrix2[8],i,6)
        rot2['matrix'].setValueAt(camMatrix2[9],i,7)
        rot2['matrix'].setValueAt(camMatrix2[10],i,8)

        frmBlnd['startframe'].setValueAt(frm-halfChunk,i)
        frmBlnd['endframe'].setValueAt(frm+halfChunk,i)
        frmBlnd2['startframe'].setValueAt(frm2-halfChunk,i)
        frmBlnd2['endframe'].setValueAt(frm2+halfChunk,i)
