import nuke,os,sys

def main():

    toolbar = nuke.menu("Nodes")
    m=toolbar.menu('ToolSets')
    m.clearMenu()
    
    import nukescripts.toolsets
    nukescripts.toolsets.createToolsetsMenu(toolbar) 

    print 'reloading toolsets'
    import mlTools.menuTools.addToolsetsMenu
    reload(mlTools.menuTools.addToolsetsMenu)
            
            
            
            
            
            
