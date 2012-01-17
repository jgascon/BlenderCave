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
from . import exceptions

def loadBlenderCave():
    if hasattr(bge.logic, 'initiated') == False:
        # Then, we must initiate blender_cave !
        bge.logic.initiated = False # Start by saying it is not configured !
        # If the geometry is not 
        if hasattr(bge.logic, 'geometry') == False:
            if hasattr(bge.logic, 'alreadyConfigure'):
                raise exceptions.Main("Already tried to configure !")
            from . import configure
        if hasattr(bge.logic, 'geometry') == False:
            raise exceptions.Main("Cannot load configuration of the current Virtual Environment !")
        if hasattr(bge.logic, 'synchronizer') == False:
            raise exceptions.Main("Cannot load synchronization system of the current Virtual Environment !")
        scene = bge.logic.getCurrentScene()
        scene.pre_render.append(run)
        bge.logic.initiated = True
    elif bge.logic.initiated == False:
        return False
    return True

def run():
    try:
        bge.logic.synchronizer.run()
    except exceptions.Quit as quit:
        print(quit)
        bge.logic.endGame()
        sys.exit()
    bge.logic.geometry.updateProjectionMatrices()

def quit(reason):
    raise exceptions.Quit(reason)

def getUserPosition(userID):
    if hasatt(bge.logic, 'geometry') == False:
        raise exceptions.Main("Error: blender_cave must be initialized first !")
    return bge.logic.geometry.getUserPosition(userID)
    
def setUserPosition(userID, position):
    if hasatt(bge.logic, 'geometry') == False:
        raise exceptions.Main("Error: blender_cave must be initialized first !")
    bge.logic.geometry.setUserPosition(userID, position)
    
def isMaster():
    if hasatt(bge.logic, 'geometry') == False:
        raise exceptions.Main("Error: blender_cave must be initialized first !")
    return bge.logic.geometry.isMaster()

#Scale and objects to synchronize can be defined before the geometry or the synchronizer are defined ...

def getScale():
    if hasattr(bge.logic, 'blender_cave_scale'):
        return bge.logic.blender_cave_scale
    return 1

def setScale(scale):
    if scale > 0:
        bge.logic.blender_cave_scale = scale
    
def addObjectToSynchronize(objectToSynchronize):
    synchronizer.addObjectToSynchronize(objectToSynchronize)
