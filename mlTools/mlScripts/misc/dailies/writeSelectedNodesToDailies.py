import nuke,sys,subprocess,os
import datetime,string


def main():
    nSel=nuke.selectedNodes()

    frmRate=str(nuke.root().fps())



    ffmpegLocation=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))+'/mlShotManager/ffmpeg.exe'
    #print ffmpegLocation
    
    #create dailies directory
    if nSel:
        date= str(datetime.date.today()).split("-")
        dateFormatted=date[0]+'-'+date[1]+'-'+date[2]
        
        path=nuke.root().name()
        user='comp'
        dailiesDir="/".join(path.split("/")[0:3])+"/dailies/"+dateFormatted+"/comp/"
        
        try:
            os.makedirs(dailiesDir)
        except WindowsError:
            pass

    #send to ffmpeg
    for n in nSel:
        
        if 'file' in n.knobs():
            path=n['file'].value()
            parentDir="/".join(path.split("/")[:-1])
            range=nuke.getFileNameList(parentDir)[0].split(" ")[-1]
            first,last=range.split("-")
            startFrame=first.zfill(4)
            output=dailiesDir+path.split("/")[-1].split(".")[0]+".mov"
            nuke.message('writing '+output)
            #cmd= [ffmpegLocation +' -f image2 -start_number '+startFrame+' -i '+path+' -c:v libx264 -g 1 -tune stillimage -crf 18 -bf 0 -vf fps='+frmRate+' -pix_fmt yuv420p -s 960x540 '+output] 
            cmd= [ffmpegLocation +' -f image2 -start_number '+startFrame+' -r '+frmRate+' -i '+path+' -c:v libx264 -g 1 -tune stillimage -crf 18 -bf 0 -r '+frmRate+' -force_fps -pix_fmt yuv420p -s 1920x1080 '+output]
    
            subprocess.Popen(cmd, shell=True)