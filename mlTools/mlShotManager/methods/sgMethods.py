import nuke
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import shotgun_api3 as shotgun
SERVER_PATH = "https://psyop.shotgunstudio.com"
SCRIPT_USER = "mlTools"
SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"

def getShotgunData(PROJECT_ID):
    sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
    fields = ['id', 'entity', 'code', 'sg_status_list','open_notes','task_assignees','content']
    filters = [
                ['project', 'is', {"type": 'Project', 'id': PROJECT_ID}],
                    {
                        "filter_operator": "any",
                        "filters": [
                            ['content','is', 'Composite'],
                            ['content','is', 'Lighting']
                        ]
                    }
                ]
    tasks = sg.find('Task',filters,fields)
    shotNotes={}
    shotData={}
    for t in tasks:
        name=t['entity']['name']
        if not name in shotData.keys():
            shotData[name]=['','','','']
        if t['content']=='Composite':
            if len(t['task_assignees']):
                 shotData[name][0]=t['task_assignees'][0]['name']
            shotData[name][1]=t['sg_status_list']
        if t['content']=='Lighting':
            if len(t['task_assignees']):
                shotData[name][2]=t['task_assignees'][0]['name']
            shotData[name][3]=t['sg_status_list']
        #only keep comp notes
        if t['content']=='Composite':
            notes= t['open_notes']
            for note in notes:
                if not name in shotNotes.keys():
                    shotNotes[name]=[]
                nt=note['name']
                noteFormatted=str(note['id'])+'###'+nt.decode("ascii","ignore")
                if not noteFormatted in shotNotes[name]:
                    shotNotes[name].append(noteFormatted)
                    
    return shotNotes,shotData

def resetCompStatus(PROJECT_ID,Sequences):
    sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
    task = nuke.ProgressTask('reseting shotgun comp status:')
    for sq in Sequences:
        fields = ['id', 'code', 'sg_status_list','shots']
        filters = [['project','is', {'type':'Project','id':PROJECT_ID}],['code', 'is',sq]]
        seq = sg.find_one('Sequence',filters,fields)
        for shot in seq['shots']:
            fields = ['id', 'code', 'sg_status_list','open_notes']
            filters = [['id', 'is',shot['id']],['sg_status_list', 'is_not','omt']]
            sh= sg.find_one('Shot',filters,fields)
            if sh:
                fields = ['id', 'code', 'sg_status_list']
                filters = [ ['entity','is',{'type':'Shot','id':sh['id']}] ,  ['content','is', 'Composite' ],['sg_status_list', 'is_not','na'],['sg_status_list', 'is_not','wtg']]
                taskID = sg.find_one('Task',filters,fields)
                task.setMessage(sh['code'])
                if taskID:
                    sg.update('Task', taskID['id'], {'sg_status_list': 'cmpt'})
                    #if notes, change to problem
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
                                sg.update('Task', taskID['id'], {'sg_status_list': 'fkd'})
              
    del(task)

def createShotgunNote(PROJECT_ID,shotTable,sendTaskCombo):
    sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
    import getpass
    user=getpass.getuser()
    fields = ['id', 'name','login']
    filters = [['login', 'is',user]]
    userReturn = sg.find_one('HumanUser',filters,fields)
    #get shot id, task id
    #get shot
    shotName=shotTable.selectedItems()[0].text()
    filters = [['project','is', {'type':'Project','id':PROJECT_ID}],['code', 'is',shotName]]
    shot = sg.find_one('Shot',filters)
    task=sendTaskCombo.currentText()
    filters = [ ['entity','is',{'type':'Shot','id':shot['id']}] ,  ['content','is', task]]
    taskID = sg.find_one('Task',filters)
    content=self.notesTextEdit.toPlainText()
    for line in content.split('\n'):
        # enter data here for a note to create
        data = {'subject':task+' Note','content':line,'user':userReturn,'project': {"type":"Project","id": PROJECT_ID},'note_links':[{'type': 'Shot', 'id': shot['id'], 'name':shotName}],'tasks': [{'type': 'Task', 'id': taskID['id'], 'name': task}]}
        # create the note
        noteID = sg.create('Note',data)
    self.notesTextEdit.setPlainText("")
    self.shotgunNotes,self.shotgunShotData=sgMethods.getShotgunData(PROJECT_ID)
    if task=='Composite':
        sg.update('Task', taskID['id'], {'sg_status_list': 'fkd'})
    
def uploadThumbnail(PROJECT_ID,shot,path):
    sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
    fields = ['id', 'code', 'sg_status_list']
    project_id = PROJECT_ID
    filters = [
        ['project','is',{'type':'Project','id':project_id}],
        ['code','is',shot]
        ]
    asset= sg.find_one("Shot",filters,fields)
    id=asset['id']
    result = sg.upload_thumbnail("Shot",id,path)
    print path,'successfully uploaded'

def getShotgunFramerange(PROJECT_ID,shot):
    sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
    fields = ['id', 'code', 'sg_status_list','sg_cut_in','sg_cut_out']
    project_id = PROJECT_ID
    filters = [
        ['project','is',{'type':'Project','id':project_id}],
        ['code','is',shot]
        ]
    range= sg.find_one("Shot",filters,fields)
    cut_in=range['sg_cut_in']
    cut_out=range['sg_cut_out']
    return cut_in,cut_out