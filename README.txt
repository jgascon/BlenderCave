Copyright © LIMSI-CNRS (2011)

contributor(s) : Damien Touraine, David Poirier-Quinot, Laurent Pointal,
Julian Adenauer, Jorge Gascon

This software is a computer program whose purpose is to distribute
blender to render on CAVE(TM) device systems.

This software is governed by the CeCILL  license under French law and
abiding by the rules of distribution of free software.  You can  use, 
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info". 

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability. 

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.


How to use Blender-CAVE - LIMSI :
There is as many blender running than there is screen in the CAVE. Thus, there can be several blender running on a single computer. For instance, that is used inside SMART-I², where all four screens (ie. : 2 physical screens multiply by 2 - 1 stereoscopic on each screen) are rendered by the same computer.
Moreover, a Virtual Environment may display scenes for several users. For instance, EVE, allows two users working at the same time on the same screens. Each user has its own independant stereoscopic point of view on the scene.
Thus, the XML configuration file (look at EVE.xml to get documentation on the configuraion file) fully describe the Virtual Environment : users and screens.

Blender-CAVE contains several files.
All .py files represent the classes and the modules used by Blender-CAVE. The main module is blenderCAVE. It contains, a 'run()' function that process synchonization and update of the camera projection matrix. But before doing such tasks, the blenderCAVE module loads the configuration file to know the topology of the Virtual Rendering system.
The 'multi.blend' file is a sample file of how to include blenderCAVE in a scene.

Blender-CAVE rely on several environment variables :
* BLENDER_CAVE_PATH : the path where resides blenderCAVE classes and modules files.
* BLENDER_CAVE_CONF : the path where resides the XML configuration files (may be $BLENDER_CAVE_PATH).
* BLENDER_CAVE_CONF_FILE : the name of the configuration file to load (can be EVE.xml, smart-i2.xml or whatever else describing your own virtual environment).
* BLENDER_CAVE_CONF_SCREEN : the name of the screen to load as given inside XML configuration file.

BLENDER_CAVE_PATH and BLENDER_CAVE_CONF should be define as environment variables. BLENDER_CAVE_CONF_FILE and BLENDER_CAVE_CONF_SCREEN can be pass on blender command line. To do that, just launch blender plus '--' and the configuration file name and the screen name.
For instance : blender ??? -- EVE.xml control
BLENDER_CAVE_PATH, BLENDER_CAVE_CONF and BLENDER_CAVE_CONF_FILE must point to the sames paths and files on all nodes that render for the Virtual Environment. Ottherwise, there may be configuration problem.

Including head tracking is not done, now. But, it can be easily added by calling bge.logic.geometry.setUserPosition(userID, position), with 'userID' = the ID of the user and 'position' is a mathutils.Matrix representing the reference frame of the user.

For blenderCAVE to work, you should add this to an element that is run once
=============================================================
import sys
import os

if 'BLENDER_CAVE_PATH' in os.environ:
    sys.path.insert(0, os.environ['BLENDER_CAVE_PATH'])

import blender_cave

try:
    blender_cave.run()

except blender_cave.exceptions.Common as error:
    print(error)
