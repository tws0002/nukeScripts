import nuke,os,sys



#set root to search for gizmos relative to this file
mlToolPath=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))+'/mlTools'
#print mlToolPath
sys.path.append(mlToolPath)
import mlScripts


#CALLBACKS
def createWriteDir():
    file = nuke.filename(nuke.thisNode()) 
    dir = os.path.dirname( file ) 
    osdir = nuke.callbacks.filenameFilter( dir ) 
    try: 
        os.makedirs( osdir ) 
        return 
    except: 
        return
 
# Activate the createWriteDir function
nuke.addBeforeRender( createWriteDir )

def matchWriteVersionToFilename():
    if '_comp_' in nuke.root().name().split('/')[-1]:
        try:
            import re
            regex = re.compile("v[0-9]{3}")
            fileVers=regex.findall(nuke.root().name())[0]
            for w in nuke.allNodes('Write'):
                renderPath=w['file'].value()
                renderVers=regex.findall(renderPath)
                if len(renderVers)>0:
                    for v in renderVers:
                        renderPath=renderPath.replace(v,fileVers)
                w['file'].setValue(renderPath)
        except:
            pass


nuke.addOnScriptSave(matchWriteVersionToFilename)

def setLightingStatusComplete():
    import tank
    PROJECT_ID=tank.platform.current_engine().context.project['id']
    import shotgun_api3 as shotgun
    SERVER_PATH = "https://psyop.shotgunstudio.com"
    SCRIPT_USER = "mlTools"
    SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
    sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

    try:
        shotName=nuke.root().name().split('/')[-1].split('_')[0]
        #get shot
        fields = ['id', 'code', 'sg_status_list']
        filters = [['project','is', {'type':'Project','id':PROJECT_ID}],['code', 'is',shotName]]
        shot = sg.find_one('Shot',filters,fields)
        #get tasks
        fields = ['id', 'code', 'sg_status_list']
        filters = [ ['entity','is',{'type':'Shot','id':shot['id']}] ,  ['content','is', 'Lighting' ]]
        LightingtaskID = sg.find_one('Task',filters,fields)
        if LightingtaskID['sg_status_list'] =='rev':
            nuke.ask(shotName+' Lighting task is currently Pending Review\nDo you want to set to Complete?')
            #sg.update('Task', precompID['id'], {'sg_status_list': 'cmpt'})
            sg.update('Task', LightingtaskID['id'], {'sg_status_list': 'cmpt'})
            fields = ['id', 'code', 'sg_status_list']
            filters = [ ['entity','is',{'type':'Shot','id':shot['id']}] ,  ['content','is', 'Composite' ]]
            ComptaskID = sg.find_one('Task',filters,fields)
            sg.update('Task', ComptaskID['id'], {'sg_status_list': 'ip'})
    except:
        pass
        
def addSubmitter():
    sub=nuke.nodePaste(os.path.dirname(__file__)+'/submitterOveride.txt')
    sub['first_frame'].setValue(nuke.root()['first_frame'].value())
    sub['last_frame'].setValue(nuke.root()['last_frame'].value())
    
def overideSumbitter():
    menubar = nuke.menu("Nuke")
    sh=menubar.menu('Shotgun')
    render=sh.menu('Render')
    render.addCommand('Psyop Render Submit',"addCallbacks.addSubmitter()","")   

def addUserText():
    if 'composite' in nuke.root().name().split('/')[-1]:
        w=nuke.toNode('comp')
        txt=nuke.toNode('userText')
        import getpass
        user=getpass.getuser()
        if w and not txt:
            w.setXYpos(w.xpos(),w.ypos()+100)
            #add text info
            txt=nuke.nodes.Text()
            txt['name'].setValue('userText')
            txt['message'].setValue(user+'\n')
            txt['translate'].setValue([0,0])
            txt['size'].setValue(25)
            txt['box'].setValue([0,60,1280,0])
            txt['font'].setValue('C:/Windows/Fonts/arial.ttf')
            txt['xjustify'].setValue('right')
            txt['yjustify'].setValue('center')
            prior=w.input(0)
            txt.setInput(0,prior)
            w.setInput(0,txt)

        if txt:
            txt['message'].setValue(user+'\n')

def updateCamera():
    path=nuke.root().name()
    if 'composite' in path:
        camPublishDir=path.split("steps")[0]+"/publish/cache/camera/renderCam"
        if os.path.exists(camPublishDir):
            vers=os.listdir(camPublishDir)
            maxDir=max(vers)
            camDir=camPublishDir+'/'+maxDir+'/alembic'
            camFile=os.listdir(camDir)[0]
            importFile=camDir+'/'+camFile
            currentCam=nuke.toNode('Camera1')
            if currentCam:
                currentFile=currentCam['file'].value()
                if not currentFile==importFile:
                    q=nuke.ask('newer camera found, replace?')
                    if q:
                        currentCam['file'].setValue(importFile)


def addAssetGizmos():
    for n in nuke.allNodes('Group'):
        if 'addAssetGizmos' in n.knobs():
            n['addAssetGizmos'].execute()
                    
def removeStartRGBAChannel():
    keep=nuke.toNode('multiKeepChannels2')
    if keep:
        keep['channels2'].setValue('none')
                    
def startupCallbacks():
    if 'composite' in nuke.root().name().split('/')[-1]:
        #add gizmos to aovs
        #from mlScripts import gizmoTools
        #gizmoTools.findMissingAssetGizmos.main()
        addAssetGizmos()
        #setLightingStatusComplete()
        #overideSumbitter()
        #addUserText()
        updateCamera()
        #removeStartRGBAChannel()
    
    #delete viewers
    for v in nuke.allNodes('Viewer'):
        nuke.delete(v)
    for grp in nuke.allNodes('Group'):
        with grp:
            for v in nuke.allNodes('Viewer'):
                nuke.delete(v)
        #if grp.name()=='Submitter':
        #    nuke.delete(grp)
    #preferences
    nuke.toNode('preferences')['postage_stamp_mode'].setValue(1)
    nuke.toNode('preferences')['expression_arrows'].setValue(0)

nuke.addOnScriptLoad(startupCallbacks)