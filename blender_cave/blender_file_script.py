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

import blender_cave.base
import blender_cave.configure.base
import os
import imp

class Configure(blender_cave.configure.base.Base):
    def __init__(self, parent, attrs, name=''):
        super(Configure, self).__init__(parent, attrs, name)

class Main(blender_cave.base.Base):
    def __init__(self, parent, configuration):
        super(Main, self).__init__(parent)

def getBlenderFileModule(blender_file_name, doimport):
    if 'blender_file_module' in globals():
        return globals()['blender_file_module']
    module_path = os.path.dirname(blender_file_name)
    specific_name, ext = os.path.splitext(os.path.basename(blender_file_name))
    module_name = '_' + specific_name
    module = None
    file_name = None
    try:
        (file, file_name, data) = imp.find_module(module_name, [module_path])
    except:
        pass
    else:
        if doimport:
            module = imp.load_module(specific_name, file, file_name, data)
    globals()['blender_file_module'] = (module, file_name, module_name, specific_name)
    return globals()['blender_file_module']
