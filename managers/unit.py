import pygame, sys, math
from pygame.locals import *

from utils import util
from obj import units

class UnitManager(object):
	#singleton implementation
	instance = None
	
	def __init__(self):
		if not UnitManager.instance:
			UnitManager.instance = UnitManager.__UnitManager()
			
	def __getattr__(self, name):
		return getattr(self.instance, name)
		
	class __UnitManager():
		PLAYERS = {"player1": 0, "player2": 1}
		UNITS = ["UT000", "US000", "UA000", "UE000"]
		UNITSTATES = ["Operational", "Conflicted", "Banished", "Destroyed"]
		ABILITIES = ["A001", "A002"]
		EFFECTS = []
		
		#array of ALL units on the map
		unitArray = []
		
		playerSelectedDEFAULT = None
		playerSelected = None
		unitSelectedDEFAULT = None	#default value for a selected unit
		unitSelected = None
		
		moveTickNom = 50
		moveTick = 0
		
		playerFOV = []
		playerUnitsVisible = []
		
		def __init__(self):
			self.setPlayerSelected("player1")
			self.resetPlayerFOV()
		
		def defineGlobals(self, DrawingManager, MapManager, UnitManager):
			global WINDOW0, MAP0, UNIT0
			WINDOW0 = DrawingManager
			MAP0 = MapManager
			UNIT0 = UnitManager
		
		#unit object factory
		def unitCreate(self, unitType, coord, player):
			if unitType not in self.UNITS:
				pass
			if len(coord) != 2:
				pass
			if player not in self.PLAYERS:
				pass
			
			toQ = coord[0]
			toR = coord[1]
			
			#object factory, nothing to see here
			targetUnit = getattr(units.Units, unitType)
			NewUnit = targetUnit()
			self.unitArray.append(NewUnit)
			
			#checking that the unit was properly created
			assert(NewUnit != None, "(Unit object factory) Failed to create the unit")
			
			#assigning values and adding the unit into appropriate arrays
			NewUnit.setOwnerId(self.PLAYERS[player])
			NewUnit.setCreationId(len(self.unitArray)-1)
			NewUnit.setCoord(toQ, toR)
			NewUnit.resetMoveQueue()
			
			if len(NewUnit.statAbilities) > 0:
				for abilityID in NewUnit.statAbilities:
					self.unitAddAbility(abilityID, NewUnit)
		
		def unitDestroy(self, deletedUnit):
			if deletedUnit not in self.unitArray:
				pass
			
			del self.unitArray[self.unitArray.index(deletedUnit)]
		
		#if 2 or more units end up in the same coordinate they become Conflicted
		def moveResolveConflicts(self):
			array = self.unitArray
			for j in range(0, len(array)-1):
				self.unitArray[j].resetState()
				for k in range(j+1, len(array)-1):
					if array[j].getCoord() == array[k].getCoord():
						array[j].setState(self.UNITSTATES[1])
					
		
		def unitMoveStart(self, units):
			flags = [0]*len(units)
			
			while True:
				flags = self.unitMoveTick(units, flags)
				 
				summ = sum(flags)
				if summ == len(units) or self.moveTick > self.moveTickNom:
					break
				pygame.time.delay(75)
				
			self.unitMoveReset(units)
			self.moveResolveConflicts()
		
		#moves units according to their movement queues in moveQueue
		def unitMoveTick(self, units, flags):		
			step = self.moveTick+1
			summ = 0
			
			for i in range (0, len(units)):
				if flags[i] == 1:
					continue
					
				curMoveQueue = units[i].getMoveQueue()
				
				if len(curMoveQueue) <= 1 or step >= len(curMoveQueue):
					flags[i] = 1
					continue
					
				units[i].setCoord(curMoveQueue[step][0], curMoveQueue[step][1])
				
			self.moveTick = step
			return flags
		
		def unitMoveReset(self, units):
			self.moveTick = 0
			
			for unit in units:
				unit.resetMoveQueue()
		
		def unitAddAbility(self, abilityID, caster):
			if abilityID not in self.ABILITIES:
				pass
				
			targetAbility = getattr(Abilities, abilityID)
			instance = targetAbility(caster)
			caster.instAbilities.append(instance)

		def setUnitTarget(self, unit, targetCoord):
			unit.setTarget(targetCoord)
			if unit.getTarget() != None:
				return True
			return False
	
		def setUnitMoveQueue(self, unit, targetCoord):
			path = MAP0.getPath(unit.statCur["SPD"], unit.getCoord(), targetCoord)
			unit.setMoveQueue(path[::-1])
	
		def getUnitById(self, unitId):
			for unit in self.unitArray:
				if unit.getCreationId == unitId:
					return unit
			return None
	
		#================= SELECTED UNIT =================
	
		def getUnitSelected(self):
			return self.unitSelected
			
		def resetUnitSelected(self):
			self.unitSelected = self.unitSelectedDEFAULT
			
		def setUnitSelected(self, unit):
			if unit == self.unitSelectedDEFAULT:
				return
			self.unitSelected = unit
			
		def unitSelectedSetMQ(self, coord):
			self.setUnitMoveQueue(self.unitSelected, coord)
			
		def unitSelectedResetActions(self):
			self.unitSelected.resetActions()
			
		def unitSelectedSetTarget(self):
			self.unitSelected.setTarget()
		
		#================= ALL UNITS =================
		
		def isScout(self, unit):
			if unit.getType() == "scout":
				return True
			return False
			
		def isTank(self, unit):
			if unit.getType() == "tank":
				return True
			return False
			
		def isArti(self, unit):
			if unit.getType() == "artillery":
				return True
			return False
			
		def isEngi(self, unit):
			if unit.getType() == "engineer":
				return True
			return False
		
		def getAllUnits(self):
			return self.unitArray
		
		def getTanks(self):
			return list(filter(self.isTank, self.unitArray))
			
		def getScouts(self):
			return list(filter(self.isScout, self.unitArray))
			
		def getArties(self):
			return list(filter(self.isArti, self.unitArray))
			
		def getEngies(self):
			return list(filter(self.isEngi, self.unitArray))
			
		def getUnitsOwnedByPlayer(self, playerId):
			ownedUnits = []
			for unit in self.unitArray:
				if unit.getOwnerId() == playerId:
					ownedUnits.append(unit)
					
			return ownedUnits
		
		#================= PLAYERS =================
		
		def getPlayerSelected(self):
			return self.playerSelected
		
		def getPlayerSelectedID(self):
			return self.PLAYERS[self.playerSelected]
		
		def setPlayerSelected(self, player):
			if player not in self.PLAYERS:
				pass
			self.playerSelected = player
			
		def getPlayerFOV(self, playerId):
			return self.playerFOV[playerId][:]
			
		def resetPlayerFOV(self):
			del self.playerFOV[:]
			for i in range(0, len(self.PLAYERS)):
				self.playerFOV.append([])
				self.playerUnitsVisible.append([])
				
		def getPlayerVisibleUnits(self, playerId):
			unitsVisible = []
			for unit in self.unitArray:
				if unit.getCreationId in self.playerUnitsVisible:
					unitsVisible.append(unit)
			return unitsVisible
		
		def calcPlayerFOV(self):
			self.resetPlayerFOV()
			toBeFOV = []
			toBeUnitsVisible = []
			
			for player in self.PLAYERS:
				ID = self.PLAYERS[player]
				
				#calculating visible area for each unit and adding it to respecti
				for unit in self.getUnitsOwnedByPlayer(ID):
					for hex in MAP0.getVisibility(unit.getStatCur("VR"), unit.getCoord()):
						if hex not in toBeFOV:
							toBeFOV.append(hex)
								
				for unit in self.unitArray:
					if unit.getCoord in toBeFOV:
						toBeUnitsVisible.append(unit.getCreationId())
						
				self.playerFOV[ID] = toBeFOV[:]
				self.playerUnitsVisible[ID] = toBeUnitsVisible[:]
				del toBeFOV[:]
				del toBeUnitsVisible[:]
						
			
#------------------------------------------
#------------------------------------------
class Abilities:
	class Ability(object):
		id = "A000"
		statName = "PrototypeAbility"
		priority = 0
		isActivated = False
		caster = None
		effects = []
		
		def __init__(self, caster):
			self.caster = caster
		
		#transfers casting data and checks the activation conditions
		def activate(self,data):
			self.isActivated = True
			
		def deactivate(self):
			self.isActivated = False
		
		#action of the activated ability
		def execute(self):
			print("This is a prototype ability, get out!")
			
		def getId(self):
			return self.id
			
		def getCaster(self):
			return self.caster
			
		def isActivated(self):
			return isActivated

	class A001(Ability):
		id = "A001"
		statName = "EngieHeal"
		priority = 30
		
		#takes targeted unit as data
		def activate(self, data):
			self.target = data
			
			dist = util.getDistance(self.caster.statCoord, self.target.statCoord)
			if dist <= self.caster.getStatCur("VR"):
				self.isActivated = True
		
		def execute(self):
			addedHP = 5
			self.target.setStatCur("HP", self.target.getStatCur("HP")+addedHP)
			if self.target.getStatCur("HP") > self.target.getStatNom("HP"):
				self.setStatCur("HP", self.target.getStatNom("HP"))
			self.deactivate()
			
			print("Added %s HP to %s(now %s HP)" % (addedHP, self.target, self.target.getStatCur("HP")))
			
	class A002(Ability):
		id = "A002"
		statName = "ReplenishAmmo"
		priority = 30
		
		def activate(self, data):
			self.isActivated = True # passive ability, therefore it's always activated
		
		def execute(self):
			addedAmmo = 5
			for dir in MAP0.DIRECTIONS:
				hex = [0, 0]
				hex[0] = self.caster.statCoord[0] + dir[0]
				hex[1] = self.caster.statCoord[1] + dir[1]
				unit = MAP0.getUnitByCoord(hex)
				if unit in UNIT0.unitListTank or unit in UNIT0.unitListArti:
					self.target.setStatCur("AMM", self.target.getStatCur("AMM")+addedAmmo)
					if unit.getStatCur("AMM") > unit.getStatNom("AMM"):
						self.setStatCur("AMM", self.target.getStatNom("AMM"))
					print("Added %s Ammo to %s(now %s Ammo)" % (addedAmmo, unit, unit.getStatCur("AMM")))
					
#------------------------------------------
#------------------------------------------
class Effects:
	class Effect(object):
		id = "E000"
		statName = "prototypeEffect"
		statTimer = 0
		unitAffected = None
		isABuff = False
		isNegative = False
		#HP, AR, SPD, VR, DMG, FRmin, FRmax, AMM
		statBuff = [0, 0, 0, 0, 0, 0, 0, 0]
		
		def __init__(self, unit):
			self.unitAffected = unit
		
		def tick(self):
			self.statTimer = -1
			if self.statTimer == 0:
				self.destroy()
			
		def destroy(self):
			effectArray = self.statUnitAffected.instEffects
			del effectArray[effectArray.index(self)]
			print("%s\' \"%s\" has expired." % (self.statUnitAffected.getName(), self.statName))
			
		def effect(self, data):
			print("This is a prototype effect, get out!")