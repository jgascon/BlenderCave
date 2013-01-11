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

import bge
import copy
import datetime
import blender_cave.device

class Console(blender_cave.device.Sender):
    def __init__(self, parent):
        configuration = {'processor_method': 'console'}
        super(Console, self).__init__(parent, configuration)
        # Backup the data
        self._keyboard = copy.copy(bge.logic.keyboard.events)
        self._mouse_events = copy.copy(bge.logic.mouse.events)
        self._mouse_position = copy.copy(bge.logic.mouse.position)

    def start(self):
        return

    def run(self):
        now = datetime.datetime.now()

        # Processing keyboard !
        keyboard = bge.logic.keyboard.events
        if self._keyboard != keyboard:
            for key in keyboard.keys():
                if keyboard[key] != self._keyboard[key]:
                    info = {'key': key, 'state': keyboard[key], 'time': now}
                    self.process(info)

        # Processing mouse !
        mouse_events = bge.logic.mouse.events
        mouse_position = bge.logic.mouse.position
        if (self._mouse_position != mouse_position) or (self._mouse_events != mouse_events):
            info = {
                'position'    : mouse_position,
                'left'        : mouse_events[189],
                'middle'      : mouse_events[190],
                'right'       : mouse_events[191],
                'Scroll up'   : mouse_events[193],
                'Scroll down' : mouse_events[194],
                'time'        : now
                }
            self.process(info)
        self._keyboard = copy.copy(bge.logic.keyboard.events)
        self._mouse_events = copy.copy(bge.logic.mouse.events)
        self._mouse_position = copy.copy(bge.logic.mouse.position)
