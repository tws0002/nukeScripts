import subprocess
import nuke

def main():
    for each in nuke.selectedNodes():
    
        if "file" in each.knobs():
    
            f="\\".join(each['file'].value().split("/")[:-1])
            subprocess.Popen('explorer '+f)