import nuke

def main():
    for grp in nuke.allNodes('Group'):
        if '_Rebuild' in grp.name():
            with grp:
                norm=nuke.toNode('ML_normalizeDepth1')
                grp.addKnob(norm.knob('whitepoint'))
                atmos=nuke.toNode('atmos_Grade')
                grp.addKnob(atmos.knob('gamma'))
                atmosM=nuke.toNode('atmos_MERGE')
                grp.addKnob(atmosM.knob('mix'))

