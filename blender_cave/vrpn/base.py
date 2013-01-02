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

import blender_cave.base
import blender_cave.exceptions

class Base(blender_cave.base.Base):
    def __init__(self, parent, configuration):
        super(Base, self).__init__(parent)
        self._vrpn = self.getParent()
        try:
            while not isinstance(self._vrpn, blender_cave.vrpn.VRPN):
                self._vrpn = self._vrpn.getParent()
        except AttributeError:
            pass

    def getVRPN(self):
        return self._vrpn

class Receiver(Base):
    def __init__(self, main, configuration):
        super(Receiver, self).__init__(main, configuration)
        self._name = configuration['name']
        self._host = configuration['host']

    def __str__(self):
        return self._name + "@" + self._host

    def run(self):
        self._connexion.mainloop()

class Sender(Base):
    def __init__(self, main, configuration):
        super(Sender, self).__init__(main, configuration)
        self._processor_method = configuration['processor_method']
        if not hasattr(self.getVRPN().getProcessor(), self._processor_method):
            raise blender_cave.exceptions.VRPN_Invalid_Device('VRPN processor does not have "' + self._processor_method + '" method')
        try:
            self._data = configuration['data']
        except KeyError:
            self._data = None
        self._users = []
        try:
            users = configuration['users']
        except KeyError:
            self._users = self.getBlenderCave().getAllUsers()
        else:
            try:
                self._users.append(self.getBlenderCave().getUserByName(users))
            except blender_cave.exceptions.User:
                raise blender_cave.exceptions.VRPN_Invalid_Device('VRPN user not found for processor "' + configuration['processor_method'] + '": ' + users)

    def process(self, info):
        info['users'] = self._users
        info['data'] = self._data
        getattr(self.getVRPN().getProcessor(), self._processor_method)(info)
