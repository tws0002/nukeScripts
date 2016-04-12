import nuke
import nukescripts

class ChangeCommonKnobs( nukescripts.PythonPanel ):
    def __init__( self, nodes ):
        nukescripts.PythonPanel.__init__( self, 'adjust all Knobs' )

        if not nodes:
            nuke.message('Nothing selected')
            return
        #GET KNOBS
        commonKnobNames=nodes[0].knobs()
        for n in nodes:
            commonKnobNames=set(commonKnobNames).intersection(n.knobs())
        commonKnobNames=set(commonKnobNames)
        print commonKnobNames
        commonKnobs=[]
        for ck in commonKnobNames:
            commonKnobs.append(nodes[0][ck])
        #ADD KNOBS
        availKnobs=[ 'ChannelMask_Knob','File_Knob', 'String_Knob', 'Int_Knob', 'Format_Knob', 'Tab_Knob', 'Script_Knob', 'PyScript_Knob', 'Text_Knob', 'WH_Knob', 'BBox_Knob', 'XYZ_Knob', 'Double_Knob', 'IArray_Knob', 'XY_Knob', 'Transform2d_Knob', 'MultiView_Knob', 'AColor_Knob', 'FrameExtentKnob', 'Menu_Knob', 'UV_Knob', 'Axis_Knob', 'Scale_Knob', 'MetaKeyFrame_Knob', 'RotoToolboxKnob', 'Radio_Knob', 'RotoKnob', 'Pulldown_Knob', 'LookupCurves_Knob', 'Color_Knob','Channel_Knob',  'Array_Knob', 'Boolean_Knob','GeoSelect_Knob', 'MultiArray_Knob','Multiline_Eval_String_Knob','Eval_String_Knob','Disable_Knob']
        omit=['icon','knobChanged','name','xpos','ypos','dopesheet','selected','note_font_size','indicators','matrix']
        exist=[]
        for ak in availKnobs:
            for knob in commonKnobs:
                k=''
                if knob.Class()==ak and not knob.name() in omit and knob.visible()  and not knob.name() in exist:
                    methodToCall = getattr(nuke,ak)
                    k=methodToCall(knob.name(),knob.name())
                    k.setName(knob.name())
                    print knob.name(),knob.value()
                    k.setValue(knob.value())
                    #print k.name(),knob.Class()
                if knob.Class()=='Enumeration_Knob' and not knob.name() in exist:
                    k=nuke.Enumeration_Knob(knob.name(),knob.name(),knob.values())
                    k.setName(knob.name())
                    k.setValue(knob.value())     
                if k:
                    print knob.name(),knob.Class()
                    self.addKnob(k)
                    k.setFlag(nuke.STARTLINE)
                    exist.append(knob.name())
        
    def knobChanged(self, knob):
        for n in nuke.selectedNodes():
            n[knob.name()].setValue(knob.value())

def main():
    ChangeCommonKnobs(nuke.selectedNodes()).showModalDialog()