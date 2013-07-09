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

import blender_cave.processor
import blender_cave
import bge

# This class allows to parameter the Processor according to the .xml file
# stored in "configuration"
class Configure(blender_cave.processor.Configure):
    def __init__(self, parent, attrs):
        super(Configure, self).__init__(parent, attrs)
        if 'I_am_a_flag' in attrs:
            self._flag = attrs['I_am_a_flag']
        else:
            self._flag = 'no flag'
            
    def getConfiguration(self):
        dic = {}
        dic['I_am_a_flag'] = self._flag
        return dic
        
class Processor(blender_cave.processor.Processor):
    def __init__(self, parent, configuration):
        super(Processor, self).__init__(parent, configuration)
        self._scene = bge.logic.getCurrentScene()
        try:
            self._flagRecup = configuration['I_am_a_flag']
        except KeyError:
            self._flagRecup = 'NOT_DEFINED'
	
    def flagInXmlFile(self):
        print(self._flagRecup, 'issued from xml file')
        
    def processorDisplayer(self,text):
        print('Here I put whatever I wish, like:',text)