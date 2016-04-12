import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

def openInExplorer(shotTable,scriptPath,seqSelection):
    selSeq=seqSelection.currentText()
    selShot=shotTable.selectedItems()[0].text()
    shotDir=scriptPath.replace("shotNum",selShot).replace("sequenceName",selSeq)
    print selShot,shotDir
    import subprocess
    f="\\".join(shotDir.split("/"))
    subprocess.Popen('explorer '+f)