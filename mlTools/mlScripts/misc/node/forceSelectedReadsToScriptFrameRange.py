import nuke

def main():
    first,last= str(nuke.root().frameRange()).split('-')
    for n in nuke.selectedNodes('Read'):
        n['first'].setValue(int(first))
        n['last'].setValue(int(last))
        n['on_error'].setValue(3)