import os,shutil,sys,re

fromDir=sys.argv[1]
toDir=sys.argv[2]
version=sys.argv[3]
if os.path.exists(toDir):
    shutil.rmtree(toDir)
shutil.copytree(fromDir,toDir)
for root, dirs, files in os.walk(toDir, topdown=False):
    for f in files:
        if version in f:
            oldname=root+'/'+f
            newname=oldname.replace(version,'current')
            os.rename(oldname,newname)