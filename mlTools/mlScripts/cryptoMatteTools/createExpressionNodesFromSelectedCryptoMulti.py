
import nuke

def main():
    #n=nuke.selectedNode()
    #if n.Class()=='Group':
    #    n.begin()
    #    s=nuke.selectedNode()
    #    n.end()
        
    for s in nuke.selectedNodes():
        mattes= s['matteList'].value().split(',')
        express=s['expression'].value()

        #n.begin()
        expr=nuke.nodes.Expression()
        expr['expr0'].setValue(express)
        expr['channel0'].setValue('rgba')
        expr.setInput(0,s)
        expr.setName(''.join(mattes))
        #n.end()