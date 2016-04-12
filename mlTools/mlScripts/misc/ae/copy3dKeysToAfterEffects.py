import nuke

from PySide import QtGui
def main():

    header="Adobe After Effects 8.0 Keyframe Data\n\n"
    header+='\t'+'Units Per Second'+'\t'+str(nuke.root().fps())+'\n'
    header+='\t'+'Source Width'+'\t'+str(nuke.root().width())+'\n'
    header+='\t'+'Source Height'+'\t'+str(nuke.root().height())+'\n'
    header+='\t'+'Source Pixel Aspect Ratio'+'\t'+'1'+'\n'
    header+='\t'+'Comp Pixel Aspect Ratio'+'\t'+'1'+'\n\n'
    header+='Transform'+'\t'+'Position\n'
    header+='\t'+'Frame'+'\t'+'X pixels'+'\t'+'Y pixels'+'\t'+'Z pixels'+'\t\n'




    n=nuke.selectedNode()

    for i in range(nuke.root().firstFrame(),nuke.root().lastFrame()+1):
        cW,cH=n.width(),n.height()
        x,y,z=n['translate'].valueAt(i)[0],n['translate'].valueAt(i)[1],n['translate'].valueAt(i)[2]
        x=x*100
        y=-y*100
        z=-z*100
        #might need to subtract the center value of transform node

        header+='\t'+str(i)+'\t'+str(x)+'\t'+str(y)+'\t'+str(z)+'\n'

    header+='\nEnd of Keyframe Data'

    header.replace('    ','\t')
    clipboard=QtGui.QApplication.clipboard()

    clipboard.setText(header)