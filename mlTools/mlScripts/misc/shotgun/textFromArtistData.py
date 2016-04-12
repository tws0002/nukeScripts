import nuke

def main():
    for n in nuke.selectedNodes():
        message=''
        for k, v in n.metadata().iteritems():
            if 'artists' in k:
                task=k.split('/')[-1]
                artist=v
                message+= task+':'+artist+'\n'
        if message:
            txt=nuke.nodes.Text()
            txt['message'].setValue(message[:-1])
            dep=n.dependent()[0]
            txt.setInput(0,n)
            dep.setInput(0,txt)
            txt['font'].setValue('C:/Windows/Fonts/arial.ttf')
            txt['xjustify'].setValue('right')
            txt['yjustify'].setValue('bottom')
            txt['size'].setValue(30)
            txt['box'].setValue([0,0,nuke.root().width(),nuke.root().height()])