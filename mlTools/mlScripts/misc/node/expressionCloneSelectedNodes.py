import nuke

def main():
    nSel=nuke.selectedNodes()
    hero=nSel[-1]
    nonKnobs=['xpos','ypos','selected','name']

    for n in nSel[:-1]:
        for k in n.knobs():
            if not k in nonKnobs:
                n[k].setExpression(hero.name()+'.'+k)