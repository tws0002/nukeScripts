#include psyq
import sys
sys.path.append('P:/global/code/addons/general/python/psyq')
import psyq

def submitToQube(nukescript,writeNode,stepSize,chunkSize):
    start,end=scriptFirstLastFrames(nukescript)
    from psyq.engines.qube import QubeSubmitter
    import psyq.util as util

    from psyq.jobs.nuke.render_job import NukeRenderJob

    #renderJob=psyq.jobs.nuke.render_job.NukeRenderJob([writeNode])
    renderJob=NukeRenderJob([writeNode])
    
    #renderJob.app_name = nuke_util.get_app_name()
    #renderJob.app_version = nuke_util.get_app_version()
    renderJob.scene_path = nukescript
    renderJob.write_nodes = [writeNode]
    #renderJob.preview_priority = Priority.HIGHEST
    renderJob.priority = 1 #1low, 2Normal
    renderJob.chunk_size = chunkSize
    #renderJob.limit_threads = limit_threads
    #renderJob.tasks = tasks
    #renderJob.cpus = cpus
    #renderJob.memory_req = memory_req
    #renderJob.submit_blocked = submit_blocked
    #renderJob.notes = notes
    renderJob.frames = util.partition_range(start,end,stepSize,chunk_size=chunkSize,ordering='Ordering.INCREASING')
    #renderJob.preview_frames = []
    #renderJob.proxy_resolution = None
    #renderJob.proxy_enabled = False
    #renderJob.use_command = use_command
    #renderJob.debug = debug
    project=nukescript.split('/projects/')[-1].split('/')[0]
    seqName=nukescript.split('/sequences/')[-1].split('/')[0]
    filename=nukescript.split('/')[-1]
    renderJob.job_name = project+'/'+seqName+': '+filename+' <'+writeNode+'>'
    #renderJob.qube_cluster = self._get_qube_cluster()
    renderJob.submit()
    
    
def scriptFirstLastFrames(nukescript):
    fileObject=open(nukescript,"r")
    contents=fileObject.read()
    fileObject.close()
    contents=contents.split("Root {")[-1].split("\n}")[0]
    lines=contents.split("\n")
    first=0
    last=0
    for l in lines:
        if "first_frame" in l:
            first=int(l.split("first_frame ")[-1])
        if "last_frame" in l:
            last=int(l.split("last_frame ")[-1])
    return first,last