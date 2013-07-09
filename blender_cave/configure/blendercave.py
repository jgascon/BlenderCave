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
            screenNumber      = 0
            self._screens     = [screen]
            self._master_node = screen._parent._name
            screen._focus     = self._focus_master
        else:
            self._screens.append(screen)
            screen._focus     = False
        return screenNumber

    def startElement(self, name, attrs):
        child = None
        if name == 'computer':
            from . import computer
            child = computer.Computer(self, attrs)
        if name == 'user':
            from . import user
            child = user.User(self, attrs)
        if name == 'processor':
            from . import processor
            self._processor = processor.Processor(self, attrs)
            child = self._processor
        return self.addChild(child)

    def display(self, indent):
        self.print_display(indent, 'Virtual environment : ' + self._name + ', ' + str(self._synchroPort) + ', ' + self._synchroAddress)
        super(BlenderCave, self).display(indent)

    def getConfiguration(self):

        if (self._master_node == '*') and (len(self._children['computer']) > 1):
            self.raise_error('Cannot determine master node as it is wildcard', False)

        computers = {}
        for computerName, computer in self._children['computer'].items():
            computers[computerName] = computer.getConfiguration()

        this_computer_name = socket.gethostname()
        if ('*' in computers) and (this_computer_name not in computers):
            computers[this_computer_name] = computers['*']
            del(computers['*'])

        if self._master_node == '*':
            # Here, we are sure that there is only one computer !
            self._master_node = 'localhost'

        try:
            users = []
            for userName, user in self._children['user'].items():
                users.append(user.getConfiguration())
        except KeyError:
            self.raise_error('No user available in the Virtual Environment', False)

        try:
            configuration = self._processor.getConfiguration()
        except AttributeError:
            configuration = {}

        configuration['users']      = users
        configuration['computers']  = computers
        configuration['connection'] = {'port'           : self._synchroPort,
                                       'address'        : self._synchroAddress,
                                       'number_screens' : len(self._screens),
                                       'master_node'    : self._master_node}

        return configuration
