import nuke
import re,os

def main():
    allReads= allNodesAllGroups("Read")
    found=[]
    for n in allReads:
        if n.Class()=='Read':
            currentPath=n['file'].value()
            newPath=findLatest(currentPath)
            if newPath:
                n['file'].setValue(newPath)
                found.append(n['file'].value())
    if found:
        nuke.message("updated Reads:\n"+"\n".join(found))

def findLatest(origPath):
    regex = re.compile("v[0-9]{2,9}")
    vers=regex.findall(origPath)
    for i in range(1,10)[::-1]:
        path=origPath
        up=int(i)
        for ver in vers:
            numsOnly=ver[1:]
            pad=len(numsOnly)
            val=int(numsOnly)
            newVer='v'+str((val+up)).zfill(pad)
            path=path.replace(ver,newVer)
        dirPath='/'.join(path.split('/')[:-1])
        if os.path.exists(dirPath):
            return path
            
            
def allNodesAllGroups(NodeClass):
    found=[]
    for grp in nuke.allNodes('Group'):
        with grp:
            for n in nuke.allNodes(NodeClass):
                found.append(n)
    return found


