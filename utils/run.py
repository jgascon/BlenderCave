#!/usr/bin/env python3.2
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

import optparse
import sys
import os
import socket
import subprocess
import signal

def testCreatePath(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def quoteString(string):
    if ' ' in string:
        return '"' + string + '"'
    return string

parser = optparse.OptionParser()

parser.add_option("",   "--blender-player",    dest="blender_player")
parser.add_option("",   "--python-path",       dest="python_path")
parser.add_option("",   "--blender-cave-path", dest="blender_cave_path")
parser.add_option("",   "--pid-path",          dest="pid_path")
parser.add_option("",   "--screen",            dest="screen")
parser.add_option("",   "--command",           dest="command")
parser.add_option("",   "--options",           dest="options")
parser.add_option("",   "--blender-file",      dest="blender_file")
parser.add_option("",   "--config-file",       dest="config_file")
parser.add_option("",   "--config-path",       dest="config_path")
parser.add_option("",   "--log-path",          dest="log_path")
parser.add_option("-c", action="store_true",   dest="clear_previous")
parser.add_option("-b", action="store_true",   dest="background")
parser.add_option("",   "--verbosity",         dest="verbosity")
parser.add_option("",   "--display",           dest="display")
parser.add_option("",   "--rb-path",           dest="rb_path")

(options, args) = parser.parse_args(sys.argv)

blender_cave_path = options.blender_cave_path

computer = socket.gethostname()

testCreatePath(options.pid_path)
pid_file = os.path.join(options.pid_path, 'blender_cave_' + computer + '_' + options.screen + '.pid')

testCreatePath(options.log_path)
log_file = os.path.join(options.log_path, 'blender_cave_' + computer + '_' + options.screen + '.log')
log_run_file = os.path.join(options.log_path, 'run_blender_cave_' + computer + '_' + options.screen + '.log')
log_run_file = os.devnull

testCreatePath(options.rb_path)
rb_file = os.path.join(options.rb_path, 'blender_cave_!PID!.dat')

if options.command == 'stop':
    try:
        file = open(pid_file, 'r')
    except:
        pass
    else:
        pid = file.read(1024)
        file.close()
        try:
            os.kill(int(pid), signal.SIGTERM)
        except OSError:
            pass
        try:
            os.remove(pid_file)
        except:
            pass
        if options.clear_previous:
            rb_file = rb_file.replace('!PID!', str(pid))
            try:
                os.remove(rb_file)
            except:
                pass
            
            
            
elif options.command == 'start':
    if options.clear_previous:
        try:
            os.remove(log_file)
        except:
            pass

    environment = os.environ

    python_path = [blender_cave_path]
    if 'PYTHONPATH' in os.environ:
        python_path += os.environ['PYTHONPATH'].split(':')
    if options.python_path is not None:
        python_path += options.python_path.split(':')
    environment['PYTHONPATH'] = quoteString(':'.join(python_path))

    if options.display is not None:
        environment['DISPLAY'] = options.display
    else:
        environment['DISPLAY'] = ":0"

    if sys.platform == "win32":
        environment['SystemRoot'] = os.path.join('C:',os.sep,'Windows')

    command = []
    if options.blender_player is not None:
        command.append(quoteString(options.blender_player))
    else:
        if sys.platform == "win32":
            blender_program = "blenderplayer.exe"
        else:
            blender_program = "blenderplayer"
        for path in os.environ["PATH"].split(os.pathsep):
            file = os.path.join(path, blender_program)
            if os.path.isfile(file) and os.access(file, os.X_OK):
                command.append(quoteString(file))
                break

    if len(command) == 0:
        print('Cannot load Blender Player !')
        sys.exit()

    if options.options is not None:
        command += options.options.split(' ')

    command += [quoteString(options.blender_file), '-']

    command.append('--screen=' + options.screen)

    command.append('--config-file='+quoteString(options.config_file))

    command.append('--config-path='+quoteString(options.config_path))

    if options.background:
        command.append('--log-file=' + quoteString(log_file))
        if options.clear_previous:
            try:
                os.remove(log_file)
            except:
                pass
            

    if options.verbosity is not None:
        command.append('--verbosity=' + options.verbosity)

    command.append('--rb-file=' + rb_file)

    if options.background:
        with open(log_run_file, "w") as fnull:
            process = subprocess.Popen(command, env=environment, stderr=fnull, stdout=fnull)
            file = open(pid_file, 'w')
            file.write(str(process.pid))
            file.close()
    else:
        subprocess.Popen(command, env=environment).communicate()[0]
