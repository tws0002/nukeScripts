def openInExplorer(self,*args):
    selShot=self.shotTable.selectedItems()[0].text()
    shotDir=self.nukeProjectPath.replace("shotNum",selShot)
    import subprocess
    f="\\".join(shotDir.split("/"))
    subprocess.Popen('explorer '+f)