import nuke,os

def main():
    #get latest camera
    path=nuke.root().name()
    camPublishDir=path.split("steps")[0]+"/publish/cache/camera/renderCam"
    vers=os.listdir(camPublishDir)
    maxDir=max(vers)
    camDir=camPublishDir+'/'+maxDir+'/alembic'
    camFile=os.listdir(camDir)[0]
    importFile=camDir+'/'+camFile
    cam=nuke.nodes.Camera2()
    cam['read_from_file'].setValue(True)
    cam['file'].setValue(importFile)
    cam['label'].setValue('[lrange [split [value file] /] 11 11]')
    #cam['read_from_file'].setValue(False)
    return cam