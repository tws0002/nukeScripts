import nuke

def main():

    n=nuke.selectedNode()
    coords=nuke.getInput('set x and y position:', '0,0')
    x,y=coords.split(',')
    found=[]
    for ch in n.channels():
        if ch.startswith('_m_') and not 'alpha' in ch and not 'all' in ch:
            result= ch,nuke.sample(n,ch,int(x),int(y))
            if result[1]==1:
                found.append(result[0])
    nuke.message(found)

