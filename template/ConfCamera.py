
import GameLogic

scene = GameLogic.getCurrentScene()
cam = scene.objects["OBCamera_" + GameLogic.cam]
scene.active_camera = cam

near = cam.near
far = cam.far
top = near
bottom = -near
	
if GameLogic.cam == "Bottom":
	bottom = -near * 0.5
	
	
matriz = [[1.0, 0.0, 0.0, 0.0],
					[0.0, 2*near/(top-bottom), (top+bottom)/(top-bottom), 0.0],
					[0.0, 0.0, (-far+near)/(far-near), -2*far*near/(far-near)],
					[0.0, 0.0, -1.0,  0.0]] 
	
#matrizs = [	[m[0][0], 0.0,(right+left)/(right-left), 0.0],
	#			[0.0, 2* near/(top - bottom),  (top+bottom)/(top-bottom), 0.0],
		#		[0.0 , 0.0, GameLogic.prev_matrix[2][2], GameLogic.prev_matrix[2][3]],
			#	[0.0, 0.0, -1.0,  0.0]] 
cam.projection_matrix = matriz
