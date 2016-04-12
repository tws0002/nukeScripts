import nuke
import getpass
import shotgun_api3 as shotgun
SERVER_PATH = "https://psyop.shotgunstudio.com"
SCRIPT_USER = "mlTools"
SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)

def main():
    shotName=nuke.root().name().split('/')[-1].split('_')[0]
    #get shot
    fields = ['id', 'code', 'sg_status_list']
    filters = [['project','is', {'type':'Project','id':1674}],['code', 'is',shotName]]
    shot = sg.find_one('Shot',filters,fields)
    #get tasks
    fields = ['id', 'code', 'sg_status_list']
    filters = [ ['entity','is',{'type':'Shot','id':shot['id']}] ,  ['content','is', 'Lighting' ]]
    taskID = sg.find_one('Task',filters,fields)
    sg.update('Task', taskID['id'], {'sg_status_list': 'cmpt'})
    #sg.update('Task', taskID['id'], {'sg_status_list': 'ip'})
    nuke.message(shotName+' status: complete\n User: '+user)