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

from . import base

class Processor(base.Base):

    def __init__(self, parent, attrs):
        super(Processor, self).__init__(parent, attrs, 'processor')
        try:
            self._processorName = self.getBlenderCave().getProcessorModule()._name
        except AttributeError:
            self._processorName = ''

    def startElement(self, name, attrs):
        child = None
        if name == 'vrpn':
            import blender_cave.vrpn.configure
            self._vrpn = blender_cave.vrpn.configure.VRPN(self, attrs)
            child = self._vrpn
        if name == 'osc':
            import blender_cave.osc.configure
            self._osc = blender_cave.osc.configure.OSC(self, attrs)
            child = self._osc
        if (name == 'specific') and (self._processorName == self.getNodeName(attrs)) and (self._processorName != ''):
            try:
                self._processor = self.getBlenderCave().getProcessorModule().Configure(self, attrs)
            except AttributeError:
                import blender_cave.processor
                self._processor = blender_cave.processor.Configure(self, attrs)
            child = self._processor
        return self.addChild(child)

    def display(self, indent):
        self.print_display(indent, 'Processor : ')
        super(Processor, self).display(indent)

    def getConfiguration(self):
        configuration = {}

        if hasattr(self, '_vrpn'):
            configuration['vrpn'] = self._vrpn.getConfiguration()
        else:
            configuration['vrpn'] = {}

        if hasattr(self, '_osc'):
            configuration['osc'] = self._osc.getConfiguration()
        else:
            configuration['osc'] = {}

        try:
            configuration['processor'] = self._processor.getConfiguration()
        except AttributeError:
            configuration['processor'] = {}

        return configuration
