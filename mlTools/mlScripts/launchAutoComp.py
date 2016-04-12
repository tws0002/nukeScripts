import sys,nuke,os


def main():

    scriptsDir=os.path.dirname(__file__)
    parentScriptsDir=os.path.dirname(scriptsDir)
    autoCompDir=parentScriptsDir+'/mlAutoComp'


    sys.path.append(autoCompDir)
    from nukescripts import panels

    
    nuke.pluginAddPath(autoCompDir)

    
    import autoComp
    reload(autoComp)
    
    
    
    from autoComp import nukeAutoCompWindow
    
    
    
    win=panels.registerWidgetAsPanel('autoComp.nukeAutoCompWindow', 'autoComp', 'farts', True)
    pane=nuke.getPaneFor('Viewer.1')
    #pane = nuke.getPaneFor('Properties.1')
    #pane = nuke.getPaneFor('DAG.1')
    #win.show()
    win.addToPane(pane)