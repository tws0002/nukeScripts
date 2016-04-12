from __future__ import with_statement
import nuke,os

def getMissingFrames(node):
    parent= os.path.dirname(node['file'].value())
    if len(nuke.getFileNameList(parent))>1:
        nuke.selectAll()
        nuke.invertSelection()
        node.setSelected(1)
        nuke.zoomToFitSelected()
        nuke.message('missing frames: '+",".join(nuke.getFileNameList(parent)))
def main():
    for n in nuke.allNodes('Read'):
        getMissingFrames(n)
    for grp in nuke.allNodes('Group'):
        with grp:
            for n in nuke.allNodes('Read'):
                getMissingFrames(n)

