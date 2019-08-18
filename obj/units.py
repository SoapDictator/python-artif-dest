import copy, sys

from utils import util

class Units:
	class Unit(object):
		uniqueId = "U000"
		statName = "unit"
		statState = "Operational"
		statCoord = [0, 0]
		statAbilities = []
		instAbilities = []
		instEffects = []
		creationId = 0
		moveQueue = []

		ownerID = None
		type = None
		
		canAttack = False
		canMove = False
		canSee = False
		
		#HP, AR, SPD, VR, DMG, FRmin, FRmax, AMM
		statNom = None
		statCur = None
		
		def castAbility(self, abilityID, data):
			if self.statState == "Operational":
				if abilityID not in self.statAbilities:
					pass
				ability = self.instAbilities[self.statAbilities.index(abilityID)]
				ability.activate(data)
				
		def uncastAbilities(self):
			for ability in self.instAbilities:
				ability.deactivate()
			
		def uncastAbility(self, abilityID):
			for ability in self.instAbilities:
				if ability.getId == abilityID:
					ability.deactivate()
		
		def effectsTick(self):
			for effect in self.instEffects:
				effect.tick()
		
		def getStatNom(self, stat):
			return self.statNom[stat]
			
		def getStatCur(self, stat):
			return self.statCur[stat]
			
		def setStatCur(self, statName, statVal):
			self.statCur[statName] = statVal
		
		def setInitialStats (self, HP, AR, SPD, VR, DMG=None, FRmin=None, FRmax=None, AMM=None):
			stat = {}
			stat["HP"] = HP
			stat["AR"] = AR
			stat["SPD"] = SPD
			stat["VR"] = VR
			stat["DMG"] = DMG
			stat["FRmin"] = FRmin
			stat["FRmax"] = FRmax
			stat["AMM"] = AMM
			self.statNom = stat
			self.statCur = copy.deepcopy(stat)
		
		def getName(self):
			return self.statName
		
		def getType(self):
			return self.type
		
		def getMoveQueue(self):
			return self.moveQueue[:]
			
		def setMoveQueue(self, queue):
			self.moveQueue = queue[:]
			
		def resetMoveQueue(self):
			del self.moveQueue[:]
			
		def getCoord(self):
			return self.statCoord[:]
			
		def setCoord(self, Q, R):
			self.statCoord = [Q, R]
		
		def getTarget(self):
			return None
			
		def setTarget(self, data):
			return False
		
		def getOwnerId(self):
			return self.ownerID
		
		def setOwnerId(self, ownerID):
			self.ownerID = ownerID
		
		def getCreationId(self):
			return self.creationId
		
		def setCreationId(self, position):
			self.creationId = position
			
		def getState(self):
			return self.statState
			
		def setState(self, state):
			self.statState = state
			
		def resetState(self):
			self.statState = "Operational"
			
		def resetActions(self):
			if self.canMove:
				self.resetMoveQueue()
			if self.canAttack:
				self.resetTarget()
			self.uncastAbilities()
			
#------------------------------------------
			
	class US000(Unit):
		uniqueId = "US000"
		statName = "Scout"
		
		canAttack = False
		canMove = True
		canSee = True
		
		def __init__(self):
			self.type = "scout"
			#HP, AR, SPD, VR, DMG, FRmin, FRmax, AMM
			self.setInitialStats(6, 2, 5, 5)

#------------------------------------------
			
	class UT000(Unit):
		uniqueId = "UT000"
		statName = "Tank"
		
		canAttack = True
		canMove = True
		canSee = True
		
		targetCoord = None
		
		def __init__(self):
			self.type = "tank"
			#HP, AR, SPD, VR, DMG, FRmin, FRmax, AMM
			self.setInitialStats(10, 2, 4, 3, 10, None, 3, 10)
		
		def setTarget(self, targetCoord):
			if self.statState == "Operational" and self.getStatCur("AMM") > 0:
				dist = util.getDistance(self.statCoord, targetCoord)
				if dist <= self.statCur["FRmax"]:
					self.targetCoord = targetCoord
			
		def resetTarget(self):
			self.targetCoord = None
			
		def getTarget(self):
			return self.targetCoord

#------------------------------------------
			
	class UA000(Unit):
		uniqueId = "UA000"
		statName = "Artillery"
		
		canAttack = True
		canMove = True
		canSee = True
		
		targetCoord = None
		
		def __init__(self):
			self.type = "artillery"
			#HP, AR, SPD, VR, DMG, FRmin, FRmax, AMM
			self.setInitialStats(8, 0, 4, 2, 11, 2, 6, 10)
		
		def setTarget(self, targetCoord):
			if self.statState == "Operational"  and self.getStatCur("AMM") > 0:
				dist = util.getDistance(self.statCoord, targetCoord)
				if dist > self.statCur["FRmin"] and dist <= self.statCur["FRmax"]:
					self.targetCoord = targetCoord
					#deletes the movement queue to prevent moving in the same turn
					self.resetMoveQueue()
		
		def resetTarget(self):
			self.targetCoord = None
			
		def getTarget(self):
			return self.targetCoord
		
		def setMoveQueue(self, queue):
			super(Units.UA000, self).setMoveQueue(queue)
			#deletes the targeted coordinate to prevent attacking in the same turn
			self.resetTarget()

#------------------------------------------
			
	class UE000(Unit):
		uniqueId = "UE000"
		statName = "Engineer"
		statAbilities = ["A001", "A002"]
		
		canAttack = False
		canMove = True
		canSee = True
		
		def __init__(self):
			self.type = "engineer"
			#HP, AR, SPD, VR, DMG, FRmin, FRmax, AMM
			self.setInitialStats(12, 3, 3, 2)