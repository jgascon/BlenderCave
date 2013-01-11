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

import os
import sys
import py_compile
import compileall

class WorkOnBlenderCave:
    def __init__(self, blender_cave_path, config_file):
        self._blender_cave_path = blender_cave_path
        self._config_file       = config_file

        sys.path.append(self._blender_cave_path)

    def compileBlenderCave(self):
        compileall.compile_dir(os.path.join(self._blender_cave_path, 'blender_cave'), quiet = True)

    def getConfiguration(self):
        from blender_cave import environment
        self._environment = environment.Environment(None)
        self._environment.setEnvironment('config_file', self._config_file)
        self._environment.processRemainingConfiguration()

        import fake_blender_cave

        Fake = fake_blender_cave.FakeBlenderCave(self._environment)

        from blender_cave import configure 
        configurator  = configure.Configure(Fake, self._environment, True)
        configuration = configurator.getConfiguration()

        if '*' in configuration:
            configuration['localhost'] = configuration['*']
            del(configuration['*'])

        return configuration

    def compileBlenderFileModule(self, blender_file_name):
        module_path = os.path.dirname(blender_file_name)
        specific_name, ext = os.path.splitext(os.path.basename(blender_file_name))
        try:
            py_compile.compile(os.path.join(module_path, '_' + specific_name + '.py'))
        except IOError:
            pass
            
        
