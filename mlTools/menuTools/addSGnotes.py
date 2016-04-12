import nuke,nukescripts
    
    
#############################notes pane###############################
class ShotgunNotesPanel(nukescripts.PythonPanel):
    def __init__(self):
        nukescripts.PythonPanel.__init__(self, 'Shotgun notes', 'mlavoy')
        # CREATE KNOBS
        #open page in shotgun
        self.openShotgunButton= nuke.PyScript_Knob('openShotgun','openShotgun')
        #button for getting notes
        self.getNotesButton= nuke.PyScript_Knob('getNotes','getNotes')
        #update shotgun note status
        self.updateShotgunButton= nuke.PyScript_Knob('updateShotgun','updateShotgun')

        # ADD KNOBS
        self.addKnob(self.openShotgunButton)
        self.addKnob(self.getNotesButton)
        self.addKnob(self.updateShotgunButton)
        self.addKnob(nuke.Text_Knob('Notes','Notes'))
        self.notes=[]
        self.checkKnobs={}

    def knobChanged(self, knob):
        if knob.name() == "openShotgun":
            self.openShotgun()
        if knob.name() == "getNotes":
            self.getNotes()
        if knob.name() == "updateShotgun":
            self.updateNotes()
        if knob.name()[0].isdigit():
            tog=0
            if knob.name() in self.notes and tog==0:
                print 'removing note'
                self.notes.remove(knob.name())
                tog=1
                print self.notes
            if not knob.name() in self.notes and tog==0:
                print 'adding note'
                self.notes.append(knob.name())
                tog=1
                print self.notes


    def openShotgun(self):
        nuke.message('alert')

    def getNotes(self):
        for k in self.knobs():
            if k[0].isdigit():
                self.removeKnob(self.checkKnobs[k])
        self.notes=[]
        self.checkKnobs={}
    

        shotName=nuke.root().name().split('/')[-1].split('_')[0]
        #setup shotgun
        import shotgun_api3 as shotgun
        SERVER_PATH = "https://psyop.shotgunstudio.com"
        SCRIPT_USER = "mlTools"
        SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
        sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
        #get shot
        fields = ['id', 'code', 'sg_status_list','open_notes']
        filters = [['project','is', {'type':'Project','id':1431}],['code', 'is',shotName]]
        shot = sg.find_one('Shot',filters,fields)
        compNotes={}
        
        for n in shot['open_notes']:
            id= n['id']
            fields = ['sg_status_list','tasks','name']
            filters = [['id', 'is',id]]
            note = sg.find_one('Note',filters,fields)
            for t in note['tasks']:
                if 'Composite' in t['name']:
                    compNotes[id]=n['name']
        for nt in compNotes.keys():
            #line=nuke.String_Knob('test','',str(compNotes[nt]))
            #self.addKnob(line)
            ch=nuke.Boolean_Knob(str(nt),str(compNotes[nt]))
            self.addKnob(ch)
            self.checkKnobs[str(nt)]=ch
            ch.setFlag(nuke.STARTLINE) 

    def updateNotes(self):
        #setup shotgun
        import shotgun_api3 as shotgun
        SERVER_PATH = "https://psyop.shotgunstudio.com"
        SCRIPT_USER = "mlTools"
        SCRIPT_KEY  = "e0078c0e80f09ee7a76de2c25afce6bd34a5bc601f598d446daf6a8e848d9089"
        sg = shotgun.Shotgun(SERVER_PATH, SCRIPT_USER, SCRIPT_KEY)
        for n in self.notes:
            sg.update('Note', int(n), {'sg_status_list': 'clsd'})      
        for k in self.knobs():
            if k[0].isdigit():
                self.removeKnob(self.checkKnobs[k])

def addSNPanel():
    global snPanel
    snPanel = ShotgunNotesPanel()
    return snPanel.addToPane()

paneMenu = nuke.menu('Pane')
paneMenu.addCommand('ShotgunNotes', addSNPanel)
nukescripts.registerPanel('mlavoy', addSNPanel)

