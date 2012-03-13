## Copyright © LIMSI-CNRS (2011)
##
## contributor(s) : Jorge Gascon, Damien Touraine, David Poirier-Quinot,
## Laurent Pointal, Julian Adenauer, 
## 
## This software is a computer program whose purpose is to distribute
## blender to render on CAVE(TM) device systems.
## 
## This software is governed by the CeCILL  license under French law and
## abiding by the rules of distribution of free software.  You can  use, 
## modify and/ or redistribute the software under the terms of the CeCILL
## license as circulated by CEA, CNRS and INRIA at the following URL
## "http://www.cecill.info". 
## 
## As a counterpart to the access to the source code and  rights to copy,
## modify and redistribute granted by the license, users are provided only
## with a limited warranty  and the software's author,  the holder of the
## economic rights,  and the successive licensors  have only  limited
## liability. 
## 
## In this respect, the user's attention is drawn to the risks associated
## with loading,  using,  modifying and/or developing or reproducing the
## software by the user in light of its specific status of free software,
## that may mean  that it is complicated to manipulate,  and  that  also
## therefore means  that it is reserved for developers  and  experienced
## professionals having in-depth computer knowledge. Users are therefore
## encouraged to load and test the software's suitability as regards their
## requirements in conditions enabling the security of their systems and/or 
## data to be ensured and,  more generally, to use and operate it in the 
## same conditions as regards security. 
## 
## The fact that you are presently reading this means that you have had
## knowledge of the CeCILL license and that you accept its terms.
## 

import mathutils
import bgl
import bge
import blender_cave
from . import packer

""" @package VEC
Manager of Virtual Environments through blenderCAVE ...
"""

class VECException (BaseException):
    def __init__(self, reason):
        self._reason = reason
        return

    def __str__(self):
        return self._reason



class VEC:

    def __init__(self, node, screenID):
        self._screenID = screenID
        self._cornersInsideVehicle={}
        self._buffers={}

        if node.attributes["name"]:
            self._screenName = node.attributes["name"].value

        child = node.firstChild
        while child:
            if child.nodeName == 'graphic_buffer':
                self._getBuffer(child)
            elif child.nodeName == 'viewport':
                self._getViewport(child)
            elif child.nodeName == 'corner':
                self._getCorner(child)
            child = child.nextSibling

            if hasattr(self, '_checkStereoMode'):
                if 'left' in self._buffers and 'right' in self._buffers:
                    if self._buffers['left']['eye'] != self._buffers['right']['eye'] or self._buffers['left']['user'] != self._buffers['right']['user']:
                        stereo_mode = bgl.Buffer(bgl.GL_BYTE, 1)
                        bgl.glGetBooleanv(bgl.GL_STEREO, stereo_mode)
                        if stereo_mode[0] == 0:
                            raise VECException('cannot address a stereo window !')

        for corner in ['topRightCorner', 'topLeftCorner', 'bottomRightCorner']:
            if (corner in self._cornersInsideVehicle) == False:
                raise VECException("Need \""+corner+"\" inside configuration file !")
# Update frame_type of the scene, otherwise, there will be black borders ...
        scene = bge.logic.getCurrentScene()
        scene.frame_type="scale"

    def isMaster(self):
        return self._screenID == 0

    def _getBuffer(self, node):
        if 'name' in node.attributes:
            bufferName = node.attributes['name'].value
            if 'user' in node.attributes:
                eye = node.attributes['eye'].value
                if eye == "middle":
                    buffer = {'eye':  0.0}
                elif eye == "left":
                    buffer = {'eye': -1.0}
                elif eye == "right":
                    buffer = {'eye': +1.0}
                else:
                    return
                try:
                    userID = int(node.attributes['user'].value)
                except TypeError:
                    raise VECException("Invalid user ID : must be an integer !")
                    return
                buffer["user"] = userID
                if bufferName == "alone":
                    bufferName = "main"
                self._buffers[bufferName] = buffer

    def _getViewport(self, node):
        if node.firstChild and node.firstChild.nodeType == node.TEXT_NODE:
            child=node.firstChild
            child.normalize()
            coordinates = []
            for coordinate in child.data.split(','):
                coordinates.append(int(coordinate))
                if len(coordinates) == 4:
                    self._viewport = coordinates

    def _getCorner(self, node):
        if 'name' in node.attributes:
            cornerName = node.attributes['name'].value
            if node.firstChild and node.firstChild.nodeType == node.TEXT_NODE:
                child=node.firstChild
                child.normalize()
                coordinates = []
                for coordinate in child.data.split(','):
                    coordinates.append(float(coordinate))
                    if len(coordinates) == 3:
                        self._cornersInsideVehicle[cornerName] = mathutils.Vector((coordinates[0], coordinates[1], coordinates[2]))

    def finalizeConfiguration(self, users):
        if hasattr(self, '_cornersInsideVehicle') == False:
            raise VECException("current configuration does not have any valid corner")
        for corner in ['topRightCorner', 'topLeftCorner', 'bottomRightCorner']:
            if corner in self._cornersInsideVehicle == False:
                raise VECException("cannot find " + corner)

        for bufferName in ['left', 'main', 'right']:
            if bufferName in self._buffers:
                if (self._buffers[bufferName]['user'] in users) == False:
                    raise VECException("Invalid user ID : ", self._buffers[bufferName]['user'])

        self._users = users

        # First, check corners validity !
        XVector = self._cornersInsideVehicle['topRightCorner'] - self._cornersInsideVehicle['topLeftCorner']
        if XVector.length < (self._cornersInsideVehicle['topRightCorner'][0] / 100000):
            raise VECException("top right and left corners are same points !")
            return

        YVector = self._cornersInsideVehicle['topRightCorner'] - self._cornersInsideVehicle['bottomRightCorner']
        if YVector.length < (self._cornersInsideVehicle['topRightCorner'][0] / 100000):
            raise VECException("top and bottom right corners are same points !")
            return

        ZVector = XVector.cross(YVector)
        if ZVector.length < (self._cornersInsideVehicle['topRightCorner'][0] / 100000):
            raise VECException("Three corners are not perpendicular !")
            return
        self._cornersInsideVehicle['bottomLeftCorner'] = self._cornersInsideVehicle['topLeftCorner'] - YVector

        Center = (self._cornersInsideVehicle['bottomLeftCorner'] + self._cornersInsideVehicle['topRightCorner']) / 2.0

        XVector.normalize()
        YVector.normalize()
        ZVector.normalize()

        self._fromVehicleToLocalScreen = mathutils.Matrix()
        self._fromVehicleToLocalScreen[0][0] = XVector[0]
        self._fromVehicleToLocalScreen[0][1] = XVector[1]
        self._fromVehicleToLocalScreen[0][2] = XVector[2]

        self._fromVehicleToLocalScreen[1][0] = YVector[0]
        self._fromVehicleToLocalScreen[1][1] = YVector[1]
        self._fromVehicleToLocalScreen[1][2] = YVector[2]

        self._fromVehicleToLocalScreen[2][0] = ZVector[0]
        self._fromVehicleToLocalScreen[2][1] = ZVector[1]
        self._fromVehicleToLocalScreen[2][2] = ZVector[2]


        self._fromVehicleToLocalScreen.invert()


        Center.resize_4d()

        self._fromVehicleToLocalScreen = self._fromVehicleToLocalScreen * mathutils.Matrix.Translation((-Center))

        self._cornersLocally = {}
        for key, value in self._cornersInsideVehicle.items():
            self._cornersInsideVehicle[key].resize_4d()
            self._cornersLocally[key] = self._fromVehicleToLocalScreen * self._cornersInsideVehicle[key]

        self._windowCoordinates = {}
        self._windowCoordinates['left'  ] = self._cornersLocally['topLeftCorner'][0]
        self._windowCoordinates['right' ] = self._cornersLocally['topRightCorner'][0]
        self._windowCoordinates['top'   ] = self._cornersLocally['topRightCorner'][1]
        self._windowCoordinates['bottom'] = self._cornersLocally['bottomRightCorner'][1]

    def _updateMatrixForBuffer(self, bufferName, camera, projection_matrix_name, post_camera_matrix_name, depth):

        scale = blender_cave.getScale()

        # Then, we transfer from the Camera referenceFrame (ie. : vehicle one) to local screen reference frame
        localScreenInCameraReferenceFrame = self._fromVehicleToLocalScreen

        userPositionInCameraReferenceFrame = self._users[self._buffers[bufferName]['user']].getPosition()
        userEyeSeparation = self._users[self._buffers[bufferName]['user']].getEyeSeparation()
        eyePositionInUserReferenceFrame = mathutils.Vector((self._buffers[bufferName]['eye'] * userEyeSeparation / 2.0, 0.0, 0.0, 1.0))
        viewPointPositionInScreenReferenceFrame = localScreenInCameraReferenceFrame * userPositionInCameraReferenceFrame * mathutils.Vector((eyePositionInUserReferenceFrame))

        # Then, we translate to the position of the eye of the user
        modelview_matrix = mathutils.Matrix.Translation((-viewPointPositionInScreenReferenceFrame)) * localScreenInCameraReferenceFrame

        # For the moment, I don't know if the near and far informations from the camera are OK ...
        nearVal = camera.near * scale
        farVal = camera.far * scale

        horizontalShifting = viewPointPositionInScreenReferenceFrame[0]
        verticalShifting   = viewPointPositionInScreenReferenceFrame[1]
        depthShifting      = viewPointPositionInScreenReferenceFrame[2]

        if (depthShifting >= 0.0001) or (depthShifting <= -0.0001):
            depthPlaneRatio = nearVal / depthShifting
        else:
            depthPlaneRatio = nearVal

        left   = (self._windowCoordinates['left'  ] - horizontalShifting) * depthPlaneRatio
        right  = (self._windowCoordinates['right' ] - horizontalShifting) * depthPlaneRatio
        bottom = (self._windowCoordinates['bottom'] -   verticalShifting) * depthPlaneRatio
        top    = (self._windowCoordinates['top'   ] -   verticalShifting) * depthPlaneRatio

        # And scale to the scene ...
        scaleToApplyToTheScene = mathutils.Matrix.Translation((0.0, 0.0, -depth))
        scaleToApplyToTheScene *= mathutils.Matrix.Scale(scale, 4)
        scaleToApplyToTheScene *= mathutils.Matrix.Translation((0.0, 0.0, depth))

        modelview_matrix = modelview_matrix * scaleToApplyToTheScene 

        setattr(camera, post_camera_matrix_name, modelview_matrix)

        projection_matrix = mathutils.Matrix()
        projection_matrix[0][0] = 2 * nearVal / (right - left)
        projection_matrix[2][0] = (right + left) / (right - left)
        projection_matrix[1][1] = 2 * nearVal / (top - bottom)
        projection_matrix[2][1] = (top + bottom) / (top - bottom)
        projection_matrix[2][2] = - (farVal + nearVal) / (farVal - nearVal)
        projection_matrix[3][2] = - 2 * farVal * nearVal / (farVal - nearVal)
        projection_matrix[2][3] = - 1.0
        projection_matrix[3][3] = 0.0

        setattr(camera, projection_matrix_name, projection_matrix)

    def updateProjectionMatrices(self):
        scene = bge.logic.getCurrentScene()
        camera = scene.active_camera

        if (hasattr(self, '_viewport')):
            camera.useViewport = True
            camera.setViewport(self._viewport[0], self._viewport[1], self._viewport[2], self._viewport[3])

        depth = camera.lens

        if 'left' in self._buffers:
            self._updateMatrixForBuffer('left', camera, 'projection_matrix_left', 'stereo_position_matrix_left', depth)
        if 'right' in self._buffers:
            self._updateMatrixForBuffer('right', camera, 'projection_matrix_right', 'stereo_position_matrix_right', depth)
        if 'main' in self._buffers:
            self._updateMatrixForBuffer('main', camera, 'projection_matrix', 'stereo_position_matrix', depth)

    def getUserIDByName(self, userName):
        for id, user in self._users.items():
            if userName == user.getName():
                return id
        return False

    def getUserPosition(self, userID):
        if userID in self._users:
            return self._users[userID].getPosition()

    def setUserPosition(self, userID, position):
        if userID in self._users:
            self._users[userID].setPosition(position)
