import nuke


def main():
    import shotgun_api3 as shotgun
    SERVER_PATH = "https://psyop.shotgunstudio.com"
    SCRIPT_USER = "mlTools"
    SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
    sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)



    for sq in ['ap','as','hd','ht','gb','gr','si','tg']:
        fields = ['id', 'code', 'sg_status_list','shots']
        filters = [['project','is', {'type':'Project','id':1674}],['code', 'is',sq]]
        seq = sg.find_one('Sequence',filters,fields)

        for shot in seq['shots']:
            fields = ['id', 'code', 'sg_status_list','open_notes']
            filters = [['id', 'is',shot['id']]]
            sh= sg.find_one('Shot',filters,fields)
            if not sh['sg_status_list'] == 'None':
                for n in sh['open_notes']:
                    id= n['id']
                    fields = ['sg_status_list','tasks','name']
                    filters = [['id', 'is',id]]
                    note = sg.find_one('Note',filters,fields)
                    for t in note['tasks']:
                        if 'Composite' in t['name']:
                            fields = ['id', 'code', 'sg_status_list']
                            filters = [ ['entity','is',{'type':'Shot','id':sh['id']}] ,  ['content','is', 'Composite' ]]
                            taskID = sg.find_one('Task',filters,fields)
                            #sg.update('Task', precompID['id'], {'sg_status_list': 'cmpt'})
                            sg.update('Task', taskID['id'], {'sg_status_list': 'fkd'})