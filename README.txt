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

BEWARE: Blender-CAVE requires a patched version of Blender. The patch can be found in 'patch/blender_revision_????????.patch'.


How to use Blender-CAVE - LIMSI :
There is as many blender running than there is screen in the CAVE. Thus, there can be several blender running on a single computer. For instance, that is used inside SMART-I², where all four screens (ie. : 2 physical screens multiply by 2 - 1 stereoscopic on each screen) are rendered by the same computer.
Moreover, a Virtual Environment may display scenes for several users. For instance, EVE, allows two users working at the same time on the same screens. Each user has its own independant stereoscopic point of view on the scene.
Thus, the XML configuration file (look at sample.xml to get documentation on the configuraion file) fully describe the Virtual Environment : users, screens, VRPN connexion ...

Blender-CAVE contains several files.
All .py files represent the classes and the modules used by Blender-CAVE. The main module is blender_cave. You just have to import this module to load BlenderCave. Moreover, you should run blender_cave.run() each frame to update "external" modules (VRPN, OSC ...).

BlenderCave is running through BlenderCave.py script. You must edit its head (until "# Below, you should not have to modify anything ...") to adapt it to your configuration.

For Blender-CAVE to work, you should add this python code to a Logic Controller that is run 'always' (ie. : each frame).
=============================================================
import blender_cave

blender_cave.run()
