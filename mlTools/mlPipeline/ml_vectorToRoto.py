import nuke

def trackFrameForward():
    node=nuke.thisNode()
    rootLayer=node.knob("curves").rootLayer
    curve=node.knob("curves").getSelected()[0]
    size=nuke.thisNode()['size'].value()
    frm=int(nuke.root()['frame'].value())
    for c,point in enumerate(curve):
        pos= posCenter= point.center.getPosition(frm)
        dxCenter=nuke.sample(node,"red",posCenter.x,posCenter.y,size,size)
        dyCenter=nuke.sample(node,"green",posCenter.x,posCenter.y,size,size)
        posCenter.x+=dxCenter
        posCenter.y+=dyCenter
        print dxCenter,dyCenter
        point.center.addPositionKey(frm+1,posCenter)
    nuke.root()['frame'].setValue(frm+1)
    
def trackFrameBackward():
    node=nuke.thisNode()
    rootLayer=node.knob("curves").rootLayer
    curve=node.knob("curves").getSelected()[0]
    size=nuke.thisNode()['size'].value()
    frm=int(nuke.root()['frame'].value())
    for c,point in enumerate(curve):
        pos= posCenter= point.center.getPosition(frm)
        dxCenter=nuke.sample(node,"blue",posCenter.x,posCenter.y,size,size)
        dyCenter=nuke.sample(node,"alpha",posCenter.x,posCenter.y,size,size)
        posCenter.x+=dxCenter
        posCenter.y+=dyCenter
        print dxCenter,dyCenter
        #posR= point.rightTangent.getPosition(frm)
        #dxR=nuke.sample(node,"blue",pos.x-posR.x,pos.y-posR.y,size,size)
        #dyR=nuke.sample(node,"alpha",pos.x-posR.x,pos.y-posR.y,size,size)
        #posR.x+=dxR
        #posR.y+=dyR
        point.center.addPositionKey(frm-1,posCenter)
        #point.rightTangent.addPositionKey(frm-1,posR)
        #point.leftTangent.addPositionKey(frm-1,-posR)
    nuke.root()['frame'].setValue(frm-1)
    

def trackChunkForward():
    node=nuke.thisNode()
    chunk=nuke.thisNode()['chunk'].value()
    size=nuke.thisNode()['size'].value()
    rootLayer=node.knob("curves").rootLayer
    curve=node.knob("curves").getSelected()[0]
    start=int(nuke.root()['frame'].value())
    end=int(start+chunk)+1
    task = nuke.ProgressTask( 'Baking camera from meta data in %s' % node.name() )
    pvals=[0]*len(curve)
    for i in range(start,end):
        if task.isCancelled():
            nuke.executeInMainThread("")
            break;
        task.setMessage( 'processing frame %s' % i )
        task.setProgress(int((float(i-start)/float(end))*100))
        temp = nuke.nodes.CurveTool()
        nuke.execute(temp, i, i)
        nuke.root()['frame'].setValue(i)
        print pvals
        for c,point in enumerate(curve):
            point.center.evaluate(i)
            if i==start:
                pos= point.center.getPosition(i)
            else:
                pos=pvals[c]
            posNextFrm=point.center.getPosition(i+1)
            dx=nuke.sample(node,"red",pos.x,pos.y,size,size)
            dy=nuke.sample(node,"green",pos.x,pos.y,size,size)
            if posNextFrm!=pos:
                pos.x=(pos.x+dx+posNextFrm.x)/2
                pos.y=(pos.y+dy+posNextFrm.y)/2
            else:
                pos.x=pos.x+dx
                pos.y=pos.y+dy
            if i==end-1:
                point.center.addPositionKey(i,pos)
            else:
                pvals[c]=pos
        node['curves'].changed()
        nuke.delete(temp)
    
def trackRangeForward():
    node=nuke.thisNode()
    size=nuke.thisNode()['size'].value()
    rootLayer=node.knob("curves").rootLayer
    curve=node.knob("curves").getSelected()[0]
    start=int(nuke.root()['frame'].value())
    end=int(nuke.root()['last_frame'].value())
    task = nuke.ProgressTask( 'Baking camera from meta data in %s' % node.name() )
    for i in range(start,end):
        if task.isCancelled():
            nuke.executeInMainThread("")
            break;
        task.setMessage( 'processing frame %s' % i )
        task.setProgress(int((float(i-start)/float(end))*100))
        temp = nuke.nodes.CurveTool()
        nuke.execute(temp, i, i)
        
        nuke.root()['frame'].setValue(i)
        for c,point in enumerate(curve):
            point.center.evaluate(i)
            pos= point.center.getPosition(i)
            print pos
            dx=nuke.sample(node,"red",pos.x,pos.y,size,size)
            dy=nuke.sample(node,"green",pos.x,pos.y,size,size)
            print c,dx,dy
            pos.x=pos.x+dx
            pos.y=pos.y+dy
            point.center.addPositionKey(i,pos)
            node['curves'].changed()
        nuke.delete(temp)

def eraseAllVals():
    node=nuke.thisNode()
    rootLayer=node.knob("curves").rootLayer
    curve=node.knob("curves").getSelected()[0]

    for point in curve:
        point.center.removeAllKeys()
   
def eraseAllFeatherVals():
    node=nuke.thisNode()
    rootLayer=node.knob("curves").rootLayer
    curve=node.knob("curves").getSelected()[0]

    for point in curve:
        point.featherCenter.removeAllKeys() 
   
   
def createReferenceMasks():
    rotoNode = nuke.thisNode() 
    rotoCurve = rotoNode['curves'] 
    rotoRoot = rotoCurve.rootLayer 
    stereoNode = nuke.createNode('Roto') 
    stereoCurve = stereoNode['curves'] 
    stereoRoot = stereoCurve.rootLayer 
    for shape in rotoRoot: 
        print 'root' 
        if isinstance(shape, nuke.rotopaint.Shape): 
            print 'shape' 
            count = 0 
            newshape = nuke.rotopaint.Shape(stereoCurve) 
            newshape.name = shape.name 
            for points in shape: 
                print 'point%s' % count 
                newpoint = nuke.rotopaint.ShapeControlPoint() 
                
                newcurve_center = nuke.rotopaint.AnimCurve() 
                newcurve_center.expressionString = "%s.curves.%s.curve.%s.main.x + %s.curves.%s.feather.%s.main.x" % (rotoNode.name(), shape.name, count, rotoNode.name(), shape.name, count)
                newcurve_center.useExpression = True 
                
                newcurve_leftTangent = nuke.rotopaint.AnimCurve() 
                newcurve_leftTangent.expressionString = "%s.curves.%s.feather.%s.left.x" % (rotoNode.name(), shape.name, count)
                newcurve_leftTangent.useExpression = True 

                newcurve_rightTangent = nuke.rotopaint.AnimCurve() 
                newcurve_rightTangent.expressionString = "%s.curves.%s.feather.%s.right.x" % (rotoNode.name(), shape.name, count)
                newcurve_rightTangent.useExpression = True 
                
                newpoint.center.setPositionAnimCurve(0, newcurve_center) 
                newpoint.leftTangent.setPositionAnimCurve(0, newcurve_leftTangent) 
                newpoint.rightTangent.setPositionAnimCurve(0, newcurve_rightTangent) 
                
                newcurve_center = nuke.rotopaint.AnimCurve() 
                newcurve_center.expressionString = "%s.curves.%s.curve.%s.main.y + %s.curves.%s.feather.%s.main.y" % (rotoNode.name(), shape.name, count, rotoNode.name(), shape.name, count)
                newcurve_center.useExpression = True 
                
                newcurve_leftTangent = nuke.rotopaint.AnimCurve() 
                newcurve_leftTangent.expressionString = "%s.curves.%s.feather.%s.left.y" % (rotoNode.name(), shape.name, count)
                newcurve_leftTangent.useExpression = True 

                newcurve_rightTangent = nuke.rotopaint.AnimCurve() 
                newcurve_rightTangent.expressionString = "%s.curves.%s.feather.%s.right.y" % (rotoNode.name(), shape.name, count)
                newcurve_rightTangent.useExpression = True 
                
                newpoint.center.setPositionAnimCurve(1, newcurve_center) 
                newpoint.leftTangent.setPositionAnimCurve(1, newcurve_leftTangent) 
                newpoint.rightTangent.setPositionAnimCurve(1, newcurve_rightTangent) 

                print newpoint.center.getPositionAnimCurve(0).expressionString 
                newshape.append(newpoint) 
                count += 1 
    stereoRoot.append(newshape) 
    stereoCurve.changed() 
 
props= ['center', 'featherCenter', 'featherLeftTangent', 'featherRightTangent', 'leftTangent', 'rightTangent']