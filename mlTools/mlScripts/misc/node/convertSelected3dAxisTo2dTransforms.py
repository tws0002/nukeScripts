import nuke


def main():

    nSel=nuke.selectedNodes()
    cam=''
    first=int(nuke.root()['first_frame'].value())
    last=int(nuke.root()['last_frame'].value())
    for n in nSel:
        if n.Class()=='Camera2':
            cam=n

    if not cam:
        nuke.message('must have a camera in selection')

    if cam:
        for n in nSel:
            if not n.Class()=='Camera2':
                #create reconcile and constant
                c=nuke.nodes.Constant()
                rec=nuke.nodes.Reconcile3D()
                rec.setInput(0,c)
                rec.setInput(1,cam)
                rec.setInput(2,n)
                nuke.execute(rec,first,last)
                tr=nuke.nodes.Transform()
                tr['name'].setValue('2Doutput_From_'+n.name())
                tr['translate'].copyAnimation(0, rec['output'].animation(0)) 
                tr['translate'].copyAnimation(1, rec['output'].animation(1)) 
                tr.setXYpos(n.xpos(),n.ypos()+200)
                nuke.delete(c)
                nuke.delete(rec)