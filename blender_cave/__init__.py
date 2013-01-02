# -*- coding: iso-8859-1 -*-
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

"""@package blender_cave
Main BlenderCave module.

It has to be loaded by a python controller inside Blender File. Moreover, you should run blender_cave.run() each frame (ie.: triggered by an Always Actuator). Thus, you should get the interactions
"""
import sys
import os
import traceback
import blender_cave.exceptions

class Main:
    def __init__(self):
        """ Contstructor : load all necessary elements """
        self._initiated = False

        # Before creating the logging system, there is none ...
        try:
            # First, we load the environment: environment variables and command line arguments
            from . import environment
            environ = environment.Environment(self)
            # Once loaded, we can create the main logger
            self._logger = environ.getEnvironment('logger')
        except:
            traceback.print_exc()
            return

        try:
            self._logger.debug('current blender file : ' + bge.logic.getCurrentBlendName())

            # Complete the environment checking with the logger correctly defined
            environ.processRemainingConfiguration()

            # Load the configuration file
            from . import configure
            global_configuration = configure.Configure(self, environ)

            blend_file = environ.getEnvironment('blend_file')

            configuration = global_configuration.getConfiguration()
            del(global_configuration)

            # Configure the reload backupper: a module to be able to reload the context in case of reload of the scene. Not efficient for the moment
            from . import reload_backupper
            self._reload_backupper = reload_backupper.ReloadBackupper(self, environ)
            del(environ)

            # Suspend the scene before getting the network because in standalone screen, resume can occure inside the constructor ...
            bge.logic.getCurrentScene().suspend()

            # Configure the network connexions: deals with network
            from . import network
            self._network = network.Network(self, configuration['connection'])

            # Configure the synchronizer: check differences between frames to exchange between the master and the slaves
            from . import synchronizer
            self._synchronizer = synchronizer.Synchronizer(self)

            # Configure the users
            from . import user
            self._users = []
            for userIndex in range(len(configuration['users'])):
                self._users.append(user.User(self, userIndex, configuration['users'][userIndex]))

            # Configure the screen: the elements that configure the projection for each window
            from . import screen
            self._screen = screen.Screen(self, configuration['screen'])

            # Configure VRPN: module to get the interactions
            from . import vrpn
            self._vrpn = vrpn.VRPN(self, configuration['vrpn'])

            # Configure OSC: module to send the position of the objects and the users to the spatialized sound rendering system
            from . import osc
            self._osc = osc.OSC(self, configuration['osc'])

            # Configure splash screen: the electocardiogram that is displayed when waiting for every connexions
            from . import splash
            self._splash = splash.Splash(self)

            if blend_file is not None:
                self.loadScene(blend_file)
            else:
                self._splash.setMessage("Waiting for all slaves !")
                self._splash.start()

            if self.isMaster():
                self._vrpn.start()
                self._osc.start()

            self._initiated = True

            # Importante: register the main processing function to be executed by Blender just before each frame rendering
            bge.logic.getCurrentScene().pre_render.append(self._network.run)
            bge.logic.getCurrentScene().pre_render.append(self._screen.run)

        except blender_cave.exceptions.Common as error:
            self._logger.error(error)
        except IOError as error:
            self._logger.error(error)
        except:
            self.log_traceback(True)

    def getUserByName(self, userName):
        """Given a user name, get its object, or raise an exception if the user does not exists"""
        for userIndex in range(len(self._users)):
            if self._users[userIndex].getName() == userName:
                return self._users[userIndex]
        raise blender_cave.exceptions.User('User "' + userName + '" not found')

    def getAllUsers(self):
        """Get the array of all the users"""
        return self._users

    def addObjectToSynchronize(self, object, name):
        """Add an object to the synchronizer"""
        self._network.addObjectToSynchronize(object, name)

    def quit(self, reason):
        """Main quit method

        This method must be call instead of any other method to properly quit BlenderCave.
        Otherwise, you may have problem of not closed socket next time you run BlenderCave
        The reason is printed inside the log file of displayed on the console"""
        self._network.quit(reason)

    def isMaster(self):
        """Are we the master rendering node ?

        Many treatment must be done only on the master rendering node.
        Some others must be done only on one node.
        In such case, you can check with this method"""
        return self._network.isMaster()

    def getScale(self):
        """Get the scale between the virtual World and the Vehicule

        This method always return 1 for the moment: we have to improve the scale management !"""
        return 1

    def getReloadBackupper(self):
        """Get the reload backupper: not usefull for the moment"""
        return self._reload_backupper

    def loadScene(self, blender_file):
        """Load a scene: not usefull for the moment"""
        self._load_scene = blender_file
        self._splash.setMessage("Loading the Scene")
        self._splash.start()

    def isNetworkReady(self):
        """Can we use the network ?

        The network is only ready when all the rendering nodes have join the simulation"""
        return self._network.isReady()

    def run(self):
        """Activate the interactions

        The interaction (VRPN and OSC) are activated by this method. So you should call it once per frame from blender file"""
        if (self._initiated) and (self.isMaster()) and (self.isNetworkReady()):
            try:
                self._vrpn.run()
                if self.isMaster(): 
                    self._osc.run()
            except:
                self.log_traceback(True)
        if hasattr(self, '_load_scene'):
            if self.isNetworkReady():
                if self._splash.sceneIsSplash():
                    actuator = bge.logic.getCurrentController().owner.actuators['Game']
                    actuator.fileName = self._load_scene
                    bge.logic.getCurrentController().activate(actuator)
                    self.getLogger().warning('Loading a new scene : ' + self._load_scene)
                del(self._load_scene)
                try:
                    del(self._not_ready_to_load)
                except AttributeError:
                    pass
            else:
                if not hasattr(self, '_not_ready_to_load'):
                    self._not_ready_to_load = True
                    self._splash.setMessage("Defering loading the scene")

                    self.getLogger().info('Defering loading ' + self._load_scene + ' until everybody is connected !')

    def getLogger(self):
        """Usefull method to get the logger

        Usefull if you wish to log anything on the main logging system (ie.: logging file or console)"""
        return self._logger

    def getOSC(self):
        """Get OSC main sender"""
        return self._osc

    def log_traceback(self, error):
        """Log the traceback

        When an axception raised, that can log all the traceback inside the main logging system.
        Parameters:
          error - (boolean) if True, then definitely stop BlenderCave
        """
        if error:
            self._logger.error(traceback.format_exc())
            self._logger.error('cannot continue to run Blender Cave !')
            self._stopAll()
        else:
            self._logger.debug(traceback.format_exc())

    def _quitByNetwork(self, reason):
        """Internal quit: do not use"""
        self._logger.info('Quit: ' + reason)
        del(self._reload_backupper)
        self._stopAll()
        bge.logic.endGame()
        sys.exit()
        import time
        while True:
            time.sleep(1)

    def _stopAll(self):
        """Internal stop: do not use"""
        self._initiated = False
        bge.logic.getCurrentScene().pre_render.remove(self._network.run)
        bge.logic.getCurrentScene().pre_render.remove(self._screen.run)

    def _startSimulation(self):
        """Internal start of the simulation: do not use"""
        bge.logic.getCurrentScene().resume()
        self._splash.stop()
        self.getLogger().info("Start the simulation !")


# If we cannot import BGE, then we must not construct Blender CAVE !
try:
    import bge
except ImportError:
    pass
else:
    sys.modules[__name__] = Main()
