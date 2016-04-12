import nuke,random,os,mlScripts,sys



#set root to search for gizmos relative to this file
assetGizmos=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))+'/assetGizmos'
nuke.pluginAddPath(assetGizmos)

#templates directory
rebuildTemplate=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))+'/templates'
#print rebuildTemplate


LUTSPath=assetGizmos+"/LUT"
#wid=nuke.toNode('preferences').knob('GridWidth').value()

def multiPlus(nSel):
    m=nuke.nodes.Merge2()
    m['operation'].setValue('plus')
    m['output'].setValue('rgb')
    offset=0
    bdX = min([node.xpos() for node in nSel])
    #avg=0
    for i,p in enumerate(nSel):
        if(i==2):
            offset=1
        m.setInput(i+offset,p)
        #avg+=p.xpos()
    m.setXYpos(bdX,nSel[0].ypos()+100)
    return m

def mergeDivide(node,divider):
    m=nuke.nodes.Merge2()
    m['operation'].setValue('divide')
    m.setInput(0,node)
    m.setInput(1,node)
    m['output'].setValue('rgb')
    m['Bchannels'].setValue(divider)
    m.setXYpos(node.xpos(),node.ypos()+40)
    return m

def unPremultNode(node):
    unp=nuke.nodes.Unpremult()
    unp.setXYpos(node.xpos(),node.ypos()+40)
    unp.setInput(0,node)
    unp.setName(node.name()+"_unpremult")
    return unp

def buildBackdrop(nodes):
    # Calculate bounds for the backdrop node. 
    bdX = min([node.xpos() for node in nodes]) 
    bdY = min([node.ypos() for node in nodes]) 
    bdW = max([node.xpos() + node.screenWidth() for node in nodes]) - bdX 
    bdH = max([node.ypos() + node.screenHeight() for node in nodes]) - bdY 
    # Expand the bounds to leave a little border. Elements are offsets for left, top, right and bottom edges respectively 
    left, top, right, bottom = (-100, -80, 200, 40) 
    bdY += top     
    bdW += (right - left) 
    bdH += (bottom - top) 
    backdrop = nuke.nodes.BackdropNode(xpos = bdX-20, bdwidth = bdW, ypos = bdY, bdheight = bdH, tile_color = int((random.random()*(13 - 11))) + 11, note_font_size=42) 
    return backdrop

def setLayer(node,layer):
    layKnob = nuke.String_Knob('layer')
    #layKnob.setVisible(False)
    node.addKnob(layKnob)
    node['layer'].setValue(layer)
    #node.knob('User').setFlag(nuke.INVISIBLE)

def findAssetGizmos(node,aov):
    #nuke.toNode(node.name()).setSelected(1)
    foundGizmos=[]
    assets=[]
    assetDirs=os.listdir(assetGizmos)
    
    for chan in node.channels():
        ch=chan.split("_")
        if "m" in ch:
            if not ch[1] in assets:
                assets.append(ch[1])
    for asset in assets:
        if asset in assetDirs:
            if asset+"_"+aov+".gizmo" in os.listdir(assetGizmos+'/'+asset):
                foundGizmos.append(asset+"_"+aov)
    print foundGizmos
    return foundGizmos

def findLUTGizmos():
    import re
    filename=nuke.root().name().split("/")[-1]
    regex = re.compile("[0-9]{2,9}")
    digits=regex.findall(filename)[0]
    seqName=filename.split(digits)[0]
    
    foundGizmos=[]
    assets=[]
    LUTS=os.listdir(LUTSPath)

    for lut in LUTS:
        if lut == "LUT_"+seqName+".gizmo":
            foundGizmos.append("LUT_"+seqName)
    return foundGizmos

def buildAOV(node,title,passes,operation,divide,lastMerge,color,function):
    prior=node
    shufs=[]
    for p in passes:
        sh=nuke.nodes.Shuffle()
        sh['in'].setValue(p)
        sh['label'].setValue('[value in]')
        sh.setInput(0,prior)
        if node.Class()!="Shuffle":
            sh.setXYpos(prior.xpos(),prior.ypos()+200)
        if node.Class()=="Shuffle":
            sh.setXYpos(prior.xpos()+400,prior.ypos())
        if prior!=node:
            sh.setXYpos(prior.xpos()+200,prior.ypos())
        prior=sh
        shufs.append(sh)
    allNodes=shufs
    nodes=[]
    if divide:
        for sh in shufs:
            m=mergeDivide(sh,"diffuse_color")
            nodes.append(m)
    else:
        for sh in shufs:
            u=unPremultNode(sh)
            nodes.append(u)
    allNodes.extend(nodes)
    m=multiPlus(nodes)
    gizmos=findAssetGizmos(m,title)
    lastNode=m
    for g in gizmos:
        giz=nuke.createNode(g)
        nuke.selectAll() 
        nuke.invertSelection() 
        giz.setInput(0,lastNode)
        giz.setXYpos(lastNode.xpos(),lastNode.ypos()+30)
        lastNode=giz
         
    noOp=nuke.nodes.NoOp()
    noOp.setName(title+"_OUT")
    noOp.setInput(0,lastNode)
    noOp.setXYpos(lastNode.xpos(),lastNode.ypos()+400)
    merge=nuke.nodes.Merge2()
    merge.setInput(0,noOp)
    merge.setInput(1,noOp)
    if lastMerge:
        merge.setInput(0,lastMerge)
    merge.setName(title+"_MERGE")
    merge['operation'].setValue(operation)
    merge['output'].setValue('rgb')
    merge.setXYpos(noOp.xpos(),noOp.ypos()+80)
    allNodes.append(m)
    allNodes.append(noOp)
    allNodes.append(merge)
    b=buildBackdrop(allNodes)
    if m.inputs()<2:
        nuke.delete(m)
    b.setName(title+"_BACKDROP")
    b['label'].setValue(title)
    b['tile_color'].setValue(int(color))
    noOpKnob = nuke.String_Knob('noOp')
    mergeKnob = nuke.String_Knob('merge')
    b.addKnob(noOpKnob)
    b.addKnob(mergeKnob)

    b['noOp'].setValue(noOp.name())
    b['merge'].setValue(merge.name())
    if function:
        globals()[function](noOp)
    return prior,merge

def matchBackdropInitialHeight():
    bds=[]
    for bd in nuke.allNodes("BackdropNode"):
        if "_BACKDROP" in bd.name():
            bds.append(bd)
    bdMin = max([bd['bdheight'].value() for bd in bds]) 
    for bd in bds:
        bd['bdheight'].setValue(bdMin)
        noOp=nuke.toNode(bd['noOp'].value())
        m=nuke.toNode(bd['merge'].value())
        noOp['xpos'].setValue(bd.xpos()+20)
        noOp['ypos'].setValue(bd.ypos()+bd['bdheight'].value()-120)
        m['xpos'].setValue(bd.xpos()+20)
        m['ypos'].setValue(bd.ypos()+bd['bdheight'].value()-30)
        

def getNodeAvgPos(nodes):
    x=0
    y=0
    for n in nodes:
        x+=n.xpos()
        y+=n.ypos()
    avgx=x/float(len(nodes))
    avgy=y/float(len(nodes))
    return avgx,avgy
        
def setupAtmos(noOp):
    unpr= noOp.input(0)
    nd=nuke.nodes.ML_normalizeDepth()
    nd.setInput(0,unpr)
    g=nuke.nodes.Grade()
    g['gamma'].setValue(.2)
    g['white'].setValue(.7)
    g['name'].setValue("atmos_Grade")
    g.setInput(0,nd)
    noOp.setInput(0,g)
    nd['script'].execute()
    
def createBackplate(node,far):
    try:
        cam=mlScripts.camera.getLatestCamera.main()
    except:
        cam=nuke.nodes.Camera2()
    cam.setXYpos(node.xpos()-800,node.ypos())
    card=nuke.nodes.Card2()
    card.setXYpos(cam.xpos()+100,cam.ypos())
    ch=nuke.nodes.CheckerBoard2()
    ch.setXYpos(card.xpos(),card.ypos()-80)
    card.setInput(0,ch)
    fr=nuke.nodes.FrameHold()
    fr.setInput(0,cam)
    #fr['disable'].setValue(True)
    first,last=nuke.root()['first_frame'].value(),nuke.root()['last_frame'].value()
    import math
    mid=math.floor((first+last)/2)
    fr['first_frame'].setValue(mid)
    fr.setXYpos(cam.xpos(),cam.ypos()+80)
    trans=nuke.nodes.TransformGeo()
    trans.setInput(0,card)
    trans.setInput(1,fr)
    trans.setXYpos(card.xpos(),card.ypos()+80)
    trans['uniform_scale'].setExpression("("+cam.name()+".haperture/"+cam.name()+".focal)*-translate.z")
    trans['translate'].setValue(float(far)*10,2)
    scan=nuke.nodes.ScanlineRender()
    scan['MB_channel'].setValue("backward")
    scan.setXYpos(trans.xpos()+100,trans.ypos())
    scan.setInput(2,cam)
    scan.setInput(1,trans)
    vb=nuke.nodes.VectorBlur()
    vb.setInput(0,scan)
    vb['uv'].setValue('backward')   
    vb.setXYpos(scan.xpos(),scan.ypos()+80)
    return vb

def insertToNewChannel(sh,chanName,inChannel):
    nuke.tcl('add_layer { '+chanName+' '+chanName+'.red '+chanName+'.green '+chanName+'.blue '+chanName+'.alpha}')
    sh['in'].setValue(inChannel)
    sh['out'].setValue(chanName)
    sh['red'].setValue('red')    
    sh['green'].setValue('green')    
    sh['blue'].setValue('blue') 
    sh['alpha'].setValue('alpha')    
    sh['label'].setValue('[value out]')


    
def setViews(nSel):
    #nuke.deleteView('main')
    #set viewNames
    p = nuke.Panel('viewNames(select back to front):')
    panelKnobs=[]
    viewOrder=[]
    for i,n in enumerate(nSel):
        name="MG"
        lableInfo=''
        if i>1:
            name="MG"+str(i)
        if i==0:
            name="FG"
            lableInfo='(front)'
        if i==len(nuke.selectedNodes())-1:
            name="BG"
            lableInfo='(back)'
        p.addSingleLineInput(n.name()+lableInfo, name)
        panelKnobs.append(n.name()+lableInfo)
    ret = p.show()
    if ret:
        for pKnob in panelKnobs:
            #nuke.addView(p.value(pKnob))
            viewOrder.append(p.value(pKnob))
    return ret,viewOrder

def forceSingleView():
    for node in nuke.allNodes():
        if 'views' in node.knobs():
            node['views'].setValue(nuke.views()[0])

def getShotgunTaskData(scriptShot):
    import shotgun_api3 as shotgun
    SERVER_PATH = "https://psyop.shotgunstudio.com"
    SCRIPT_USER = "mlTools"
    SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
    PROJECT_ID=1674
    sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
    filters = [['project','is', {'type':'Project','id':PROJECT_ID}],['code', 'is',scriptShot]]
    shot = sg.find_one('Shot',filters)

    fields = ['id', 'entity', 'code', 'sg_status_list','task_assignees','content','tasks']
    filters = [
                ['project', 'is', {"type": 'Project', 'id': PROJECT_ID}],
                ['entity', 'is', {"type": 'Shot', 'id': shot['id']}]
                ]
    tasks = sg.find('Task',filters,fields)
    taskDict={}
    for t in tasks:
        taskDict[t['content']]=t['task_assignees'][0]['name']  
        
    return taskDict

def createMetaDataNode(taskDict,node):
    meta=nuke.nodes.ModifyMetaData()
    meta.setInput(0,node)
    metaString='{set frame [frame]} '
    #for task in taskDict.keys():
    #    metaString+='{set Key Value} '.replace('Key','artists/'+task.replace(' ','')).replace('Value',taskDict[task].replace(' ',''))
    meta['metadata'].fromScript(metaString)
    return meta
    
def main():





    if nuke.root().name()=='Root':
        nuke.message('save file in shot directory before running script')
        
        
    scriptRoot=nuke.root().name().split("/nuke/")[0]
    scriptName=nuke.root().name().split("/nuke/")[1].split(".nk")[0]
    scriptShot=scriptName.split("_")[0]
    scriptVersion=scriptName.split("_")[-1]
        
    nSel=nuke.selectedNodes()
    if len(nSel) and nuke.root().name()!='Root':
        continu,viewOrder=setViews(nSel)
        #viewOrder.reverse()
        if not continu:
            return
        #jv=nuke.nodes.JoinViews()
        
        #for i,n in enumerate(nSel):
        #    jv.setInput(i,n)
        
        jvx,jvy=getNodeAvgPos(nSel)
        #jv.setXYpos(jvx,jvy+200)
        #get min depth from renders
        tmpM=multiPlus(nSel)
        tmpM['Achannels'].setValue('uPointCamera')
        tmpM['Bchannels'].setValue('uPointCamera')
        nd=nuke.nodes.ML_normalizeDepth()
        nd.setInput(0,tmpM)
        nd['script'].execute()
        far=nd['whitepoint'].value()
        if 'inf' in str(far):
            far=-100000
        nuke.delete(tmpM)
        nuke.delete(nd)
        
        
        #deselect
        nuke.selectAll() 
        nuke.invertSelection() 
        backView=''
        rebuilds=[]
        #add rebuild group from template
        for i,v in enumerate(nSel):
            rebuild=nuke.nodePaste(rebuildTemplate)
            rebuild.setInput(0,v)
            rebuild.setXYpos(v.xpos(),v.ypos()+100)
            rebuild.setName(viewOrder[i]+'_Rebuild')
            rebuilds.append(rebuild)
            if not backView:
                backView=rebuild
            #place far in atmosGrade
            with rebuild:
                depth=nuke.toNode('ML_normalizeDepth1')
                depth['whitepoint'].setValue(far)
        
        

        nuke.selectAll() 
        nuke.invertSelection() 

        viewOrder=rebuilds
        viewOrder.reverse()
        priorMerge=''
        m=viewOrder[0]
        for i,view in enumerate(viewOrder):
            if i<len(viewOrder)-1:
                m=nuke.nodes.Merge2()
                m['operation'].setValue('over')
                m['also_merge'].setValue('all')
                m.setXYpos(view.xpos(),view.ypos()+600)
            if i>0:
                d=nuke.nodes.Dot()
                d.setInput(0,view)
                d.setXYpos(view.xpos()+40,priorMerge.ypos())
                priorMerge.setInput(1,d)
            if not priorMerge:
                m.setInput(0,view)
            if priorMerge and i<len(viewOrder)-1:
                m.setInput(0,priorMerge)
                m.setXYpos(priorMerge.xpos(),priorMerge.ypos()+100)
            priorMerge=m
        #add lightwrap
        lw=nuke.nodes.chromaLumaLightwrap()
        lw.setInput(0,priorMerge)
        lw.setXYpos(priorMerge.xpos(),priorMerge.ypos()+200)
        #add backplate setup
        vb=createBackplate(lw,far)
        #connect backplate
        d=nuke.nodes.Dot()
        d.setInput(0,vb)
        d.setXYpos(vb.xpos()+400,vb.ypos())
        lw.setInput(1,d)
        m=nuke.nodes.Merge2()
        m.setInput(0,lw)
        m.setInput(1,d)
        m['operation'].setValue('under')
        m.setXYpos(lw.xpos(),d.ypos())
        m['also_merge'].setValue('all')
        #add prelut shuffle
        #sh=nuke.nodes.Shuffle()
        #sh.setInput(0,m)
        #sh.setXYpos(m.xpos(),m.ypos()+400)
        #insertToNewChannel(sh,"preLut","rbga")
        #sh['in'].setValue("rgba")
        #add LUT gizmo, Why does attah to camera?
        #lutGizmo=findLUTGizmos()
        #lastNode=sh
        #for g in lutGizmo:
        #    giz=nuke.createNode(g)
        #    giz.setXYpos(lastNode.xpos(),lastNode.ypos()+200)
        #    giz.setInput(0,lastNode)
        #    lastNode=giz
        #add keepChannels
        keep=nuke.nodes.multiKeepChannels()
        keep.setInput(0,m)
        #keep['channels2'].setValue('startRGBA')
        #keep['channels3'].setValue('preLut')
        #add grain
        grain=nuke.nodes.LumaGrain2()
        grain.setInput(0,keep)
        
        #add text info
        #txt=nuke.nodes.Text()
        #txt['message'].setValue('[ lrange [split [ basename [ value root.name ] ] . ] 0 0 ]\n[frame]')
        #txt['translate'].setValue([0,0])
        #txt['size'].setValue(50)
        #txt['box'].setValue([0,120,1920,0])
        #txt.setInput(0,grain)
        #txt['font'].setValue('C:/Windows/Fonts/arial.ttf')
        #txt['xjustify'].setValue('left')
        #txt['yjustify'].setValue('center')
        
        #add metadata
        #taskDictionary=getShotgunTaskData(scriptShot)
        taskDictionary={}
        metaDataNode=createMetaDataNode(taskDictionary,grain)
        
        #add crop
        cr=nuke.nodes.Crop()
        cr['crop'].setValue(0)
        cr.setInput(0,metaDataNode)
        cr['box'].setValue([0,0,nuke.root().width(),nuke.root().height()])
        
        #add writeOut
        w=nuke.nodes.Write()
        w.setInput(0,cr)
        w.setName('comp')
        w['channels'].setValue('all')
        w['file_type'].setValue('exr')
        renderPath=scriptRoot+'/_renders/nuke/'+scriptName+'/'+w.name()+'/exr/'+scriptShot+'_'+w.name()+'_'+scriptVersion+'.%04d.exr'
        w['file'].setValue(renderPath)
        w['metadata'].setValue('all metadata')
        #forceSingleView()
        from mlScripts import gizmoTools
        gizmoTools.findMissingAssetGizmos.main()
