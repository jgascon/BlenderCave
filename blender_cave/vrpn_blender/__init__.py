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
import os
import sys
import imp
import logging
from .. import exceptions
from . import processor

try:
    from . import tracker
    from . import analog
    from . import button
except ImportError:
    print('No VRPN Available !')

if hasattr(bge.logic, 'vrpn') == False:
    bge.logic.vrpn = []

def callback(userdata, info):
    print(type(userdata), info)

def configure(node):


    try:
        blend_filename = bge.logic.getCurrentBlendName()
        vrpn_module_path = os.path.dirname(blend_filename)
        module_name, ext = os.path.splitext(os.path.basename(blend_filename))
        module_name = 'vrpn_' + module_name
        (file, filename, data) = imp.find_module(module_name, [vrpn_module_path])
        imp.load_module('vrpn_processor', file, filename, data)
        logging.debug('Loading  "' + filename + '" as vrpn processor')
    except ImportError:
        print('Cannot import "' + module_name + '" module')
        bge.logic.vrpn_processor = processor.Processor()
        
    if not hasattr(bge.logic, 'vrpn_processor'):
        print('Module "' + module_name + '" did not define bge.logic.vrpn_processor !')
        bge.logic.vrpn_processor = processor.Processor()

    if not isinstance(bge.logic.vrpn_processor, processor.Processor):
        print('Module "' + module_name + '" did not define bge.logic.vrpn_processor as an instance (or a son) of processor.Processor !')
        bge.logic.vrpn_processor = processor.Processor()

    child = node.firstChild
    while child:
        if child.nodeName == 'tracker':
            try:
                bge.logic.vrpn.append(tracker.Tracker(child))
            except exceptions.VRPN as inst:
                print(inst)
            except NameError:
                pass
        if child.nodeName == 'analog':
            try:
                bge.logic.vrpn.append(analog.Analog(child))
            except exceptions.VRPN as inst:
                print(inst)
            except NameError:
                pass
        if child.nodeName == 'button':
            try:
                bge.logic.vrpn.append(button.Button(child))
            except exceptions.VRPN as inst:
                print(inst)
            except NameError:
                pass
        child = child.nextSibling

def run():
    for index in range(len(bge.logic.vrpn)):
        bge.logic.vrpn[index].run()
