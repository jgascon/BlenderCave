# -*- coding: iso-8859-1 -*-
## Copyright © LIMSI-CNRS (2013)
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
import blender_cave.base
import blender_cave.exceptions

""" @package screen
Manager of Virtual Environments through blenderCAVE ...
"""

class Screen(blender_cave.base.Base):

    def __init__(self, parent, configuration):
        super(Screen, self).__init__(parent)

        if 'viewport' in configuration:
            self._viewport = configuration['viewport']

        corners       = configuration['corners']
        self._buffers = {}
        for bufferName in configuration['buffers']:
            user = self.getBlenderCave().getUserByName(configuration['buffers'][bufferName]['user'])
            self._buffers[bufferName] = {'user' : user, 'eye': configuration['buffers'][bufferName]['eye']}

        stereo_mode = bgl.Buffer(bgl.GL_BYTE, 1)
        bgl.glGetBooleanv(bgl.GL_STEREO, stereo_mode)
        if ((not 'left' in self._buffers) or (not 'right' in self._buffers)) and (stereo_mode == 1):
            raise blender_cave.exceptions.VirtualEnvironment('Stereo window but buffer is missing !')
        if (not 'middle' in self._buffers) and (stereo_mode == 0):
            raise blender_cave.exceptions.VirtualEnvironment('Monoscopic window but "middle" buffer is missing !')

        # First, check corners validity !
        XVector = corners['topRightCorner'] - corners['topLeftCorner']
        if XVector.length < (corners['topRightCorner'][0] / 100000):
            raise blender_cave.exceptions.VirtualEnvironment("top right and left corners are same points !")
            return

        YVector = corners['topRightCorner'] - corners['bottomRightCorner']
        if YVector.length < (corners['topRightCorner'][0] / 100000):
            raise blender_cave.exceptions.VirtualEnvironment("top and bottom right corners are same points !")
            return

        ZVector = XVector.cross(YVector)
        if ZVector.length < (corners['topRightCorner'][0] / 100000):
            raise blender_cave.exceptions.VirtualEnvironment("Three corners are not perpendicular !")
            return
        corners['bottomLeftCorner'] = corners['topLeftCorner'] - YVector

        Center = (corners['bottomLeftCorner'] + corners['topRightCorner']) / 2.0

        XVector.normalize()
        YVector.normalize()
        ZVector.normalize()

        self._fromVehicleToLocalScreen = mathutils.Matrix()
        self._fromVehicleToLocalScreen[0][0] = XVector[0]
        self._fromVehicleToLocalScreen[1][0] = XVector[1]
        self._fromVehicleToLocalScreen[2][0] = XVector[2]

        self._fromVehicleToLocalScreen[0][1] = YVector[0]
        self._fromVehicleToLocalScreen[1][1] = YVector[1]
        self._fromVehicleToLocalScreen[2][1] = YVector[2]

        self._fromVehicleToLocalScreen[0][2] = ZVector[0]
        self._fromVehicleToLocalScreen[1][2] = ZVector[1]
        self._fromVehicleToLocalScreen[2][2] = ZVector[2]

        self._fromVehicleToLocalScreen.invert()

        self._fromVehicleToLocalScreen = self._fromVehicleToLocalScreen * mathutils.Matrix.Translation((-Center))

        self._cornersLocally = {}
        for key, value in corners.items():
            corners[key].resize_4d()
            self._cornersLocally[key] = self._fromVehicleToLocalScreen * corners[key]

        self._windowCoordinates = {}
        self._windowCoordinates['left'  ] = self._cornersLocally['topLeftCorner'][0]
        self._windowCoordinates['right' ] = self._cornersLocally['topRightCorner'][0]
        self._windowCoordinates['top'   ] = self._cornersLocally['topRightCorner'][1]
        self._windowCoordinates['bottom'] = self._cornersLocally['bottomRightCorner'][1]

# Update frame_type of the scene, otherwise, there will be black borders ...
        scene = bge.logic.getCurrentScene()
        scene.frame_type="scale"

        self._focus = configuration['focus']
        if self._focus:
            self.getLogger().info('Focus forced on this screen')

    def _updateMatrixForBuffer(self, bufferName, camera, projection_matrix_name, post_camera_matrix_name, depth):

        user = self._buffers[bufferName]['user']
        scale = self.getBlenderCave().getScale()

        # Then, we transfer from the Camera referenceFrame (ie. : vehicle one) to local screen reference frame
        localScreenInCameraReferenceFrame = self._fromVehicleToLocalScreen

        userPositionInCameraReferenceFrame = user.getPosition()
        userEyeSeparation = user.getEyeSeparation()
        eyePositionInUserReferenceFrame = mathutils.Vector((self._buffers[bufferName]['eye'] * userEyeSeparation / 2.0, 0.0, 0.0, 1.0))
        viewPointPositionInScreenReferenceFrame = localScreenInCameraReferenceFrame * userPositionInCameraReferenceFrame * eyePositionInUserReferenceFrame

        viewPointPositionInScreenReferenceFrame_3d = viewPointPositionInScreenReferenceFrame
        viewPointPositionInScreenReferenceFrame_3d.resize_3d()
        viewPointPositionInScreenReferenceFrame.resize_3d()

        # Then, we translate to the position of the eye of the user
        from_vehicule_to_eye_by_screen = mathutils.Matrix.Translation((-viewPointPositionInScreenReferenceFrame_3d)) * localScreenInCameraReferenceFrame

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

        projection_matrix = mathutils.Matrix()
        projection_matrix[0][0] = 2 * nearVal / (right - left)
        projection_matrix[0][2] = (right + left) / (right - left)

        projection_matrix[1][1] = 2 * nearVal / (top - bottom)
        projection_matrix[1][2] = (top + bottom) / (top - bottom)

        projection_matrix[2][2] = - (farVal + nearVal) / (farVal - nearVal)
        projection_matrix[2][3] = - 2 * farVal * nearVal / (farVal - nearVal)

        projection_matrix[3][2] = - 1.0
        projection_matrix[3][3] = 0.0

        setattr(camera, post_camera_matrix_name, user.getVehiclePosition())
        setattr(camera, projection_matrix_name, projection_matrix * from_vehicule_to_eye_by_screen * scaleToApplyToTheScene)

    def updateProjectionMatrices(self):

        # Force the window to keep the focus by setting mouse position in the middle of the window ...
        if self._focus:
            bge.render.setMousePosition(bge.render.getWindowWidth() // 2, bge.render.getWindowHeight() // 2)

        scene = bge.logic.getCurrentScene()
        camera = scene.active_camera

        if (hasattr(self, '_viewport')):
            camera.useViewport = True
            camera.setViewport(self._viewport[0], self._viewport[1], self._viewport[2], self._viewport[3])

        depth = (camera.near + camera.far) / 2.0

        if 'left' in self._buffers:
            self._updateMatrixForBuffer('left', camera, 'projection_matrix_left', 'stereo_position_matrix_left', depth)
        if 'right' in self._buffers:
            self._updateMatrixForBuffer('right', camera, 'projection_matrix_right', 'stereo_position_matrix_right', depth)
        if 'alone' in self._buffers:
            self._updateMatrixForBuffer('alone', camera, 'projection_matrix', 'stereo_position_matrix', depth)

    def run(self):
        try:
            self.updateProjectionMatrices()
        except:
            self.getBlenderCave().log_traceback(True)
        
