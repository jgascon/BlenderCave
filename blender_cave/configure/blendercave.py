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

import socket

from . import base

class BlenderCave(base.Base):

    def __init__(self, parent, attrs):
        super(BlenderCave, self).__init__(parent, attrs)
        if 'synchroPort' in attrs:
            self._synchroPort = int(attrs['synchroPort'])
        else:
            self._synchroPort = 2731
        if 'synchroAddress' in attrs:
            self._synchroAddress = attrs['synchroAddress']
        else:
            self._synchroAddress = '225.0.0.37'
        if 'focus_master' in attrs:
            focus_console = attrs['focus_master']
            if focus_console.lower() == 'true':
                self._focus_master = True
            else:
                self._focus_master = False
        else:
            self._focus_master = False

    def addScreenAndGetItsID(self, screen):
        try:
            screenNumber = len(self._screens)
        except AttributeError:
            screenNumber = 0
            self._screens = [screen]
        else:
            self._screens.append(screen)
        return screenNumber

    def startElement(self, name, attrs):
        child = None
        if name == 'computer':
            from . import computer
            child = computer.Computer(self, attrs)
        if not self.getParser().getOnlyScreens():
            if name == 'user':
                from . import user
                child = user.User(self, attrs)
            if name == 'vrpn':
                import blender_cave.vrpn.configure
                self._vrpn = blender_cave.vrpn.configure.VRPN(self, attrs)
                child = self._vrpn
            if name == 'osc':
                import blender_cave.osc.configure
                self._osc = blender_cave.osc.configure.OSC(self, attrs)
                child = self._osc
        return self.addChild(child)

    def display(self, indent):
        self.print_display(indent, 'Virtual environment : ' + self._name + ', ' + str(self._synchroPort) + ', ' + self._synchroAddress)
        super(BlenderCave, self).display(indent)

    def getConfiguration(self):
        localConfiguration = {}
        if self.getParser().getOnlyScreens():
            for computerName in self._children['computer']:
                localConfiguration[computerName] = self._children['computer'][computerName].getConfiguration()
            return localConfiguration
        localConfiguration['users'] = []
        try:
            for userName in self._children['user']:
                localConfiguration['users'].append(self._children['user'][userName].getLocalConfiguration())
        except KeyError:
            self.raise_error('No user available in the Virtual Environment', False)

        try:
            for computerName in self._children['computer']:
                if computerName == socket.gethostname():
                    this_computer = self._children['computer'][computerName]
                    break
                if computerName == '*':
                    this_computer =  self._children['computer'][computerName]
            screen = this_computer.getConfiguration()
            localConfiguration['screen'] = screen.getConfiguration()
            localConfiguration['screen']['focus_master'] = self._focus_master
        except (KeyError, UnboundLocalError):
            self.raise_error('This computer is not defined in the configuration file', False)

        for screenIndex in range(len(self._screens)):
            if self._screens[screenIndex]._is_master:
                master_node = self._screens[screenIndex]._parent._name

        if master_node == '*':
            master_node = 'localhost'

        localConfiguration['connection'] = {'port'           : self._synchroPort,
                                            'address'        : self._synchroAddress,
                                            'number_screens' : len(self._screens),
                                            'is_master'      : screen._is_master,
                                            'screen_id'      : screen._screen_id,
                                            'master_node'    : master_node}

        if hasattr(self, '_vrpn'):
            localConfiguration['vrpn'] = self._vrpn.getLocalConfiguration()
        else:
            localConfiguration['vrpn'] = {}

        if hasattr(self, '_osc'):
            localConfiguration['osc'] = self._osc.getLocalConfiguration()
        else:
            localConfiguration['osc'] = {}

        return localConfiguration
