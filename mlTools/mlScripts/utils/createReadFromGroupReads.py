import nuke

def main():
    for n in nuke.selectedNodes():
        r=nuke.nodes.Read()
        r.setXYpos(n.xpos(),n.ypos()+200)
        for rn in n.knobs():
            if rn in r.knobs() and not rn=='name':
                r[rn].setValue(n[rn].value())
            