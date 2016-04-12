import nuke

def main():
    for grp in nuke.allNodes('Group'):
        if 'addAssetGizmos' in grp.knobs():
            with grp:
                d=nuke.toNode('ml_AtmosControl')
                nuke.show(d,1)