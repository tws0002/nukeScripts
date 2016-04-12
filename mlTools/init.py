import nuke,os,sys,re,shutil

print 'ml_tools found'

def walkThruGizmos(directory):
    #os walk thru gizmoPath,folder names are menu names
    for path, dirs, files in os.walk(directory):
        dirs.sort()
        files.sort()
        for f in files:
            if f.endswith(".gizmo"):
                path=path.replace("\\","/")
                #avoid backup folders
                if not "_backup" in path:
                    nuke.pluginAddPath(path)
                    prntPath= path+'/'+f
                    #print prntPath.replace(directory,""),"found"



assetGizmosPath=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))+'/assetGizmos'
print "assetGizmosPath",assetGizmosPath
walkThruGizmos(assetGizmosPath)


mlGizmosPath=os.path.dirname(__file__)+'/mlGizmos'
walkThruGizmos(mlGizmosPath)


def makeCurrent():
    file = nuke.filename(nuke.thisNode(),nuke.REPLACE)
    scriptFilePath=nuke.root().name()

    if '/increments' in scriptFilePath:
        regex = re.compile("_[0-9]{3}[.]")
        incr=regex.findall(scriptFilePath)[0]
        scriptFilePath=scriptFilePath.replace('/increments','').replace(incr,'.')
    
    fileName=file.split('/')[-1]
    outName=fileName.split("_")[1]
    outExt=fileName.split(".")[-1]
    if outExt=='jpg':
        outExt='jpeg'
    scriptName=scriptFilePath.split('/')[-1]
    newFile=scriptFilePath.split('nuke')[0]+'_renders/nuke/'+scriptName.replace('.nk','')+'/'+outName+'/'+outExt+'/'+fileName
    
    print 'fileName',fileName
    print 'outName',outName
    print 'outExt',outExt
    print 'scriptName',scriptName
    
    regex = re.compile("_v[0-9]{2,9}")
    vers=regex.findall(file)
    for ver in vers:
        ver=ver.replace("_","")
        newFile=newFile.replace(ver,'current')

    print 'newFile',newFile
    
    thumbFile=file.replace('/exr/','/exr/.thumbs/').replace('.exr','.jpeg')   
    newThumbFile=newFile.replace('/exr/','/exr/.thumbs/').replace('.exr','.jpeg') 
        
    newDir = os.path.dirname(newFile)
    newThumbDir=os.path.dirname(newThumbFile)
    try:
        os.makedirs( newDir )
    except:
        pass
    try:
        os.makedirs( newThumbDir )
    except:
        pass
    try:
        shutil.copyfile(file,newFile)
    except:
        print 'noCopy file'
        pass
    try:
        shutil.copyfile(thumbFile,newThumbFile)
    except:
        print 'noCopy file'
        pass


