import bge
import os

if 'with_blender_cave' not in locals():
    try:
        import blender_cave
        with_blender_cave = True
    except ImportError:
        with_blender_cave = False

timer      = 0
frameRates = []

def run():
    global timer, frameRates, with_blender_cave

    if with_blender_cave:
        blender_cave.run()

    frameRates.append(round(bge.logic.getAverageFrameRate(),2))

    timer += 1
    if timer >= 500:

        if with_blender_cave:
            if blender_cave.isMaster():
                record('results_'+str(blender_cave.numberScreens()))
                blender_cave.quit("end of bench !")
        else:
            record('results')
            bge.logic.endGame()

def record(fileName):
    global frameRates

    fileName = os.path.join(bge.logic.expandPath('//'), 'records', fileName)
    File = open(fileName, 'w')
    File.write(str(frameRates))
    File.close()
