from __future__ import with_statement
import nuke

def main():
    grp=nuke.thisNode()
    for n in nuke.allNodes():
        try:
            path=n.filename()
            if 'gizmo' in path:
                name=n.name()
                nodeInputs=[]
                for i in range(n.inputs()):
                    nodeInputs.append(n.input(i))
                nPos=[n.xpos(),n.ypos()]
                nName=n.name()
                c = n.makeGroup()
                c.setSelected(1)
                nuke.nodeCopy('%clipboard%')
                nuke.delete(c)
                with grp:
                    n.setSelected(1)
                    c=nuke.nodePaste('%clipboard%')
                    nuke.delete(n)
                    c.setXYpos(nPos[0],nPos[1])
                    c.setName(nName)
                    for i in range(len(nodeInputs)):
                        c.setInput(i,nodeInputs[i])

        except:
            pass

