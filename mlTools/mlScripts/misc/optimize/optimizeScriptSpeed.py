from __future__ import with_statement
import nuke

#make toggle checkbox for all passes, put in groups for faster selections


ignoreTags=['Arnold_Hair','raw','single_scatter','sss_mix','scratches','grunge','pixelGrid','direct_diffuse_raw','indirect_diffuse_raw']
playerNames=['casillas','chungYong','donovan','falcao','gotze','kerzhakov','messi','moses','oscar','ronaldo','rooney','shaarawy','wuLei']

def disableNodes():

    for n in nuke.allNodes('Read'):
        playerFound=0
        for p in playerNames:
            if p in n.name():
                playerFound=1
        if not playerFound:
            for it in ignoreTags:
                if it in n.name():
                    n['disable'].setValue(True)
                    for d in nuke.dependentNodes(nuke.INPUTS,n,evaluateAll=False):
                        d['disable'].setValue(True)


def main():
    disableNodes()
    for grp in nuke.selectedNodes('Group'):
        if 'file' in grp.knobs():
            if not 'chars' in grp['file'].value():
                with grp:
                    disableNodes()
    #nuke.removeAutolabel(autolabel)
    #del(tank_on_startup)