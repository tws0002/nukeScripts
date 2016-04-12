import nuke,os


#remote satellite process for publishing renders within shots folders


def findExrsFromDirectory(dir,alreadyExisting):
    seqs=[]
    for path, dirs, files in os.walk(dir):
		if not path in alreadyExisting:
			fList= nuke.getFileNameList(path,True)
			for item in fList:
				item=item.replace('exrsl','')
				if 'exr' in item and "####" in item and 'beauty' in item:
					dirModTime=os.path.getmtime(path)
					foundPath=path+'/'+item+':'+str(dirModTime)
					seqs.append(foundPath.replace('\\','/'))
    return seqs

def updatePublishedFile(shot):
    #get publish file
    publishFile=threeD_RendersPath.replace("shotNum",shot)+"/published.txt"
    if not os.path.exists(publishFile):
        fileObject=open(publishFile,"w")
        fileObject.close()
    #get published seqs   
    fileObject=open(publishFile,"r")
    contents=fileObject.read()
    fileObject.close()
    existingSeqs=contents.split("\n")
	existingDirs=[]
	for exSeq in existingSeqs:
		existingDirs.append("/".join(exSeq.split("/"))[:-4])
	
    #compare seq to published
    newSeqs=[]
    for seq in findExrsFromDirectory(threeD_RendersPath.replace("shotNum",shot),existingDirs):
        if not seq in existingSeqs:
            newSeqs.append(seq)
            
    #write to publish file    
    if len(newSeqs)>0:
        fileObject=open(publishFile,"a")
        for ns in newSeqs:
            fileObject.write(ns+"\n")
        fileObject.close()
    return newSeqs
          
