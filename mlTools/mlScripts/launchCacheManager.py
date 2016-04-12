import sys,nuke,os
def main():
    scriptsDir=os.path.dirname(__file__)
    parentScriptsDir=os.path.dirname(scriptsDir)
    cacheManagerDir=parentScriptsDir+'/mlCacheManager'
    #del sys.modules['shotManager']
    sys.path.append(cacheManagerDir)
    from nukescripts import panels
    nuke.pluginAddPath(cacheManagerDir)
    import cacheManager
    reload(cacheManager)
    
    from cacheManager import NukeTestWindow



    win=panels.registerWidgetAsPanel('cacheManager.NukeTestWindow', 'cacheManager', 'farts', True)
    pane = nuke.getPaneFor('Properties.1')
    #pane = nuke.getPaneFor('DAG.1')
    #win.show()
    win.addToPane(pane)