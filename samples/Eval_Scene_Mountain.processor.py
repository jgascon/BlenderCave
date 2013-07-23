import blender_cave.processor
import blender_cave.vrpn.head_controlled_navigation as hc_nav
import blender_cave
import bge
import mathutils
import math
import sys
import copy
import os
import time
from math import radians

class Configure(blender_cave.processor.Configure):
    def __init__(self, parent, attrs):
        super(Configure, self).__init__(parent, attrs, 'Mountain')

class Processor(blender_cave.processor.Processor):
    def __init__(self, parent, configuration):
        super(Processor, self).__init__(parent, configuration)
        if 'EXPE_JOYSTICK' in os.environ:
            self._use_HCNav    = False
        else:
            self._use_HCNav    = True
        self._scene            = bge.logic.getCurrentScene()
        self._controller       = bge.logic.getCurrentController()
        self._moveBox          = self._scene.objects['MoveBox']
        self._home_position    = copy.copy(self._moveBox.worldPosition)
        self._home_orientation = copy.copy(self._moveBox.worldOrientation)

        self._mat_trans = mathutils.Matrix.Rotation(radians(90.0), 4, 'X')
        self._mat_trans_inv = self._mat_trans.inverted()

        if self._use_HCNav:
            self._navigator = hc_nav.HCNav(parent, self.process_HCNav)
            self._navigator.setPositionFactors(1, 20.0, 1.0)
            #self._navigator.setHeadNeckLocation(mathutils.Matrix())


        if self.getBlenderCave().isMaster():
            self.getBlenderCave().getSceneSynchronizer().getItem(self._moveBox).activate(True, False)
            try:
                post_fix        = ('NAV' if self._use_HCNav else 'JOY') + '_' + os.environ['EXPE_LOG_USER'] + '.log'
                self._log_traj  = open(os.environ['EXPE_LOG_DIRECTORY'] + 'traj_' + post_fix, 'w+')
                self._log_touch = open(os.environ['EXPE_LOG_DIRECTORY'] + 'touch_' + post_fix, 'w+')
            except:
                self.getBlenderCave().log_traceback(True)

                    
        self._move_position = False

    def user_position(self, info):
        super(Processor, self).user_position(info)
        if self._use_HCNav:
            for user in info['users']:
                self._navigator.setHeadLocation(user, info)

    def process_HCNav(self, matrix, info):
        new_matrix = self._moveBox.worldOrientation.to_4x4() * self._mat_trans * matrix.inverted() * self._mat_trans_inv * self._moveBox.worldOrientation.to_4x4().inverted()
        self._moveBox.worldPosition = new_matrix.to_translation() + self._moveBox.worldPosition
        self._moveBox.worldOrientation = new_matrix.to_3x3() * self._moveBox.worldOrientation

    def reset(self, users = None):
        self._moveBox.worldPosition    = self._home_position
        self._moveBox.worldOrientation = self._home_orientation
        if not users is None:
            for user in users:
                if self._use_HCNav:
                    self._navigator.update(self._navigator.RESET, user)
                user.resetVehiclePosition()

    def rum_a(self, info):
        if self._use_HCNav:
            return
        if info['channel'][1] < 0.2:
            self._controller.activate(self._controller.actuators['RotX_DOWN'])
            self._controller.deactivate(self._controller.actuators['RotX_UP'])
        elif info['channel'][1] > 0.8:
            self._controller.activate(self._controller.actuators['RotX_UP'])
            self._controller.deactivate(self._controller.actuators['RotX_DOWN'])
        else:
            self._controller.deactivate(self._controller.actuators['RotX_UP'])  
            self._controller.deactivate(self._controller.actuators['RotX_DOWN'])
         
        if info['channel'][0] < 0.2:
            self._controller.activate(self._controller.actuators['RotZ_UP'])
            self._controller.deactivate(self._controller.actuators['RotZ_DOWN'])
         
        elif info['channel'][0] > 0.8:
            self._controller.activate(self._controller.actuators['RotZ_DOWN'])
            self._controller.deactivate(self._controller.actuators['RotZ_UP'])
        else:
            self._controller.deactivate(self._controller.actuators['RotZ_UP'])
            self._controller.deactivate(self._controller.actuators['RotZ_DOWN'])

        if info['channel'][5] < 0.2:
            self._controller.activate(self._controller.actuators['LocX_UP'])
            self._controller.deactivate(self._controller.actuators['LocX_DOWN'])
         
        elif info['channel'][5] > 0.8:
            self._controller.activate(self._controller.actuators['LocX_DOWN'])
            self._controller.deactivate(self._controller.actuators['LocX_UP'])
        else:
            self._controller.deactivate(self._controller.actuators['LocX_UP'])
            self._controller.deactivate(self._controller.actuators['LocX_DOWN'])

        if info['channel'][6] < 0.2:
            self._controller.activate(self._controller.actuators['LocZ_UP'])
            self._controller.deactivate(self._controller.actuators['LocZ_DOWN'])
         
        elif info['channel'][6] > 0.8:
            self._controller.activate(self._controller.actuators['LocZ_DOWN'])
            self._controller.deactivate(self._controller.actuators['LocZ_UP'])
        else:
            self._controller.deactivate(self._controller.actuators['LocZ_UP'])
            self._controller.deactivate(self._controller.actuators['LocZ_DOWN'])


    def rum_b(self, info):
        #print(info['button'])
        #return
        if self._use_HCNav:
            return
        if info['button'] == 22:
            if info['state'] == 1:
                self._controller.activate(self._controller.actuators['RotY_DOWN'])
            else:
                self._controller.deactivate(self._controller.actuators['RotY_DOWN'])
        
        if info['button'] == 25:
            if info['state'] == 1:
                self._controller.activate(self._controller.actuators['RotY_UP'])
            else:
                self._controller.deactivate(self._controller.actuators['RotY_UP'])

        if info['button'] == 26:
            if info['state'] == 1:
                self._controller.activate(self._controller.actuators['LocY_UP'])
            else:
                self._controller.deactivate(self._controller.actuators['LocY_UP'])
        
        if info['button'] == 23:
            if info['state'] == 1:
                self._controller.activate(self._controller.actuators['LocY_DOWN'])
            else:
                self._controller.deactivate(self._controller.actuators['LocY_DOWN'])


    def buttons(self, info):
        if not self._use_HCNav:
            return
        if (info['button'] == 0) and (info['state'] == 1):
            self._navigator.update(self._navigator.CALIBRATE)
        if (info['button'] == 1) and (info['state'] == 1):
            self._navigator.update(self._navigator.TOGGLE)
        if (info['button'] == 2) and (info['state'] == 1):
            self.reset(info['users'])

    def texts(self, info):
        if not self._use_HCNav:
            return
        cmd = None
        if info['message'] == 'COMPUTER CALIBRATION':
            print('Calibration')
            cmd = self._navigator.CALIBRATE
        elif info['message'] == 'COMPUTER NAVIGATION':
            print('Navigation')
            cmd = self._navigator.TOGGLE
        elif info['message'] == 'COMPUTER HOME':
            self.reset(info['users'])
        elif info['message'] == 'COMPUTER QUIT':
            self.getBlenderCave().quit("because user asked !")

        if cmd is not None:
            for user in info['users']:
                self._navigator.update(cmd, user)

    def console(self, info):
        try:
            cmd = None
            if info['key'] == 113:
                self.getBlenderCave().quit("'q' pressed")
            if info['key'] == 104:
                self.reset(info['users'])
            if info['key'] == 99:
                cmd = self._navigator.CALIBRATE
            if info['key'] == 110:
                cmd = self._navigator.TOGGLE
            if cmd is not None:
                for user in info['users']:
                    self._navigator.update(cmd, user)
        except KeyError:
            pass


    def run(self):
        if self.getBlenderCave().isMaster():
            position = self._moveBox.worldPosition
            position = str(position[0]) + ',' + str(position[1]) + ',' + str(position[2])
            orientation = self._moveBox.worldOrientation.to_quaternion()
            orientation = str(orientation[1]) + ',' + str(orientation[2]) + ',' + str(orientation[3]) + ',' + str(orientation[0])
            self._log_traj.write(position + '\n' + orientation +'\n' + str(time.time()) + '\n' + str(time.asctime()) +'\n\n')
            self._log_traj.flush()
