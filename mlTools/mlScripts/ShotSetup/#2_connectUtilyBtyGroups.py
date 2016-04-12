import nuke

def main():
    for n in nuke.selectedNodes('Group'):
        if n.Class()=='Group':
            fileName=n['file'].value().split("/")[-1]
            if 'lAll_beauty' in fileName:
                copy=nuke.nodes.Copy()
                copy['from0'].setValue('none')
                copy['to0'].setValue('none')
                copy['channels'].setValue('all')
                #util
                util= fileName.replace('lAll_beauty','uBasic_beauty')
                utilNode=n
                for nd in nuke.selectedNodes('Group'):
                    if util in nd['file'].value():
                        utilNode=nd
                copy.setInput(0,utilNode)
                copy.setInput(1,n)
                #domelight
                dome= fileName.replace('lAll_beauty','domeLgt_beauty')
                domeNode=n
                for nd in nuke.selectedNodes('Group'):
                    if dome in nd['file'].value():
                        domeNode=nd
                        dlc=nuke.nodes.domeLight_contribution()
                        dlc.setInput(0,n)
                        dlc.setInput(1,domeNode)
                        copy.setInput(1,dlc)
                    