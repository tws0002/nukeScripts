import nuke,os,sys

def main():
    toolSetsDir=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    
    p = nuke.Panel('create Toolset from Selection')
    p.addSingleLineInput('toolsetName', '')
    dirs=' '.join(os.listdir(toolSetsDir+'/ToolSets'))
    p.addEnumerationPulldown('directory', dirs)
    ret = p.show()
    
    if ret:
        nuke.createToolset(p.value('directory')+'/'+p.value('toolsetName'),-1,toolSetsDir)
    