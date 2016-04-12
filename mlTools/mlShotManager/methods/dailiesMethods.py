import nuke
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import datetime,os,subprocess
ffmpegLocation=os.path.dirname(os.path.dirname(__file__))+'/ffmpeg.exe'

def writeToDailies(shotTable):
    selShot=shotTable.selectedItems()[0].text()
    date= str(datetime.date.today()).split("-")
    dateFormatted=date[0]+'-'+date[1]+'-'+date[2]

    path=nuke.root().name()
    user='comp'
    dailiesDir="/".join(path.split("/")[0:3])+"/dailies/"+dateFormatted+"/comp/"

    try:
        os.makedirs(dailiesDir)
    except WindowsError:
        pass

    
    startFrame='0101'
    frmRate='24'
    renderLocation=self.getSelectionFromNukeTreeSeqsOut()[0]
    output=dailiesDir+renderLocation.split("/")[-1].split(".")[0]+".mov"


    #cmd= [ffmpegLocation +' -f image2 -start_number '+startFrame+' -i '+self.twoD_RendersPath.replace("shotNum",selShot)+'/'+renderLocation+' -c:v libx264 -g 1 -tune stillimage -crf 18 -bf 0 -vf fps='+frmRate+' -pix_fmt yuv420p -s 960x540 '+output] 
    cmd= [ffmpegLocation +' -f image2 -start_number '+startFrame+' -i '+self.twoD_RendersPath.replace("shotNum",selShot)+'/'+renderLocation+' -c:v libx264 -g 1 -tune stillimage -crf 18 -bf 0 -r '+frmRate+' -pix_fmt yuv420p -s 1920x1080 '+output] 
    subprocess.Popen(cmd, shell=True)

    print self.getSelectionFromNukeTreeSeqsOut()[0],"compressing"