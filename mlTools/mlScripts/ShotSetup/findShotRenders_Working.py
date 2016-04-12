import nuke,nukescripts,os,re



def main():
    class TestPanel(nukescripts.PythonPanel):
        def __init__(self):
            super(TestPanel,self).__init__('select beauty renders to import' )

            
            filepath=nuke.root().name()
            path=filepath.partition('composite')[0]
            rendersPath=path+'/lighting/_renders/maya'


            seqs=[]
            exists=[]
            topDirs=os.listdir(rendersPath)
            dirLength=len(topDirs)
            task = nuke.ProgressTask("getRenders")
            switch=0
            tops=[]
            searchDirs=[rendersPath+'::0']
            for dir in searchDirs:
                directory=dir.split('::')[0]
                level=int(dir.split('::')[1])+1
                if level==1:
                    tops=os.listdir(directory)
                for i,d in enumerate(tops):
                    if d in directory:
                        task.setMessage( 'processing %s' % d )
                        task.setProgress( int( float(i) / len(tops) *100) )
                if level<=4:
                    for file in os.listdir(directory):
                        if os.path.isdir(directory+'/'+file):
                            searchDirs.append(directory+'/'+file+'::'+str(level))
                if level>4 and directory.split('/')[-1]=='beauty':
                    fList= nuke.getFileNameList(directory,True)
                    for item in fList:
                        item=item.replace('exrsl','')
                        if 'exr' in item:
                            #if 'beauty_beauty' in item or 'utility_beauty' in item:
                            if '_beauty.' in item:
                                foundPath=directory+'/'+item
                                regex = re.compile("[.][0-9]*[.]")
                                pad=regex.findall(foundPath)
                                for p in pad:
                                    foundPath=foundPath.replace(str(p),".####.")
                                fileOnly=foundPath.split(' ')[0]
                                if not fileOnly in exists:
                                    exists.append(fileOnly)
                                    seqs.append(foundPath.replace('\\','/'))


            seqs.sort()
            
            seqDict={}
            for seq in seqs:
                seqSplit=seq.split('/maya/')[1]
                seqSplit=seqSplit.split('/')
                renderLayer=seqSplit[1]
                if not renderLayer in seqDict.keys():
                    seqDict[renderLayer]=[]
                seqDict[renderLayer].append(seq)
            
            dictKeys=seqDict.keys()
            dictKeys.sort()
            
            for key in dictKeys:
                t=nuke.Text_Knob(key)
                t.setFlag(nuke.STARTLINE)
                self.addKnob(t)
                for seq in seqDict[key]:
                    version=seq.split('/maya/')[-1].split('/')[0]
                    tabLength=40-len(version)
                    tab=""
                    for i in range(tabLength):
                        tab+=" "
                    file=seq.split('/')[-1]
                    b=nuke.Boolean_Knob(seq,version+tab+file)
                    b.setFlag(nuke.STARTLINE)
                    self.addKnob(b) 

                


            
            self._makeOkCancelButton()

            del(task)
        
    p = TestPanel()
    result=p.showModalDialog()

    if result:
        for k in p.knobs():
            if p.knobs()[k].Class()=='Boolean_Knob':
                if p.knobs()[k].value():
                    path=k.split(" ")[0]
                    r=nuke.nodes.Read()
                    r['file'].setValue(path)
                    if len(k.split(" "))>0:
                        first=k.split(" ")[1].split('-')[0]
                        last=k.split(" ")[1].split('-')[1]
                        r['first'].setValue(int(first))
                        r['last'].setValue(int(last))