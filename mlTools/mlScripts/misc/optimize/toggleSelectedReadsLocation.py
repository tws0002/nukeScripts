from __future__ import with_statement
import os,shutil,nuke



def main():
    #set root knob if not exists
    if not( 'fileLocation' in nuke.root().knobs()):
        dirsLoc=nuke.String_Knob('fileLocation','fileLocation')
        dirsLoc.setValue('server')
        nuke.root().addKnob(dirsLoc)

    print nuke.root()['fileLocation'].value()

    #get all reads
    readPaths = []
    readNodes=[]
    groups=nuke.allNodes("Group")
    reads=nuke.selectedNodes("Read")
    for r in reads:
        path=r['file'].value()
        if not path in readNodes:
            readPaths.append(path)
            readNodes.append(r)
    for grp in groups:
        if 'file' in grp.knobs():
            readNodes.append(grp)
        with grp:
            reads=nuke.allNodes("Read")
            for r in reads:
                path=r['file'].value()
                if not path in readNodes:
                    readPaths.append(path)
                    readNodes.append(r)

    #set values
    incr=int(nuke.activeViewer().node()['frame_increment'].value())
    driveLetter = 'C:/'
    if os.path.exists('D:/'):
        driveLetter = 'D:/'
    if os.path.exists('E:/'):
        driveLetter = 'E:/'


    if nuke.root()['fileLocation'].value()=='server':
        task = nuke.ProgressTask( 'copying files:')
        for x,each in enumerate(readNodes):
            path=each['file'].value()
            if task.isCancelled():
                break
            
            for i in range(each['first'].value(),each['last'].value()+1,incr):
                framePath=path.replace("%04d",str(i).zfill(4))
                framePath=framePath.replace("%03d",str(i).zfill(3))
                task.setMessage( 'processing %s' % framePath )
                if not driveLetter in framePath:
                    copyTo = framePath.replace('P:/' , driveLetter)
                    if not os.path.exists(copyTo) and os.path.exists(framePath):
                        dir= "/".join(copyTo.split("/")[:-1])
                        if not os.path.exists(dir):
                            os.makedirs(dir)
                        shutil.copy(framePath , copyTo)
            
                newRead = path.replace('P:/' , driveLetter)
                each.knob('file').setValue(newRead)
                each.knob('tile_color').setValue(0x70ff52ff)
                each['on_error'].setValue(3)
            task.setProgress( int( float(x) /len(readNodes) *100) )
        del(task)
        nuke.root()['fileLocation'].setValue('local')

    else:
        task = nuke.ProgressTask( 'switching files:')
        for x,each in enumerate(readNodes):
            path=each['file'].value()
            if task.isCancelled():
                break
            newRead = path.replace(driveLetter,'P:/')
            each.knob('file').setValue(newRead)
            each.knob('tile_color').setValue(0)
            each['on_error'].setValue(0)
            task.setProgress( int( float(x) /len(readNodes) *100) )
        del(task)
        nuke.root()['fileLocation'].setValue('server')
