
from __future__ import with_statement
import nuke
import os,re
import nukescripts
import mlScripts

omitRenders=['single_scatter','_raw','sss_mix','Arnold_','_depthRemapped','_grunge','_pixelGrid','uAutoAsset','uAutoMaterial','uAutoObject','Z']

def getChannelsfromRead(node):
    chanDict={}
    for ch in node.channels():
        chName=ch.split('.')[0]
        chColor=ch.split('.')[-1]
        if not chName in chanDict:
            chanDict[chName]=[]
        chanDict[chName].append(chColor)    
    return chanDict

def findRendersFromDirectory(dir):
    seqs=[]
    exists=[]
    print 'looking for sibling renders'
    for path, dirs, files in os.walk(dir):
        fList= nuke.getFileNameList(path,True)
        for item in fList:
            item=item.replace('exrsl','')
            if 'exr' in item:
                foundOmit=0
                for omit in omitRenders:
                    if omit in item:
                        foundOmit=1
                if not foundOmit:
                    foundPath=path+'/'+item
                    fileOnly=foundPath.split(' ')[0]
                    regex = re.compile("[.][0-9]{2,9}")
                    seqPad=regex.findall(fileOnly)
                    for pad in seqPad:
                      fileOnly=fileOnly.replace(pad,".####")
                      foundPath=foundPath.replace(pad,".####")
                    if '####' in fileOnly:
                        if not fileOnly in exists:
                            #print foundPath
                            exists.append(fileOnly)
                            seqs.append(foundPath.replace('\\','/'))
                
    if len(seqs)<2:
        print 'looking for cousin renders'
        dir=os.path.dirname(dir)
        seqs=[]

        for path, dirs, files in os.walk(dir):
            fList= nuke.getFileNameList(path,True)
            for item in fList:
                item=item.replace('exrsl','')
                if 'exr' in item:
                    foundOmit=0
                    for omit in omitRenders:
                        if omit in item:
                            foundOmit=1
                    if not foundOmit:
                        foundPath=path+'/'+item
                        fileOnly=foundPath.split(' ')[0]
                        regex = re.compile("[.][0-9]{2,9}")
                        seqPad=regex.findall(fileOnly)
                        for pad in seqPad:
                          fileOnly=fileOnly.replace(pad,".####")
                          foundPath=foundPath.replace(pad,".####")
                        if '####' in fileOnly:
                            if not fileOnly in exists:
                                #print foundPath
                                exists.append(fileOnly)
                                seqs.append(foundPath.replace('\\','/'))
    if len(seqs)<2:
        nuke.message('No other sequences found for selected Read')
        return None
    commonPath=os.path.commonprefix(seqs)
    #print commonPath
    #get commonName
    names=[]
    for each in seqs:
        names.append(each.split(' ')[0].split('/')[-1].split('.')[0])

    commonName=os.path.commonprefix(names)
    print commonPath
    print commonName
    #print commonName
    uniquePaths=[]
    uniqueNames=[]
    version=''
    for seq in seqs:
        #remove version from filename Only
        seqPath="/".join(seq.split('/')[:-1])
        seqFile=seq.split('/')[-1]
        regex = re.compile("[_][v][0-9]{3}")
        version=regex.findall(seqFile)
        if len(version)>0:
            version=version[-1]
            seqFile=seqFile.replace(version,'')
            seq=seqPath+'/'+seqFile
        else:
            version=''
        
        uniquePath=seq.replace(commonPath,"").split(" ")[0]
        frameNum=re.findall(r".[0-9]{4}.", uniquePath)
        #commented out to avoid placing #### at shot number
        #if len(frameNum)>0:
        #    uniquePath=uniquePath.replace(frameNum[-1],".####.")
        if not uniquePath in uniquePaths:
            uniquePaths.append(uniquePath)
            uniqueNames.append("".join(uniquePath.split("/")[-1].replace(commonName,"").split(".")[:-2]))#passName.####.exr
        
        
    return uniquePaths,uniqueNames,commonPath,commonName,version

#create readGroup
def createReadGroup(node,grp):
    knobs=['file','cacheLocal','format','proxy','proxy_format','first','before','last','after','frame_mode','frame','origfirst','origlast','on_error','reload','colorspace','premultiplied','raw','auto_alpha','offset_negative_display_window']
    for k in knobs:
        l = nuke.Link_Knob(k)
        l.makeLink(node.name(), k)
        grp.addKnob( l )
        if not node.knobs()[k].getFlag(nuke.STARTLINE):
            l.clearFlag(nuke.STARTLINE)

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
            
            
            
#add new channel from input 1    
def shuffleCopyNewChannel(sh,newPass):
    nuke.tcl('add_layer { '+newPass+' '+newPass+'.red '+newPass+'.green '+newPass+'.blue '+newPass+'.alpha}')
    sh['in'].setValue('rgba')
    sh['in2'].setValue('none')
    sh['out'].setValue('none')
    sh['out2'].setValue(newPass)
    sh['black'].setValue('red')    
    sh['white'].setValue('green')    
    sh['red2'].setValue('blue') 
    sh['green2'].setValue('alpha')    
    sh['label'].setValue('[value out2]')
    
def consolidateChannels(node,passes,newPass):
    shufs=[node]
    for p in passes:
        sh=nuke.nodes.Shuffle()
        sh['in'].setValue(p)
        sh.setInput(0,node)
        sh.setXYpos(shufs[-1].xpos()+50,shufs[-1].ypos())
        shufs.append(sh)
    shufs.remove(node)
    m=multiPlus(shufs)
    shCopy=nuke.nodes.ShuffleCopy()
    shuffleCopyNewChannel(shCopy,newPass)
    shCopy.setInput(0,node)
    shCopy.setInput(1,m)
    prior=shCopy
    for p in passes:
        rem=nuke.nodes.Remove()
        rem['channels'].setValue(p)
        rem.setInput(0,prior)
        prior=rem
    return prior
        
def buildAssetMattes(node):
    channels=[]
    for ch in node.channels():
        if ch.startswith("m_"):
            channels.append(ch)
    assets={}
    for chan in channels:
        asset=chan.split("_")[1]
        if not asset in assets.keys():
            assets[asset]=[]
        if asset in chan:
            assets[asset].append(chan)
    prior=node
    for asset in assets.keys():
        expression="clamp("
        for chan in assets[asset]:
            if not ".alpha" in chan:
                #A+B(1-a)/b
                expression+=chan+" + "
        exp=nuke.nodes.Expression()
        exp['channel0'].setValue('rgba')
        exp['expr0'].setValue(expression[:-2]+")")
        exp.setInput(0,prior)

        shCopy=nuke.nodes.ShuffleCopy()
        nuke.tcl('add_layer { m_'+asset+'_all '+'m_'+asset+'_all'+'.red}')
        shCopy['in'].setValue('rgba')
        shCopy['in2'].setValue('none')
        shCopy['out'].setValue('none')
        shCopy['out2'].setValue('m_'+asset+'_all ')
        shCopy['black'].setValue('red')   
        shCopy.setInput(0,prior)
        shCopy.setInput(1,exp)
        prior=shCopy
    return prior

def buildHairMattes(node):
    hChans=[]
    for ch in node.channels():
        if ch.startswith("_h_"):
            hChans.append(ch)

    prior=node
    if len(hChans)>0:
        expression="clamp("
        for chan in hChans:
            if not ".alpha" in chan:
                #A+B(1-a)/b
                expression+=chan+" + "
        exp=nuke.nodes.Expression()
        exp['channel0'].setValue('rgba')
        exp['expr0'].setValue(expression[:-2]+")")
        exp.setInput(0,prior)

        shCopy=nuke.nodes.ShuffleCopy()
        nuke.tcl('add_layer { _h_all _h_all.red}')
        shCopy['in'].setValue('rgba')
        shCopy['in2'].setValue('none')
        shCopy['out'].setValue('none')
        shCopy['out2'].setValue('_h_all ')
        shCopy['black'].setValue('red')   
        shCopy.setInput(0,prior)
        shCopy.setInput(1,exp)
        prior=shCopy
    return prior    
    
def buildRemainderChannel(node):
    lightChans=[]
    for ch in node.channels():
        ch=ch.split('.')[0]
        if not ch in lightChans:
            lightChans.append(ch)

    nonAdditiveChans=['diffuse_color','beauty','startRGBA','rgba']
    expression='COLOR'
    for ch in lightChans:
        if not ch in nonAdditiveChans:
            if not 'light_group' in ch:
                expression+=' - '+ch+'.COLOR'
            
    #create expression node
    nuke.tcl('add_layer { remainderRGBA remainderRGBA.red remainderRGBA.green remainderRGBA.blue remainderRGBA.alpha }')
    exp=nuke.nodes.Expression()
    exp['channel0'].setValue('remainderRGBA.red -remainderRGBA.green -remainderRGBA.blue')
    exp['expr0'].setValue(expression.replace('COLOR','red'))
    exp['channel1'].setValue('-remainderRGBA.red remainderRGBA.green -remainderRGBA.blue')
    exp['expr1'].setValue(expression.replace('COLOR','green'))
    exp['channel2'].setValue('-remainderRGBA.red -remainderRGBA.green remainderRGBA.blue')
    exp['expr2'].setValue(expression.replace('COLOR','blue'))
    exp.setInput(0,node)
    return exp
    
def checkForNewAovs(thisNode):
    #insert redundant channels
    channels=['direct_specular','direct_specular_2','indirect_specular','indirect_specular2','indirect_specular_2']
    for ch in thisNode.channels():
        if not ch in channels:
            channels.append(ch.split(".")[0])
            
    parentDir="/".join(thisNode['file'].value().split("/")[:-1])
    if os.path.exists(parentDir):
    
        #check if siblings are directories, if so, this is a publish render, else a working render
        dirFound=False
        for d in os.listdir(parentDir):
            if os.path.isdir(parentDir+'/'+d):
                dirFound=True
                break
        if not dirFound:
            parentDir="/".join(thisNode['file'].value().split("/")[:-2])
        foundDirs= os.listdir(parentDir)

        newDirs=[]
        for d in foundDirs:
            foundOmit=0
            for omit in omitRenders:
                if omit in d:
                    foundOmit=1
            if not foundOmit:
                if os.path.isdir(parentDir+'/'+d):
                    if not d in channels:
                        newDirs.append(d)
        if len(newDirs):
            nuke.message("REBUILDING:\n"+"\n".join(newDirs))
            buildGrp(thisNode,1)
            from mlScripts import gizmoTools
            gizmoTools.findMissingAssetGizmos.main()
    
def versionUp():
    node=nuke.thisNode()
    with node:
        for n in nuke.allNodes('Read'):
            n.setSelected(1)
        mlScripts.utils.version.version_up()
        print 'updated'
    file=node['file'].value()
    fName=file.split('/')[-1].split('.')[0]
    regex = re.compile("v[0-9]{2,9}")
    vers=regex.findall(file)[0]
    #node['label'].setValue(fName+'\n'+vers)
    #checkForNewAovs(node)	

def versionDown():
    node=nuke.thisNode()
    with node:
        for n in nuke.allNodes('Read'):
            n.setSelected(1)
        mlScripts.utils.version.version_down()
        print 'updated'
    file=node['file'].value()
    fName=file.split('/')[-1].split('.')[0]
    regex = re.compile("v[0-9]{2,9}")
    vers=regex.findall(file)[0]
    #node['label'].setValue(fName+'\n'+vers)
    #checkForNewAovs(node)	
    
def updateLatest():
    node=nuke.thisNode()
    with node:
        for n in nuke.allNodes('Read'):
            n.setSelected(1)
        mlScripts.utils.version.version_latest()
        print 'updated'
    file=node['file'].value()
    fName=file.split('/')[-1].split('.')[0]
    regex = re.compile("v[0-9]{2,9}")
    vers=regex.findall(file)[0]
    #node['label'].setValue(fName+'\n'+vers)
    checkForNewAovs(node)

def main():
    nSel=nuke.selectedNodes()
    nuke.selectAll() 
    nuke.invertSelection() 
    for n in nSel:
        #get other passes from selected Read
        buildGrp(n,0)

def getChannelsAsDictionary(node):
    chanDict={}
    for ch in node.channels():
        chName=ch.split(".")[0]
        if chName not in chanDict.keys():
            chanDict[chName]=[ch]
        else:
            chanDict[chName].append(ch)
    return chanDict
        
def getConnections(node):
    connections={}
    for d in node.dependent():
        for i in range(d.inputs()):
            if d.input(i):
                if d.input(i).name()==node.name():
                    connections[d.name()]=i
    return connections
    
def buildGrp(n,rebuild):
    filename=n['file'].value().split('/')[-1]
    
    if rebuild:
        thisNode=n
        n=nuke.nodes.Read()
        n['file'].setValue(thisNode['file'].value())
        n['first'].setValue(thisNode['first'].value())
        n['last'].setValue(thisNode['last'].value())
        nuke.selectAll() 
        nuke.invertSelection() 
        n.setSelected(True)
        #get other passes from selected Read

        filename=n['file'].value().split('/')[-1]

    task = nuke.ProgressTask("getRenders")
    task.setMessage( 'processing %s' % filename )

    f=n['file'].value()
    dir=os.path.dirname(f)
    seqData=findRendersFromDirectory(dir)

    if seqData:

        n.setSelected(True)
        grp=nuke.collapseToGroup(n)
        myGroup=nuke.toNode(grp.name())
        n= nuke.allNodes('Read',group=myGroup)[0]
        n['name'].setValue("HeroRead")
    
        uniquePaths,uniqueNames,commonPath,commonName,version=seqData
        
        
        #ignore cryptoMatte in lightingRenders
        
        if not 'uBasic' in filename:
            uBasicRemove=[]
            for uN in uniqueNames:
                print uN
                if uN.startswith('u'):
                    print 'remove'
                    uBasicRemove.append(uN)
            for uR in uBasicRemove:
                uniqueNames.remove(uR)
        print uniqueNames
        #return message of number of sequences found
        #nuke.message(str(len(uniqueNames)) +' sequences found:'+"\n"+"\n".join(uniqueNames))
        
        nodes=[]
        sh=''
        priorShuffle=''
        cryptoMaterialExists=0
        with grp:
            for p,each in enumerate(uniqueNames):
                if not each=="":
                    #create read node, set expressions
                    r=nuke.nodes.Read()
                    r['file'].setValue(commonPath+uniquePaths[p].replace('.####',version+'.####'))#add version back into uniquePath
                    #r['file'].setValue(commonPath+uniquePaths[p])
                    r['first'].setExpression("HeroRead.first")
                    r['last'].setExpression("HeroRead.last")
                    r['on_error'].setValue(3)
                    r['name'].setValue(each)
                    ref=nuke.nodes.Reformat()
                    ref.setInput(0,r)
                    
                    if 'Crypto' in each:
                        #store cryptoAsset for metadata fetching
                        if 'CryptoAsset' in each:
                            cryptoMaterialExists=r
                        chanDict=getChannelsAsDictionary(r)
                        for ch in chanDict.keys():
                        
                            #create shuffleCopy and setup
                            sh=nuke.nodes.ShuffleCopy()
                            sh.setInput(1,ref)
                            if not priorShuffle:
                                sh.setInput(0,n)
                            if priorShuffle:
                                sh.setInput(0,priorShuffle)
                            sh['in'].setValue(ch)
                            sh['in2'].setValue('rgba')
                            nuke.tcl('add_layer { '+ch+' '+ch+'.red '+ch+'.green '+ch+'.blue '+ch+'.alpha}')
                            sh['out'].setValue('none')
                            sh['out2'].setValue(ch)
                            #sh['red'].setValue('red')
                            #sh['green'].setValue('green')
                            #sh['blue'].setValue('blue')
                            #sh['alpha'].setValue('alpha')
                            sh['black'].setValue('red')    
                            sh['white'].setValue('green')    
                            sh['red2'].setValue('blue') 

                            sh['green2'].setValue('alpha') 
 
                            sh['label'].setValue('[value out2]')

                            #add to array
                            priorShuffle=sh
                            nodes.append(r)
                    
                    else:
                        #create shuffleCopy and setup
                        sh=nuke.nodes.ShuffleCopy()
                        sh.setInput(1,ref)
                        if not priorShuffle:
                            ref=nuke.nodes.Reformat()
                            ref.setInput(0,n)
                            sh.setInput(0,ref)
                            heroRef=ref
                        if priorShuffle:
                            sh.setInput(0,priorShuffle)
                        sh['in'].setValue('rgba')
                        sh['in2'].setValue('rgba')
                        nuke.tcl('add_layer { '+each+' '+each+'.red '+each+'.green '+each+'.blue '+each+'.alpha}')
                        sh['out'].setValue('none')
                        sh['out2'].setValue(each)
                        #sh['red'].setValue('red')
                        #sh['green'].setValue('green')
                        #sh['blue'].setValue('blue')
                        #sh['alpha'].setValue('alpha')
                        sh['black'].setValue('red')    
                        sh['white'].setValue('green')    
                        sh['red2'].setValue('blue') 
                        if 'rgba.alpha' in r.channels():
                            sh['green2'].setValue('alpha') 
                        else:
                            sh['green2'].setValue('alpha2')    
                        sh['label'].setValue('[value out2]')

                        #add to array
                        priorShuffle=sh
                        nodes.append(r)
                        
                    task.setProgress( int( float(p) / len(uniqueNames) *100) )
            #avoid consolidate if not lighting pass reads
            if 'direct_specular.red' in sh.channels():
                c=consolidateChannels(sh,['direct_specular','direct_specular_2'],'spec')    
                sh=consolidateChannels(c,['indirect_specular','indirect_specular2','indirect_specular_2'],'indirect_spec')    
            #create combined asset mattes 
            sh=buildAssetMattes(sh)
            #build hair Mattes
            sh=buildHairMattes(sh)
            sh2=sh
            #add startRGBA channel
            sh=nuke.nodes.Shuffle()
            sh['in'].setValue('rgba')
            nuke.tcl('add_layer { '+'startRGBA'+' '+'startRGBA'+'.red '+'startRGBA'+'.green '+'startRGBA'+'.blue '+'startRGBA'+'.alpha}')
            sh['out'].setValue('startRGBA')
            sh.setInput(0,sh2)
            if 'spec.red' in sh.channels():
                sh=buildRemainderChannel(sh)
            copyBB=nuke.nodes.CopyBBox()
            copyBB.setInput(0,sh)
            copyBB.setInput(1,heroRef)
            if cryptoMaterialExists:
                metaNode=nuke.nodes.CopyMetaData()
                metaNode.setInput(0,copyBB)
                metaNode.setInput(1,cryptoMaterialExists)
                copyBB=metaNode
            
            nuke.toNode('Output1').setInput(0,copyBB)
            nuke.toNode('Output1').setXYpos(copyBB.xpos(),copyBB.ypos()+80)
  
        createReadGroup(n,grp)
        del(task)
        grp['postage_stamp'].setValue(1)  
        grp.knobs()['User'].setLabel("MultiChannelRead")
        file=grp['file'].value()
        fName=file.split('/')[-1].split('.')[0]
        regex = re.compile("v[0-9]{2,9}")
        vers=regex.findall(file)[0]
        grp['label'].setValue('[lindex [split [lindex [split [value file] /] end] .] 0] ')

        if rebuild:
            grp.setXYpos(thisNode.xpos(),thisNode.ypos())
            #reconnect to old group connections
            connections=getConnections(thisNode)
            for c in connections.keys():
                nuke.toNode(c).setInput(connections[c],grp)
            nuke.delete(thisNode)
        
        #using 'scripts' in call because 'scripts' is currently called during import of all script files
        #pyButtonLatest = nuke.PyScript_Knob('updateVersion', "updateToLatest", "mlScripts.GatherAovs_Arnold.updateLatest()")
        #pyButtonLatest.setFlag(nuke.STARTLINE) 
        pyButtonUp = nuke.PyScript_Knob('verionUp', "versionUp", "import mlPipeline\nfrom mlPipeline import ml_pipelineTools\nreload(mlPipeline.ml_pipelineTools)\nmlPipeline.ml_pipelineTools.versionUp()")
        pyButtonDown = nuke.PyScript_Knob('verionDown', "versionDown", "import mlPipeline\nfrom mlPipeline import ml_pipelineTools\nreload(mlPipeline.ml_pipelineTools)\nmlPipeline.ml_pipelineTools.versionDown()")
        #grp.addKnob(pyButtonLatest)
        grp['on_error'].setValue(3)
        grp.addKnob(pyButtonUp)
        grp.addKnob(pyButtonDown)
        nuke.selectAll() 
        nuke.invertSelection() 
