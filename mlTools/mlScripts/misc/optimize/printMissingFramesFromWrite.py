import os,nuke


def main():
    n=nuke.selectedNode()

    path=n['file'].value()

    parent= os.path.dirname(path)

    filelist=os.listdir(parent)
    filelist.sort()

    frameList=[]
    for i in filelist:
        frameList.append(i.split('.')[1])


    missing=''
    for i in range(495):
        if str(i).zfill(4) not in frameList:
            missing+=str(i)+','


    print missing