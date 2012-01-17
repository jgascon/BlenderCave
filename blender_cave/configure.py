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

import sys
import xml.dom.minidom
import string
import socket
import bge
import os
from . import geometry
from . import synchronizer
from . import user
from . import exceptions

""" @package configure
Must be import only once : for the first start of the application
"""

if hasattr(bge.logic, 'geometry') or hasattr(bge.logic, 'synchronizer'):
    raise exceptions.Configure("Implementation error : XML configuration file already loaded !")


def loadConfigurationFile(fileName):
    if 'BLENDER_CAVE_CONF' in os.environ:
        fileName = os.path.join(os.environ['BLENDER_CAVE_CONF'], fileName)
    try:
        file = xml.dom.minidom.parse(fileName)
    except IOError:
        return False
    globals()['xmlFile'] = file
    globals()['xmlFileName'] = fileName
    return True
    

def parseCommandLine():
    if (sys.argv[0] == 'blenderplayer'):
        argument_separator = '-'
    else:
        argument_separator = '--'
    if (argument_separator in sys.argv):
        indexOfMinusMinus = sys.argv.index(argument_separator)
        for index in range(indexOfMinusMinus + 1, len(sys.argv)):
            if ('XML_FileName' in locals()) == False:
                if os.path.splitext(sys.argv[index])[1] == '.xml':
                    XML_FileName = sys.argv[index]
                    continue
            if ('screenNameToLoad' in globals()) == False:
                globals()['screenNameToLoad'] = sys.argv[index]
            if ('screenNameToLoad' in globals()) and ('XML_FileName' in locals()):
                break
    if 'XML_FileName' in locals():
        if loadConfigurationFile(XML_FileName) == False:
            raise exceptions.Configure("Warning, invalid XML file or too many configuration specified")

def screenConfiguration(node, is_current_computer):
    if node.nodeName != 'screen':
        return
    if ('nbScreens' in globals()) == False:
        globals()['nbScreens'] = 0
    else:
        globals()['nbScreens'] = globals()['nbScreens'] + 1
    if is_current_computer == False:
        return
    if node.hasAttributes():
        if 'screenNameToLoad' in globals() and 'name' in node.attributes:
            if node.attributes['name'].value != globals()['screenNameToLoad']:
                return
        if 'currentGeometry' in globals():
            del globals()['currentGeometry']
            if 'screenNameToLoad' in globals():
                raise exceptions.Configure("Configuration File Error : several screens with the same name " + globals()['screenNameToLoad'] + " available")
            else:
                raise exceptions.Configure("Configuration File Error : several screens available, but no window specified in the command line")
            return
        globals()['currentScreenID'] = globals()['nbScreens']
        try:
            globals()['currentGeometry'] = geometry.VEC(node, globals()['nbScreens']);
        except exceptions.Configure as error:
            del globals()['currentGeometry']
            return

def computerConfiguration(node):
    if node.nodeName != 'computer':
        return
    if node.hasAttributes():
        if ('name' in node.attributes) == False:
            return
        if node.attributes['name'].value == '*':
            node.attributes['name'].value = socket.gethostname()
        if ('master_computer' in globals()) == False:
            globals()['master_computer'] = node.attributes['name'].value
        if node.attributes['name'].value == socket.gethostname():
            is_current_computer = True
        else:
            is_current_computer = False
        child = node.firstChild
        while child:
            screenConfiguration(child, is_current_computer);
            child = child.nextSibling

def userConfiguration(node):
    if node.nodeName != 'user':
        return
    try:
        currentUser = user.User(node)
        if ('users' in globals()) == False:
            globals()['users'] = {}
        globals()['users'][currentUser.getID()] = currentUser
    except user.UserException as inst:
        return

def mainConfiguration(node):
    global synchroPort
    global synchroAddress
    if node.nodeName != 'virtualEnvironment':
        return

    if node.hasAttributes():
        if 'synchroPort' in node.attributes:
            try:
                synchroPort = int(node.attributes['synchroPort'].value)
            except ValueError:
                raise exceptions.Configure("Configuration file error : synchroPort must be an int !")
                
        if 'synchroAddress' in node.attributes:
            synchroAddress = node.attributes['synchroAddress'].value

    child = node.firstChild
    while child:
        userConfiguration(child)
        computerConfiguration(child)
        child = child.nextSibling

bge.logic.alreadyConfigure = True

parseCommandLine()

if (('xmlFile' in locals()) == False) and ('BLENDER_CAVE_CONF_FILE' in os.environ):
    if loadConfigurationFile(os.environ['BLENDER_CAVE_CONF_FILE']) == False:
        raise exceptions.Configure("\"" + os.environ['BLENDER_CAVE_CONF_FILE'] + "\" invalid configuration file from \"BLENDER_CAVE_CONF_FILE\" environment variable !")

if (('xmlFile' in locals()) == False):
    raise exceptions.Configure("Usage : " + sys.argv[0] + " blender_options -- configuration_file current_configuration")

if (('screenNameToLoad' in locals()) == False) and ('BLENDER_CAVE_CONF_SCREEN' in os.environ):
    locals()['screenNameToLoad'] = os.environ['BLENDER_CAVE_CONF_SCREEN']

if xmlFile.hasChildNodes() == False:
    raise exceptions.Configure("Invalid configuration file (" + xmlFileName + ") !")

mainConfiguration(xmlFile.firstChild)

if (('synchroPort' in locals()) == False) or (('synchroAddress' in locals()) == False):
    raise exceptions.Configure('Missing synchroPort and synchroAddress from configuration file !')

if ('currentGeometry' in locals()) == False:
    if 'screenNameToLoad' in locals():
        raise exceptions.Configure('Cannot read configuration "' + screenNameToLoad + '" from ' + xmlFileName + ' !')
    else:
        raise exceptions.Configure('Cannot read any configuration from ' + xmlFileName)

if ('users' in locals()) == False:
    raise exceptions.Configure('Cannot read any user from ' + xmlFileName)

bge.logic.geometry = currentGeometry

print(" Configuration file : " + xmlFileName)
if 'screenNameToLoad' in locals():
    print("  Screen name : " + screenNameToLoad)

if (bge.logic.geometry.isMaster()):
    print("  I'm the rendering master !")
else:
    print("  I'm one of the the rendering slave (master is : " + master_computer + ") !")

nbScreens = nbScreens + 1

bge.logic.geometry.finalizeConfiguration(users)
bge.logic.synchronizer = synchronizer.Synchronizer(bge.logic.geometry.isMaster(), synchroPort, synchroAddress, nbScreens, master_computer, currentScreenID)
