import nuke

def main():
    for n in nuke.allNodes():
        try:
            path=n.filename()
            if 'assetGizmos' in path:
                name=n.name()
                n.setSelected(1)
                x,y=n.xpos(),n.ypos()
                g=n.makeGroup()
                nuke.delete(n)
                g.setXYpos(x,y)
                g.setName(name)
        except:
            pass