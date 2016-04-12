from __future__ import with_statement
import nuke

def main():
    for n in nuke.selectedNodes():
        tog=0
        if n['note_font_size'].value()==10:
            n['postage_stamp'].setValue(True)
            n['note_font_size'].setValue(11)
            tog=1
        if 'postage_stamp' in n.knobs() and not tog:
            if n['postage_stamp'].value():
                n['note_font_size'].setValue(10)
                n['postage_stamp'].setValue(False)
    for grp in nuke.allNodes('Group'):
        with grp:
            for n in nuke.selectedNodes():
                tog=0
                if n['note_font_size'].value()==10:
                    n['postage_stamp'].setValue(True)
                    n['note_font_size'].setValue(11)
                    tog=1
                if 'postage_stamp' in n.knobs() and not tog:
                    if n['postage_stamp'].value():
                        n['note_font_size'].setValue(10)
                        n['postage_stamp'].setValue(False)
