import nuke,os,sys

#create nuke menu
menuTitle="assetGizmos"
menubar = nuke.menu("Nuke")
m = menubar.addMenu("&"+menuTitle)

#set root to search for gizmos relative to this file
assetGizmos=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))+'/assetGizmos'

nuke.pluginAddPath(assetGizmos)


#os walk thru gizmoPath,folder names are menu names
for path, dirs, files in os.walk(assetGizmos):
    dirs.sort()
    files.sort()
    for f in files:
        if f.endswith(".gizmo"):
            path=path.replace("\\","/")
            nuke.pluginAddPath(path)
            gPath=path+"/"+f
            menus=gPath.split(menuTitle)[-1].split("/")
            parentMenu=m
            for menu in menus[1:-1]:
                if menu:
                    newMenu=parentMenu.addMenu("&"+menu)
                    parentMenu=newMenu
            giz=f.split(".")[0]
            parentMenu.addCommand(str(giz),"nuke.createNode("+"\""+giz+"\""+")","")

