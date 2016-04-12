import sys,nuke,os


def main():

    scriptsDir=os.path.dirname(__file__)
    parentScriptsDir=os.path.dirname(scriptsDir)
    shotManagerDir=parentScriptsDir+'/mlShotManager'

    #del sys.modules['shotManager']
    sys.path.append(shotManagerDir)
    from nukescripts import panels

    
    nuke.pluginAddPath(shotManagerDir)

    
    import shotManager
    reload(shotManager)
    
    
    
    from shotManager import NukeTestWindow
    
    
    
    win=panels.registerWidgetAsPanel('shotManager.NukeTestWindow', 'shotManager', 'farts', True)
    pane=nuke.getPaneFor('Viewer.1')
    #pane = nuke.getPaneFor('Properties.1')
    #pane = nuke.getPaneFor('DAG.1')
    #win.show()
    win.addToPane(pane)