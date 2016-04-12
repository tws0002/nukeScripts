import nuke,os,sys

toolbar = nuke.menu("Nodes")
m=toolbar.menu('ToolSets')

#set root to search for gizmos relative to this file
toolSetsDir=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))+'/ToolSets'
toolSetsDir=toolSetsDir.replace('\\','/')
#print toolSetsDir
nuke.pluginAddPath(toolSetsDir)


for path, dirs, files in os.walk(toolSetsDir):
    files.sort()
    dirs.sort()
    for f in files:
        name= f.split('.')[0]
        fpath=path.replace('\\','/')+'/'+f
        menus=fpath.replace(toolSetsDir,"").split("/")
        parentMenu=m
        for menu in menus[:-1]:
            if menu:
                newMenu=parentMenu.addMenu("&"+menu)
                parentMenu=newMenu
        parentMenu.addCommand(name, 'nuke.loadToolset("%s")' % fpath, "")
#m.addCommand('refreshMenu','','')