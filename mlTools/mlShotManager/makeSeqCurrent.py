import os,shutil,sys,re

parentDir=sys.argv[1]
newDir=sys.argv[2]

print "test"

regex = re.compile("v[0-9]{2,9}")

for i,file in enumerate(os.listdir(parentDir)):
    if not file.startswith('.'):
        vers=regex.findall(file)
        newFile=file
        for ver in vers:
            newFile=newFile.replace(ver,"current")
        shutil.copy(parentDir+"/"+file,newDir+"/"+newFile)
