from __future__ import with_statement
import nuke,math
import os,re,sys
import nukescripts




def placeCard():
    dist=nuke.thisNode()['distance'].value()
    cam=nuke.thisNode()['camName'].value()
    cam=nuke.toNode(cam)
    if cam:
        print cam,dist
        
        cardScale=(cam['haperture'].value()/cam['focal'].value())*dist

        mCam = nuke.math.Matrix4()
        mTransformGeo = nuke.math.Matrix4()
        mResult = nuke.math.Matrix4()
        
        transformMatrixVals=[cardScale, 0, 0, 0, 0, cardScale, 0, 0, 0, 0, cardScale, -dist, 0, 0,0, 1]
            
        for i in range(0,16):
            mCam[i] = cam['matrix'].valueAt(nuke.frame())[i]
            mTransformGeo[i] = transformMatrixVals[i]

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
        
        nuke.thisNode()['translate'].setValue(translate)
        nuke.thisNode()['rotate'].setValue(cam['rotate'].value())
        nuke.thisNode()['scaling'].setValue(scale)
        
        
        print translate, rotate, scale

    else:
        nuke.message("must enter a valid camera")
