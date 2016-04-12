import nuke,os,sys

def main():

    menubar = nuke.menu("Nuke")
    menubar.removeItem('mlTools')
    menubar.removeItem('assetGizmos')
    print 'reloading scripts'
    import mlTools.menuTools.setupScripts
    reload(mlTools.menuTools.setupScripts)
    print 'reloading tools'
    import mlTools.menuTools.setupTools
    reload(mlTools.menuTools.setupTools)
    print 'reloading assetGizmos'
    import mlTools.menuTools.setupAssetGizmos
    reload(mlTools.menuTools.setupAssetGizmos)
    