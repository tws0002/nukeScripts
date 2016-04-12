from __future__ import with_statement
import nuke

def main():
    grp=nuke.selectedNode()   
    with grp:
        for node in nuke.allNodes():
            found=0
            switch=0
            for k in node.knobs():
                if node.knob(k).isAnimated():
                    label=nuke.Text_Knob(node.name()+"_divider",node.name())
                    if not switch:
                        grp.addKnob(label)
                    l = nuke.Link_Knob(k)
                    l.makeLink(node.name(), k)
                    l.setName(node.name()+'_'+k)
                    grp.addKnob(l)
                    node.knob(k).removeKey(0)
                    switch=1
            if switch:
                l = nuke.Link_Knob('disable')
                l.makeLink(node.name(), 'disable')
                l.setName(node.name()+'_disable')
                grp.addKnob(l)
        #label=nuke.Text_Knob("btn_divider","I/O")
        #grp.addKnob(label)
        #pyButtonUpdateToGizmo = nuke.PyScript_Knob('updateGizmo', "updateGizmo", "scripts.convertGroupToGizmo.main()")
        #pyButtonUpdateToGizmo.setFlag(nuke.STARTLINE) 
        #grp.addKnob(pyButtonUpdateToGizmo)
