import nuke,os

#create nuke menu
menuTitle="mlTools"
menubar = nuke.menu("Nuke")
m = menubar.addMenu("&"+menuTitle)

#set root to search for gizmos relative to this file
mlToolsPath=os.path.dirname(os.path.dirname(__file__))
nuke.pluginAddPath(mlToolsPath)


#set scripts root location
import mlScripts
scriptsRootDir=mlToolsPath+"/mlScripts"
nuke.pluginAddPath(scriptsRootDir)

print scriptsRootDir
print mlScripts

#os walk thru assets folder find py files
for path, dirs, files in os.walk(scriptsRootDir):
    files.sort()
    dirs.sort()
    for f in files:
        if not '#' in path and not '#' in f:
            if f.endswith(".py") and not f.startswith("__"):
                path=path.replace("\\","/")
                nuke.pluginAddPath(path)
                sPath=path+"/"+f
                #remove mlToolsPath from scriptPath
                localDirPath=sPath.split(menuTitle+'/')[-1].replace('/','.').replace('.py','')
                #prepend parent to path (mlTools.mlScripts.scriptName)
                localDirPath=menuTitle+'.'+localDirPath
                #print localDirPath
                filename=f.split(".")[0]
                __import__(localDirPath)
                menus=sPath.split(menuTitle)[-1].split("/")
                parentMenu=m
                for menu in menus[1:-1]:
                    if menu:
                        newMenu=parentMenu.addMenu("&"+menu)
                        parentMenu=newMenu
                parentMenu.addCommand(str(filename),localDirPath+".main()","") 
                if filename=="createDirsFromSelectedWrites":
                    parentMenu.addCommand(str(filename),localDirPath+".main()","F8")
                if filename=="createReadFromWrite":
                    parentMenu.addCommand(str(filename),localDirPath+".main()","^R")
                if filename=="matchBackdrops":
                    parentMenu.addCommand(str(filename),localDirPath+".main()","Ctrl+Alt+B")
                if filename=="GatherAovs_Arnold":
                    parentMenu.addCommand(str(filename),localDirPath+".main()","Ctrl+Alt+M")
                if filename=="toggleGizmoGroup":
                    parentMenu.addCommand(str(filename),localDirPath+".main()","Ctrl+Alt+G")
                if filename=="launchShotManager":
                    parentMenu.addCommand(str(filename),localDirPath+".main()","Ctrl+Alt+Z")
                if filename=="createExpressionNodesFromSelectedCryptoMulti":
                    parentMenu.addCommand(str(filename),localDirPath+".main()","Ctrl+Alt+E")
                if filename=="toggleActiveAovs":
                    parentMenu.addCommand(str(filename),localDirPath+".main()","Ctrl+Alt+W")
