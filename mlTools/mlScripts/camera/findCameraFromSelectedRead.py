import nuke,os
import tank
from pprint import pprint

def get_publish_metadata(img_path):
    img_dir = img_path if os.path.isdir(img_path) else os.path.dirname(img_path)
    engine = tank.platform.current_engine()
    tkinst = engine.tank
    pipeline_cfg = tkinst.pipeline_configuration
    publish_type = pipeline_cfg.get_published_file_entity_type()
    context = tkinst.context_from_path(img_dir)
    template_name = "%s_publish" % (context.entity['type'].lower())
    publish_template = engine.get_template_by_name(template_name)
    fields = publish_template.get_fields(img_dir)

    filters = [
    ["entity",            "is", context.entity],
    ["sg_component_name", "is", fields['publish_name']],
    ["sg_component_type", "is", "image/lighting"],
    ["version_number",    "is", fields['version']],
    ]

    try:
        results = tkinst.shotgun.find(publish_type, filters, ["sg_metadata"])[0]
        metadata = eval(results.get('sg_metadata', '{}'))
    except:
        metadata = {}
    return metadata
    
def get_publish_metadata_value(img_path, key):
    return get_publish_metadata(img_path).get(key)
    
    
def get_origin_scene(img_path):
    return get_publish_metadata_value(img_path, "origin_scene")

def main():
    msg=''
    selSeq=nuke.selectedNode()['file'].value()
    msg+="ORIGIN SCENE:\n"
    msg+=get_publish_metadata_value(selSeq, "origin_scene")+'\n'
    #pprint (get_publish_metadata_value(selSeq, "origin_scene"))
    refs=get_publish_metadata_value(selSeq, "references")
    maFiles=[]
    abcFiles=[]
    for ref in refs:
        if 'camera' in ref:
            cam=nuke.nodes.Camera2()
            cam['file'].setValue(ref.replace('\\','/'))
            cam['read_from_file'].setValue(True)
            cam['label'].setValue('[lrange [split [value file] /] 11 11]')
        if '.mb' in ref or '.ma' in ref:
            maFiles.append(ref.replace('\\','/'))
        if '.abc' in ref:
            abcFiles.append(ref.replace('\\','/'))
    msg+="\n"        
    msg+="Alembic Cache References:\n"
    for abc in abcFiles:
        msg+=abc+'\n'
    msg+="\n"  
    msg+="Maya File References:\n"
    for ma in maFiles:
        msg+=ma+'\n'
    #pprint (get_publish_metadata_value(selSeq, "published_from"))
    #pprint (get_publish_metadata_value(selSeq, "aovs"))
    #pprint (get_publish_metadata_value(selSeq, "unpublished_aov"))
    print msg


