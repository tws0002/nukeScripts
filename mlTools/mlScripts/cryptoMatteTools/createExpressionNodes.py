import sys
sys.path.append('P:/global/code/addons/nuke/plugins/standard/7.0/cryptomatte/1.0.0')
import cryptomatte_utilities as cu
import nuke
reload(cu)


def makeCryptoExpression(readNode, names):
    namesToHash = [];
    if type(names) is str:
        namesToHash.append(names);
    else:
        namesToHash = names

    cryptomatte_channels = cu._identify_cryptomattes_in_channels(readNode)
    ID_list = []
    for name in namesToHash:
        ID_list.append( cu.automatte_djb2_hash(name) )

    expression = cu._build_multi_expression(cryptomatte_channels, ID_list)
    return expression

    id_name_pairs = cu.parse_metadata(grp)
    metadataAssets = [x[1] for x in id_name_pairs]
    
def main():
    node = nuke.selectedNode()

    id_name_pairs = cu.parse_metadata(node)
    metadataAssets = [x[1] for x in id_name_pairs]

    for m in metadataAssets:
        name=m
        if '/obj/' in m:
            name=m.split('/')[2]
        try:
            expr=nuke.nodes.Expression()
            expr.setName(name)
            expr.setInput(0,node)
            expr['expr0'].setValue(makeCryptoExpression(node,m))
            expr['channel0'].setValue('rgba')
        except:
            pass