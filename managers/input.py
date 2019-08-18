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
		inputState = ['freeRoam', 'unitSelected', 'unitTarget']
		currentState = inputState[0]
		
		mappingMouse = {"1":"mouse1", "3":"wheel", "3":"mouse2", "4":"wheelUp", "5":"wheelDown"}
		mappingScrollDirections = ["scrollDown", "scrollUp", "scrollLeft", "scrollRight"]
		
		mapKeyUpUniversal = 	{}
		mapKeyDownUniversal = 	{"down":"keyScrollDown", 
												"up":"keyScrollUp",
												"left":"keyScrollLeft",
												"right":"keyScrollRight"}
		mapKeyUpFreeRoam = 		{"escape":"terminate", 
												"mouse1":"keyUnitSelect", 
												"e":"keyEventHandle", 
												"z":"keyEventUndo"}
		mapKeyDownFreeRoam = {}
		mapKeyUpUnitSelected =	{"escape":"keyCancelSelect", 
												"mouse1":"keySelectUnitMQ", 
												"a":"keySelectTarget", 
												"z":"keyResetUnitActions"}
		mapKeyDownUnitSelected = {}
		mapKeyUpUnitTarget = {"escape":"keyCancelTargeting",
											"mouse1":"keySelectUnitTarget"}
		mapKeyDownUnitTarget = {}
		
		mapKeyUpDict = {}
		mapKeyDownDict = {}
		
		def defineGlobals(self, EventManager, DrawingManager, MapManager, UnitManager):
			global EVENT0, WINDOW0, MAP0, UNIT0
			EVENT0 = EventManager
			WINDOW0 = DrawingManager
			MAP0 = MapManager
			UNIT0 = UnitManager
		
		def getInputState(self):
			return self.currentState
			
		def setInputState(self, num):
			self.currentState = self.inputState[num]
			if num == 0:
				 UNIT0.resetUnitSelected()
				 
		def handleInput(self):
			targetMethod = None
			targetMethodUni = None
			keyPressed = None
			keyUnPressed = None
			
			if self.getInputState() == 'freeRoam':
				self.mapKeyUpDict = self.mapKeyUpFreeRoam
				self.mapKeyDownDict = self.mapKeyDownFreeRoam
			elif self.getInputState() == 'unitSelected':
				self.mapKeyUpDict = self.mapKeyUpUnitSelected
				self.mapKeyDownDict = self.mapKeyDownUnitSelected
			elif self.getInputState() == 'unitTarget':
				self.mapKeyUpDict = self.mapKeyUpUnitTarget
				self.mapKeyDownDict = self.mapKeyDownUnitTarget
		
			for event in pygame.event.get():
				if event.type == QUIT:
					self.terminate()
					
				if event.type == MOUSEBUTTONDOWN:
					keyPressed = self.getMouseMap(event.button)
				
				elif event.type == KEYDOWN:
					keyPressed = pygame.key.name(event.key)
				
				elif event.type == MOUSEBUTTONUP:
					keyUnPressed = self.getMouseMap(event.button)
				
				elif event.type == KEYUP:
					keyUnPressed = pygame.key.name(event.key)
					
				if keyPressed in self.mapKeyDownDict.keys():
					getattr(self, self.mapKeyDownDict[keyPressed])()
				if keyPressed in self.mapKeyDownUniversal.keys():
					getattr(self, self.mapKeyDownUniversal[keyPressed])()
					
				if keyUnPressed in self.mapKeyUpDict.keys():
					getattr(self, self.mapKeyUpDict[keyUnPressed])()
				elif keyUnPressed in self.mapKeyUpUniversal.keys():
					getattr(self, self.mapKeyUpUniversal[keyUnPressed])()

		def getMouseMap(self, mouseButton):
			return self.mappingMouse[str(mouseButton)]
		
		#================= FREE ROAM MAPPINGS =================
					
		#TODO: fix selecting one of the units from Conflict
		def keyUnitSelect(self):
			coord = WINDOW0.pixeltohex(pygame.mouse.get_pos())
			units = MAP0.getUnitByCoord(coord)
			
			if units != None and len(units) != 0:
				UNIT0.setUnitSelected(MAP0.getUnitByCoord(coord)[0])
				self.setInputState(1)
				
			#adding/removing obstacles
			elif coord not in MAP0.MOARRAY:
				MAP0.MOARRAY.append(coord)
			else:
				for i in range(0, len(MAP0.MOARRAY)+1):
					if MAP0.MOARRAY[i] == coord:
						del MAP0.MOARRAY[i]
						break
		
		def keyEventHandle(self):
			EVENT0.eventHandle();
			
		def keyEventUndo(self):
			EVENT0.eventUndo()
		
		def keyScrollDown(self):
			WINDOW0.screenScrollDown()
		
		def keyScrollUp(self):
			WINDOW0.screenScrollUp()
		
		def keyScrollLeft(self):
			WINDOW0.screenScrollLeft()
		
		def keyScrollRight(self):
			WINDOW0.screenScrollRight()
		
		#================= UNIT SELECTED MAPPINGS =================
		
		def keyCancelSelect(self):
			self.setInputState(0)
		
		def keySelectUnitMQ(self):
			UNIT0.unitSelectedSetMQ(WINDOW0.pixeltohex(pygame.mouse.get_pos()))
			self.setInputState(0)
		
		def keySelectTarget(self):
			if UNIT0.getUnitSelected().canAttack == True:
				self.setInputState(2)
				
		def keyResetUnitActions(self):
			UNIT0.unitSelectedResetActions()
		
		#================= UNIT ATTACKING MAPPINGS =================
		
		def keyCancelTargeting(self):
			self.setInputState(1)
			
		def keySelectUnitTarget(self):
			UNIT0.setUnitTarget(UNIT0.getUnitSelected(), WINDOW0.pixeltohex(pygame.mouse.get_pos()))
		
		def mapKeys(self):
			utils.getKeyMap()
		
		def terminate(self):
			#print("Terminated on turn %s." % EVENT0.getTurnCounter())
			#print("============\n")
			pygame.quit()
			sys.exit()