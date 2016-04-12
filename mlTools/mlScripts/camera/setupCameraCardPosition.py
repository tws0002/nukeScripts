import nuke,math


def main():
    cam=nuke.selectedNode()
    if cam.Class()=="Camera2":
        dist=nuke.getInput("card distance from camera?")
        tr=nuke.nodes.TransformGeo()
        tr.setInput(1,cam)
        tr['translate'].setValue(dist,2)
        tr['translate'].setValue(dist,2)
        tr['uniform_scale'].setValue((cam['haperture'].value()/cam['focal'].value())*tr['translate'].value()[2])
        
        mCam = nuke.math.Matrix4()
        mTransformGeo = nuke.math.Matrix4()
        mResult = nuke.math.Matrix4()

        for i in range(0,16):
            mCam[i] = cam['matrix'].valueAt(nuke.frame())[i]
            mTransformGeo[i] = tr['matrix'].valueAt(nuke.frame())[i]

        mResult = mTransformGeo *  mCam

        #AxisResult = nuke.createNode("Axis")
        #AxisResult.setName("Axis_result")
        #AxisResult['useMatrix'].setValue(True)
        #for i in range(0,16):
        #    AxisResult['matrix'].setValueAt(mResult[i], nuke.frame(), i)

        mResult.transpose()

        mTranslate = nuke.math.Matrix4(mResult)
        mTranslate.translationOnly()
        mRotate = nuke.math.Matrix4(mResult)
        mRotate.rotationOnly()
        mScale = nuke.math.Matrix4(mResult)
        mScale.scaleOnly()

        translate = (mTranslate[12], mTranslate[13], mTranslate[14])
        rotateRad = mRotate.rotationsZXY()
        rotate = (math.degrees(rotateRad[0]), math.degrees(rotateRad[1]), math.degrees(rotateRad[2]))
        scale = (mScale.xAxis().x, mScale.yAxis().y, mScale.zAxis().z)

        print translate, rotate, scale
    else:
        nuke.message("must select a camera")