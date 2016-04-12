from __future__ import with_statement
import nuke

def main():
    outs=[]
    for n in nuke.allNodes('NoOp'):
        if n.name().endswith("_OUT"):
            outs.append(n)
    grps=nuke.allNodes('Group')
    for grp in grps:
        with grp:
            for n in nuke.allNodes('NoOp'):
                if n.name().endswith("_OUT"):
                    outs.append(n)
    for out in outs:
        print out.name()
        nodes=[out]
        switch=1
        for t in nodes:
            for x in range(t.inputs()):
                if not 'IN' in t.input(x).name():
                    thisNode=t.input(x)
                    nodes.append(thisNode)
                    if not 'template' in thisNode.knobs():
                        if not thisNode['disable'].value():
                            switch=0
                            break
        m=nuke.toNode(out.name().replace("OUT","MERGE"))
        if m:
            print m.name()
            m['disable'].setValue(switch)

            
            
            
            
def fromSelection():
    startMerge=nuke.thisNode()
    startNode=nuke.toNode(startMerge.name().replace("MERGE","OUT"))
    nodes=[startNode]
    switch=1
    for t in nodes:
        for x in range(t.inputs()):
            if not 'IN' in t.input(x).name():
                thisN=t.input(x)
                nodes.append(thisN)
                if not 'template' in thisN.knobs():
                    if not thisN['disable'].value():
                        switch=0
                        break
    return switch