import nuke

def main():
    for n in nuke.selectedNodes():
        data= n.metadata()['exr/dataWindow']
        if data[2]-data[0]<1:
            nuke.delete(n)