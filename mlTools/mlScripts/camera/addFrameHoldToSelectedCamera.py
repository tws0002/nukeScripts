import nuke

def main():
    cam=nuke.selectedNode()
    if cam.Class()=='Camera2':
        frameKnob = nuke.Int_Knob('holdFrame')
        cam.addKnob(frameKnob)
        cam['holdFrame'].setValue(int(nuke.frame()))
        for knob in cam.knobs():
            if cam[knob].isAnimated():
                cam[knob].setExpression('curve(holdFrame)')
        label=cam['label'].value()
        label+=('\nHOLDFRAME [value holdFrame]') 
        cam['label'].setValue(label)
        #cam['read_from_file'].setValue(False)