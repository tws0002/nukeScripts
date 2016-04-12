#P:\global\apps\TweakSoftware\RV\win64\rv-win64-x86-64-3.12.20\bin\rv.exe [ P:/projects/bloodbornehunt_7526P/sequences/rabbit/shots/rab0010/steps/composite/_renders/nuke/rab0010_composite_v001/comp/exr/rab0010_comp_v001.####.exr ] [ -in 110 -out 120 P:/projects/bloodbornehunt_7526P/sequences/rabbit/shots/rab0010/steps/composite/_renders/nuke/rab0010_composite_v001/comp/exr/rab0010_comp_v001.####.exr ] 
import subprocess
rvLocation='P:\global\apps\TweakSoftware\RV\win64\rv-win64-x86-64-3.12.20\bin\rv.exe'
def launchRvConform(shots):
    shotList=''
    for sh in shots:
        shotList+= sh+' '
        
    cmd= ['P:\\global\\apps\\TweakSoftware\\RV\\win64\\rv-win64-x86-64-3.12.20\\bin\\rvio.exe '+shotList]
    print cmd
    subprocess.Popen(cmd, shell=True)
    
    #print shotList
    #import psylaunch
    #psylaunch.launch_app("rv", args=[shotList], wait=True)