import nuke,os,sys,subprocess

def main():
    toolSetsDir=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))+'/ToolSets'

    
    f="\\".join(toolSetsDir.split("/"))
    subprocess.Popen('explorer '+f)
    