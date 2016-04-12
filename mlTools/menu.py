from __future__ import with_statement
import sys, os
import nuke
 

#Defaults
nuke.knobDefault( 'Shuffle.label', '[value in]' )
nuke.knobDefault( 'OneView.label', '[value view]' )
nuke.knobDefault( 'Read.on_error', '3' )
#setup start resolution
#nuke.addFormat("1280 720 0 0 1280 720 1 720p")
nuke.knobDefault( 'Root.format', 'HD' )

mlToolsRoot=os.path.dirname(os.path.dirname(__file__))
nuke.pluginAddPath(mlToolsRoot)
import mlTools

mlToolsPath=os.path.dirname(__file__)
nuke.pluginAddPath(mlToolsPath)
import mlScripts

#import additional startup scripts
nuke.pluginAddPath(mlToolsPath+'/menuTools')
import setupScripts
import setupTools
import setupAssetGizmos
import addToolsetsMenu
import addCallbacks
#import addSGnotes
import addSnap3D


#add shot manager
shotManager_dir = os.path.join(os.path.dirname(__file__), 'mlShotManager')
sys.path.append(shotManager_dir)
import shotManager
#add cache manager
cacheManager_dir = os.path.join(os.path.dirname(__file__), 'mlCacheManager')
sys.path.append(cacheManager_dir)
import cacheManager
autoComp_dir = os.path.join(os.path.dirname(__file__), 'mlAutoComp')
sys.path.append(autoComp_dir)
import autoComp

def makeCurrent():
    import nuke, os,re,shutil
    file = nuke.filename(nuke.selectedNode(),nuke.REPLACE)
    dir = os.path.dirname( file )
    
    regex = re.compile("v[0-9]{2,9}")
    vers=regex.findall(file)
    
    newFile=file
    for ver in vers:
        newFile=newFile.replace(ver,'current')
    
    newDir = os.path.dirname( newFile )
    try:
        os.makedirs( newDir )
    except:
        pass
    shutil.copy(file,newFile)

