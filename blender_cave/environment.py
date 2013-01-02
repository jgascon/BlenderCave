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

import os
import sys
import stat
import optparse
import logging
import blender_cave.exceptions
import blender_cave.base

class _OptionParser(optparse.OptionParser):

    def __init__(self):
        super(_OptionParser, self).__init__()
        self._errors = []

    def error(self, msg):
        self._errors.append(msg)
        pass

    def getErrors(self):
        return self._errors

class Environment(blender_cave.base.Base):

    def __init__(self, parent):
        super(Environment, self).__init__(parent)

        try:
            arguments = sys.argv[sys.argv.index('-'):]
        except ValueError:
            try:
                arguments = sys.argv[sys.argv.index('--'):]
            except ValueError:
                arguments = []

        parser = _OptionParser()
        parser.add_option("", "--config-path", dest="config_path", help="Configuration files path",      metavar="PATH")
        parser.add_option("", "--rb-file",     dest="rb_file",     help="Reload Backupper file",         metavar="PATH")
        parser.add_option("", "--blend-file",  dest="blend_file",  help="Blender (.blend) file to open", metavar="FILE")
        parser.add_option("", "--config-file", dest="config_file", help="Configuration file to open",    metavar="FILE")
        parser.add_option("", "--log-file",    dest="log_file",    help="Log file",                      metavar="FILE")
        parser.add_option("", "--verbosity",   dest="verbosity",   help="Log level",                     metavar="debug|info|warning|error|critical")
        parser.add_option("", "--screen",      dest="screen",      help="Screen to load")
        parser.add_option("", "--address",     dest="address",     help="Multicast address") 
        parser.add_option("", "--port",        dest="port",        help="Global address port",           metavar="port_number")

        (self._environment, args) = parser.parse_args(arguments)

        self.setLogger()

        parsing_errors = parser.getErrors()
        for parsing_error in parsing_errors:
            self._environment.logger.warning('Parsing error : "' + str(parsing_error) + '"')
        if len(parsing_errors) > 0:
            self._environment.logger.info(parser.get_usage())

    def processRemainingConfiguration(self):

        self._conf_paths = []
        if self._environment.config_path is not None:
            if stat.S_ISDIR(os.stat(self._environment.config_path).st_mode):
                self._conf_paths.append(self._environment.config_path)
            else:
                self.getLogger().warning(self._environment.config_path + ' BLENDER_CAVE_CONF_PATH environment variable is not a valid path.')
        if 'BLENDER_CAVE_CONF_PATH' in os.environ:
            if stat.S_ISDIR(os.stat(os.environ['BLENDER_CAVE_CONF_PATH']).st_mode):
                self._conf_paths.append(os.environ['BLENDER_CAVE_CONF_PATH'])
            else:
                self.getLogger().warning(os.environ['BLENDER_CAVE_CONF_PATH'] + ' BLENDER_CAVE_CONF_PATH environment variable is not a valid path.')
        self._conf_paths.append(os.getcwd())

        self._environment.config_file = self.checkConfigurationFile(self._environment.config_file, True)

        if self._environment.config_file is None:
            try:
                self._environment.config_file = self.checkConfigurationFile(os.environ['BLENDER_CAVE_CONF_FILE'], True)
            except KeyError:
                raise blender_cave.exceptions.Environment("Undefined configuration file !\nYou must at least define BLENDER_CAVE_CONF_FILE environment variable or --config as an argument !")

        if (self._environment.screen is None) and ('BLENDER_CAVE_CONF_SCREEN' in os.environ):
            self._environment.screen = os.environ['BLENDER_CAVE_CONF_SCREEN']

        if self._environment.port is not None:
            try:
                self._environment.port = int(self._environment.port)
            except ValueError:
                raise blender_cave.exceptions.Environment("Invalid port parameter : it must be an integer !")

    def setLogger(self):
        logger = logging.getLogger('BlenderCave')

        if self._environment.log_file is not None:
            log_file = self._environment.log_file
        elif 'BLENDER_CAVE_LOG_FILE' in os.environ:
            log_file = os.environ['BLENDER_CAVE_LOG_FILE']
        else:
            log_file = None
        del(self._environment.log_file)

        if log_file is None:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('[BlenderCave] %(levelname)s %(message)s'))
        else:
            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

        logger.addHandler(handler)

        if self._environment.verbosity is not None:
            verbosity = self._environment.verbosity.lower()
        elif 'BLENDER_CAVE_LOG_LEVEL' in os.environ:
            verbosity = os.environ['BLENDER_CAVE_LOG_LEVEL'].lower()
        else:
            verbosity = None
        del(self._environment.verbosity)

        if verbosity == 'debug':
            logger.setLevel(logging.DEBUG)
        elif verbosity == 'info':
            logger.setLevel(logging.INFO)
        elif verbosity == 'warning':
            logger.setLevel(logging.WARNING)
        elif verbosity == 'error':
            logger.setLevel(logging.ERROR)
        elif verbosity == 'critical':
            logger.setLevel(logging.CRITICAL)
        else:
            logger.setLevel(logging.WARNING)

        self._environment.logger = logger

    def checkConfigurationFile(self, filename, main):
        if filename is not None:
            if os.path.isabs(filename):
                if main:
                    self._conf_paths.insert(0, os.path.dirname(filename))
                    test_path = self._conf_paths
                else:
                    test_path = [os.path.dirname(filename)]
                filename = os.path.basename(filename)
            else:
                test_path = self._conf_paths
            for path in test_path:
                complete_filename = os.path.join(path, filename)
                try:
                    file = open(complete_filename)
                except:
                    continue
                return complete_filename
                    
        return

    def getEnvironment(self, key):
        return getattr(self._environment, key)

    def setEnvironment(self, key, value):
        setattr(self._environment, key, value)
