import nuke

def main():
    nuke.getInput("localDrive?","C:")
    paths=[]
    for n in nuke.selectedNodes("Read"):
        paths.append(n['file'].value())
    
        