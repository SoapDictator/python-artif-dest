#
#Artificially Destined
#=============
#by SoapDictator
#

import pygame, sys, math
from pygame.locals import *

sys.path.append('/AD/obj')
sys.path.append('/AD/managers')
sys.path.append('/AD/utils')
from managers import event, window, input, unit, map
		
class Main(object):
	#singleton implementation
	instance = None
	
	def __init__(self):
		if not Main.instance:
			Main.instance = Main.__Main()
			
	def __getattr__(self, name):
		return getattr(self.instance, name)
	
	class __Main():
		def __init__(self):
			global EVENT0, WINDOW0, INPUT0, UNIT0, MAP0
			EVENT0 = event.GameEventManager()
			WINDOW0 = window.WindowManager()
			INPUT0 = input.InputManager()
			UNIT0 = unit.UnitManager()
			MAP0 = map.MapManager()
			
			EVENT0.defineGlobals(EVENT0, MAP0, UNIT0)
			WINDOW0.defineGlobals(INPUT0, MAP0, UNIT0)	
			INPUT0.defineGlobals(EVENT0, WINDOW0, MAP0, UNIT0)
			MAP0.defineGlobals(WINDOW0, UNIT0)
			UNIT0.defineGlobals(WINDOW0, MAP0, UNIT0)
			
			#regression(haha) tests
			#self.testTankAttack().testArtiAttack().testUnitCastAbility()
			
			#for manual testing
			# self.testCreateUnits()
			
			pygame.key.set_repeat(50,50)
			
			while True:
				INPUT0.handleInput()
				WINDOW0.screenRefresh()
		
		#TESTS
		def testCreateUnits(self):
			EVENT0.eventAdd("EventUnitCreate", ("UA000", [-4, -3], "player1"))
			EVENT0.eventAdd("EventUnitCreate", ("UA000", [4, 3], "player2"))
			EVENT0.eventAdd("EventUnitCreate", ("US000", [-3, -4], "player1"))
			EVENT0.eventAdd("EventUnitCreate", ("US000", [3, 4], "player2"))
			EVENT0.eventHandle()
			
			return self
		
		def testUnitMove(self):
			EVENT0.eventAdd("EventUnitCreate", ("UT000", [0, 0], "player1"))
			EVENT0.eventHandle()
			
			tstUnit0 = units[len(units)-1]
			tstUnit0.setMoveQueue(MAP0.getPath(tstUnit0.getStatCur("SPD"), tstUnit0.getCoord(), [3, 3]))
			EVENT0.eventHandle()
			
			try:
				assert(tstUnit0.getCoord() == [3, 3])
			except:
				print("Test Fail: UT000 horribly failed to move!")
			UNIT0.unitDestroy(tstUnit0)
			return self
		
		def testTankAttack(self):
			EVENT0.eventAdd("EventUnitCreate", ("UT000", [0, 0], "player1"))
			EVENT0.eventAdd("EventUnitCreate", ("US000", [1, 1], "player2"))
			EVENT0.eventHandle()
			
			units = UNIT0.getAllUnits()
			tstUnit0 = units[len(units)-2]
			tstUnit1 = units[len(units)-1]
			
			UNIT0.setUnitTarget(tstUnit0, tstUnit1.getCoord())
			EVENT0.eventHandle()
			
			UNIT0.unitDestroy(tstUnit0)
			try:
				assert(tstUnit1.getStatCur("HP") <= 0)
			except:
				print("Test Fail: Tank's attack failed horribly!")
				UNIT0.unitDestroy(tstUnit1)
			return self
			
		def testArtiAttack(self):
			EVENT0.eventAdd("EventUnitCreate", ("UA000", [0, 0], "player1"))
			EVENT0.eventAdd("EventUnitCreate", ("US000", [3, 3], "player2"))
			EVENT0.eventHandle()
			
			units = UNIT0.getAllUnits()
			tstUnit0 = units[len(units)-2]
			tstUnit1 = units[len(units)-1]
			
			UNIT0.setUnitTarget(tstUnit0, tstUnit1.getCoord())
			EVENT0.eventHandle()
			
			UNIT0.unitDestroy(tstUnit0)
			try:
				assert(tstUnit1.getStatCur("HP") <= 0)
			except:
				print("Test Fail: Artillery's attack failed horribly!")
				UNIT0.unitDestroy(tstUnit1)
			return self
			
		def testUnitCastAbility(self):
			EVENT0.eventAdd("EventUnitCreate", ("UE000", [0, 0], "player1"))
			EVENT0.eventAdd("EventUnitCreate", ("US000", [1, 1], "player1"))
			EVENT0.eventHandle()
			
			units = UNIT0.getAllUnits()
			tstUnit0 = units[len(units)-2]
			tstUnit1 = units[len(units)-1]
			
			tstUnit0.castAbility("A001", tstUnit1)
			EVENT0.eventHandle()
			
			UNIT0.unitDestroy(tstUnit0)
			UNIT0.unitDestroy(tstUnit1)
			return self

StartShenanigans = Main()