import pygame, sys
from pygame.locals import *
from utils import util

class InputManager(object):
	#singleton implementation
	instance = None
	
	def __init__(self):
		if not InputManager.instance:
			InputManager.instance = InputManager.__InputManager()
			
	def __getattr__(self, name):
		return getattr(self.instance, name)
	
	class __InputManager():
		inputState = ['moveSelection', 'unitSelected', 'unitTarget']
		currentState = inputState[0]
		heldKey = []
		
		def defineGlobals(self, EventManager, DrawingManager, MapManager, UnitManager):
			global EVENT0, WINDOW0, MAP0, UNIT0
			EVENT0 = EventManager
			WINDOW0 = DrawingManager
			MAP0 = MapManager
			UNIT0 = UnitManager
		
		def getState(self):
			return self.currentState
			
		def setState(self, num):
			self.currentState = self.inputState[num]
			if num == 0:
				 UNIT0.resetUnitSelected()
				 
		def handleInput(self):
		
			for event in pygame.event.get():	#this is chinese level of programming, needs fixing as well
				if event.type == QUIT:
					self.terminate()
				
				if event.type == KEYUP:
					if event.key == K_DOWN:		del self.heldKey[self.heldKey.index(K_DOWN)]
					elif event.key == K_UP:		del self.heldKey[self.heldKey.index(K_UP)]
					elif event.key == K_LEFT:		del self.heldKey[self.heldKey.index(K_LEFT)]
					elif event.key == K_RIGHT:	del self.heldKey[self.heldKey.index(K_RIGHT)]
					
				if event.type == KEYDOWN:
					if event.key == K_DOWN:		self.heldKey.append(K_DOWN)
					elif event.key == K_UP:		self.heldKey.append(K_UP)
					elif event.key == K_LEFT:		self.heldKey.append(K_LEFT)
					elif event.key == K_RIGHT:	self.heldKey.append(K_RIGHT)
				
				if self.getState() == 'moveSelection':
					if pygame.mouse.get_pressed() == (1, 0, 0):
						coord = WINDOW0.pixeltohex(pygame.mouse.get_pos())
						UNIT0.setUnitSelected(MAP0.getUnitByCoord(coord))
						if UNIT0.getUnitSelected() != None:	
							self.setState(1)
						elif coord not in MAP0.MOARRAY:
							MAP0.MOARRAY.append(coord)
						else:
							for i in range(0, len(MAP0.MOARRAY)+1):
								if MAP0.MOARRAY[i] == coord:
									del MAP0.MOARRAY[i]
									break
					
					if event.type == KEYDOWN:
						if event.key == K_ESCAPE:	self.terminate()
						elif event.key == K_e:			EVENT0.eventHandle()
						elif event.key == K_z:			EVENT0.eventUndo()
											
				elif self.getState() == 'unitSelected':
					unit = UNIT0.getUnitSelected()
					if pygame.mouse.get_pressed() == (1, 0, 0):
						coord = WINDOW0.pixeltohex(pygame.mouse.get_pos())
						path = MAP0.getPath(unit.statCur["SPD"], unit.getCoord(), coord)
						unit.setMoveQueue(path[::-1])
						self.setState(0)
					if event.type == KEYDOWN:
						if event.key == K_ESCAPE:		self.setState(0)
						elif event.key == K_a:			self.setState(2)
						elif event.key == K_z:			
							unit.resetMoveQueue()
							unit.resetTarget()
						
				elif self.getState() == 'unitTarget':
					unit = UNIT0.getUnitSelected()
					if pygame.mouse.get_pressed() == (1, 0, 0):
						if UNIT0.isTank(unit) or UNIT0.isArti(unit):
							FR = unit.statCur["FRmax"]
						else:
							self.setState(1)
							continue
							
						coord = WINDOW0.pixeltohex(pygame.mouse.get_pos())
						if util.getDistance(unit.getCoord(), coord) <= FR:
							isok = UNIT0.setTarget(unit, coord)
							if isok:
								self.setState(1)
							break
					if event.type == KEYDOWN:
						if event.key == K_ESCAPE:	self.setState(1)
						elif event.key == K_e:
							self.setState(1)
							
			if len(self.heldKey) != 0:
				for key in self.heldKey:
					if key == K_DOWN:		WINDOW0.screenScroll([0, -1])
					elif key == K_UP:			WINDOW0.screenScroll([0, +1])
					elif key == K_LEFT:		WINDOW0.screenScroll([+1, 0])
					elif key == K_RIGHT:	WINDOW0.screenScroll([-1, 0])

		def terminate(self):
			#print("Terminated on turn %s." % EVENT0.getTurnCounter())
			#print("============\n")
			pygame.quit()
			sys.exit()