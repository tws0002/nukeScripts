
from __future__ import with_statement
import nuke
import os,re
import nukescripts
import mlScripts

def getChannelsfromRead(node):
    chanDict={}
    for ch in node.channels():
        chName=ch.split('.')[0]
        chColor=ch.split('.')[-1]
        if not chName in chanDict:
            chanDict[chName]=[]
        chanDict[chName].append(chColor)    
    return chanDict

def findRendersFromDirectory(dir,tile):
    seqs=[]
    exists=[]
    print 'looking for sibling renders'
    for path, dirs, files in os.walk(dir):
        fList= nuke.getFileNameList(path,True)
        for item in fList:
            item=item.replace('exrsl','')
            if 'exr' in item:
                foundPath=path+'/'+item
                fileOnly=foundPath.split(' ')[0]
                regex = re.compile("[.][0-9]{2,9}")
                seqPad=regex.findall(fileOnly)
                for pad in seqPad:
                    fileOnly=fileOnly.replace(pad,".####")
                    foundPath=foundPath.replace(pad,".####")
                regex = re.compile("[h][0-9][v][0-9]")
                seqTile=regex.findall(fileOnly)
                if '####' in fileOnly:
                    if tile in fileOnly:
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
                    foundPath=path+'/'+item
                    fileOnly=foundPath.split(' ')[0]
                    regex = re.compile("[.][0-9]{2,9}")
                    seqPad=regex.findall(fileOnly)
                    for pad in seqPad:
                      fileOnly=fileOnly.replace(pad,".####")
                      foundPath=foundPath.replace(pad,".####")
                    if '####' in fileOnly:
                        if tile in fileOnly:
                            seqs.append(foundPath.replace('\\','/'))
                    
    commonPath=os.path.commonprefix(seqs)
    print commonPath
    #get commonName
    names=[]
    for each in seqs:
        names.append(each.split(' ')[0].split('/')[-1].split('.')[0])

    commonName=os.path.commonprefix(names)
    print commonName
    uniquePaths=[]
    uniqueNames=[]
    for seq in seqs:
        uniquePath=seq.replace(commonPath,"").split(" ")[0]
        #diffuse/_Hammer_Beauty_v043.diffuse.0157.exr
        frameNum=re.findall(r".[0-9]{4}.", uniquePath)
        #commented out to avoid placing #### at shot number
        #if len(frameNum)>0:
        #    uniquePath=uniquePath.replace(frameNum[-1],".####.")
        if not uniquePath in uniquePaths:
            uniquePaths.append(uniquePath)
            uniqueNames.append("".join(uniquePath.split("/")[-1].replace(commonName,"").split(".")[:-2]))#passName.####.exr
        
        
    return uniquePaths,uniqueNames,commonPath,commonName

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

def checkForNewAovs(thisNode):
    #insert redundant channels
    channels=['direct_specular','direct_specular_2','indirect_specular','indirect_specular2','indirect_specular_2']
    for ch in thisNode.channels():
        if not ch in channels:
            channels.append(ch.split(".")[0])
    parentDir="/".join(thisNode['file'].value().split("/")[:-1])
    if os.path.exists(parentDir):
        commonDir="/".join(thisNode['file'].value().split("/")[:-2])
        foundDirs= os.listdir(commonDir)
        print foundDirs
        newDirs=[]
        for d in foundDirs:
            if not d in channels:
                newDirs.append(d)
        if len(newDirs):
            #nuke.message("REBUILDING:\n"+"\n".join(newDirs))
            rebuildGroup(thisNode)
    
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
    node['label'].setValue(fName+'\n'+vers)
    checkForNewAovs(node)	

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
    node['label'].setValue(fName+'\n'+vers)
    checkForNewAovs(node)	
    
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
    node['label'].setValue(fName+'\n'+vers)
    checkForNewAovs(node)

def getChannelsAsDictionary(node):
    chanDict={}
    for ch in node.channels():
        chName=ch.split(".")[0]
        if chName not in chanDict.keys():
            chanDict[chName]=[ch]
        else:
            chanDict[chName].append(ch)
    return chanDict
        
    
def main():
    nSel=nuke.selectedNodes()
    nuke.selectAll() 
    nuke.invertSelection() 
    for n in nSel:
        n.setSelected(True)
        #get other passes from selected Read

        filename=n['file'].value().split('/')[-1]
        task = nuke.ProgressTask("getRenders")
        task.setMessage( 'processing %s' % filename )
        grp=nuke.collapseToGroup(n)
        myGroup=nuke.toNode(grp.name())
        n= nuke.allNodes('Read',group=myGroup)[0]
        n['name'].setValue("HeroRead")
        tile=''
        f=n['file'].value()
        regex = re.compile("[h][0-9]*[v][0-9]*")
        seqTile=regex.findall(f.split('/')[-1])
        for pad in seqTile:
            if not tile:
                tile=pad
        
        dir=os.path.dirname(f)
        seqData=findRendersFromDirectory(dir,tile)
        uniquePaths,uniqueNames,commonPath,commonName=seqData

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
        with grp:
            for p,each in enumerate(uniqueNames):
                if not each=="":
                    #create read node, set expressions
                    r=nuke.nodes.Read()
                    r['file'].setValue(commonPath+uniquePaths[p])
                    r['first'].setExpression("HeroRead.first")
                    r['last'].setExpression("HeroRead.last")
                    r['on_error'].setExpression("HeroRead.on_error")
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
                        each=each.replace('_'+tile,'')
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
            sh2=sh
            #add startRGBA channel
            sh=nuke.nodes.Shuffle()
            sh['in'].setValue('rgba')
            nuke.tcl('add_layer { '+'startRGBA'+' '+'startRGBA'+'.red '+'startRGBA'+'.green '+'startRGBA'+'.blue '+'startRGBA'+'.alpha}')
            sh['out'].setValue('startRGBA')
            sh.setInput(0,sh2)
            
            
            nuke.toNode('Output1').setInput(0,sh)
            nuke.toNode('Output1').setXYpos(sh.xpos(),sh.ypos()+80)
  
        createReadGroup(n,grp)
        del(task)
        grp['postage_stamp'].setValue(1)  
        grp.knobs()['User'].setLabel("MultiChannelRead")
        file=grp['file'].value()
        fName=file.split('/')[-1].split('.')[0]
        regex = re.compile("v[0-9]{2,9}")
        vers=regex.findall(file)[0]
        grp['label'].setValue(fName+'\n'+vers)

        
        #using 'scripts' in call because 'scripts' is currently called during import of all script files
        pyButtonLatest = nuke.PyScript_Knob('updateVersion', "updateToLatest", "mlScripts.arnoldGatherBty.updateLatest()")
        pyButtonLatest.setFlag(nuke.STARTLINE) 
        pyButtonUp = nuke.PyScript_Knob('verionUp', "versionUp", "mlScripts.arnoldGatherBty.versionUp()")
        pyButtonDown = nuke.PyScript_Knob('verionDown', "versionDown", "mlScripts.arnoldGatherBty.versionDown()")
        grp.addKnob(pyButtonLatest)
        grp.addKnob(pyButtonUp)
        grp.addKnob(pyButtonDown)
        nuke.selectAll() 
        nuke.invertSelection() 

def getConnections(node):
    connections={}
    for d in node.dependent():
        for i in range(d.inputs()):
            if d.input(i):
                if d.input(i).name()==node.name():
                    connections[d.name()]=i
    return connections
                    
def rebuildGroup(thisNode):

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
    grp=nuke.collapseToGroup(n)
    myGroup=nuke.toNode(grp.name())
    n= nuke.allNodes('Read',group=myGroup)[0]
    n['name'].setValue("HeroRead")

    f=n['file'].value()
    dir=os.path.dirname(f)
    seqData=findRendersFromDirectory(dir)
    uniquePaths,uniqueNames,commonPath,commonName=seqData

    #return message of number of sequences found
    #nuke.message(str(len(uniqueNames)) +' sequences found:'+"\n"+"\n".join(uniqueNames))

    nodes=[]
    sh=''
    priorShuffle=''
    with grp:
        for p,each in enumerate(uniqueNames):
            if not each=="":
                #create read node, set expressions
                r=nuke.nodes.Read()
                r['file'].setValue(commonPath+uniquePaths[p])
                r['first'].setExpression("HeroRead.first")
                r['last'].setExpression("HeroRead.last")
                r['on_error'].setExpression("HeroRead.on_error")
                r['name'].setValue(each)
        
                if 'Crypto' in each:
                    print each
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
        sh2=sh
        #add startRGBA channel
        sh=nuke.nodes.Shuffle()
        sh['in'].setValue('rgba')
        nuke.tcl('add_layer { '+'startRGBA'+' '+'startRGBA'+'.red '+'startRGBA'+'.green '+'startRGBA'+'.blue '+'startRGBA'+'.alpha}')
        sh['out'].setValue('startRGBA')
        sh.setInput(0,sh2)

        nuke.toNode('Output1').setInput(0,sh)
        nuke.toNode('Output1').setXYpos(sh.xpos(),sh.ypos()+80)

    createReadGroup(n,grp)
    del(task)
    grp['postage_stamp'].setValue(1)  
    grp.knobs()['User'].setLabel("MultiChannelRead")
    file=grp['file'].value()
    fName=file.split('/')[-1].split('.')[0]
    regex = re.compile("v[0-9]{2,9}")
    vers=regex.findall(file)[0]
    grp['label'].setValue(fName+'\n'+vers)

    grp.setXYpos(thisNode.xpos(),thisNode.ypos())
    #reconnect to old group connections
    connections=getConnections(thisNode)
    for c in connections.keys():
        nuke.toNode(c).setInput(connections[c],grp)

    nuke.delete(thisNode)
        

    #using 'scripts' in call because 'scripts' is currently called during import of all script files
    pyButtonLatest = nuke.PyScript_Knob('updateVersion', "updateToLatest", "mlScripts.arnoldGatherBty.updateLatest()")
    pyButtonLatest.setFlag(nuke.STARTLINE) 
    pyButtonUp = nuke.PyScript_Knob('verionUp', "versionUp", "mlScripts.arnoldGatherBty.versionUp()")
    pyButtonDown = nuke.PyScript_Knob('verionDown', "versionDown", "mlScripts.arnoldGatherBty.versionDown()")
    grp.addKnob(pyButtonLatest)
    grp.addKnob(pyButtonUp)
    grp.addKnob(pyButtonDown)
    nuke.selectAll() 
    nuke.invertSelection() 



    

