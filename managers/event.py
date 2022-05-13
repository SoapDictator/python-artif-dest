from managers import unit
import time

global AVAILIBLEEVENTS
#dictionary entry format - (event name: priority)
AVAILIBLEEVENTS = {
	"EventUnitCreate": 0,
	"EventUnitAttack": 1,
	"EventUnitAbilityCast": 2,
	"EventUnitHPCheck": 4,
	"EventUnitDestroy": 5,
	"EventUnitMove": 6,
	"EventEffectTick": 9}

class GameEventManager(object):
	#singleton implementation
	instance = None
	
	def __init__(self):
		if not GameEventManager.instance:
			GameEventManager.instance = GameEventManager.__GameEventManager()
			
	def __getattr__(self, name):
		return getattr(self.instance, name)
	
	class __GameEventManager():
		turnCounter = 0
		eventQueue = []
		eventLastest = None
		priorityMod = 0
		fileLog = None
		
		def __init__(self):
			existingText = ""
			
			try:
				self.fileLog = open("event_log.txt", "r")
				existingText = self.fileLog.read()
				self.fileLog.close()
			except:
				pass
			
			self.fileLog = open("event_log.txt", "w")
			self.fileLog.write(existingText+"\n")
			string = "=====================\n"+time.ctime()+"\n=====================\n"
			self.fileLog.write(string)
		
		def defineGlobals(self, EventManager, MapManager, UnitManager):
			global EVENT0, MAP0, UNIT0
			EVENT0 = EventManager
			MAP0 = MapManager
			UNIT0 = UnitManager
		
		def eventAdd(self, eventName, data = None, priorityModSecondary = None):	#TODO: event sorting mechanism
			if eventName not in AVAILIBLEEVENTS:
				pass
			
			targetEvent = getattr(Events, eventName)
			event = targetEvent(data)
			try:
				priority = AVAILIBLEEVENTS[eventName] + priorityModSecondary
			except:
				priority = AVAILIBLEEVENTS[eventName] + self.priorityMod
			
			#checking that the event was properly created
			assert(event != None, "(Event object factory) Failed to create the event!")
			
			if len(self.eventQueue) > 1:
				if self.eventQueue[0][1] > priority:
					self.eventQueue.insert(0, [event, priority])
				elif self.eventQueue[len(self.eventQueue)-1][1] < priority:
					self.eventQueue.append([event, priority])
				else:
					for i in range(1, len(self.eventQueue)):
						if self.eventQueue[i-1][1] <= priority and self.eventQueue[i][1] >= priority:
							self.eventQueue.insert(i, [event, priority])
							break
			else:
				if len(self.eventQueue) == 1 and self.eventQueue[0][1] > priority:
					self.eventQueue.insert(0, [event, priority])
				else:
					self.eventQueue.append([event, priority])
			self.eventLastest = event
		
		def eventUndo(self):
			if self.eventLastest != None:
				for i in range(0, len(self.eventQueue)):
					if self.eventLastest == self.eventQueue[i][0]:
						#print("Undid %s" % self.eventQueue[i][0])
						del self.eventQueue[i]
						self.eventLastest = None
		
		def eventHandle(self):
			UNIT0.resetPlayerFOV()
			
			self.priorityMod = 0
			for i in range (0, 3):
				self.eventAdd("EventUnitHPCheck", self.priorityMod)
				self.eventAdd("EventUnitAbilityCast", self.priorityMod)
				if i == 0:	#preturn
					pass
				
				if i == 1:	#first half
					for UNIT in UNIT0.getTanks():
						if UNIT.getTarget() != None:
							EVENT0.eventAdd("EventUnitAttack", UNIT)
							
					self.eventAdd("EventUnitMove", UNIT0.getScouts())
			
				if i == 2:	#second half
					for UNIT in UNIT0.getArties():
						if UNIT.getTarget() != None:
							EVENT0.eventAdd("EventUnitAttack", UNIT)
					
					#have to call it 3 times, otherwise destroyed units will try to move and cause a bug
					self.eventAdd("EventUnitMove", UNIT0.getEngies())
					self.eventAdd("EventUnitMove", UNIT0.getArties())
					self.eventAdd("EventUnitMove", UNIT0.getTanks())
												
				if i == 3:	#postturn
					self.eventAdd("EventEffectTick", None)
					
				self.priorityMod += 10
			
			for event in self.eventQueue:
				self.fileLog.write("%d: %s (" % (event[1], event[0].getName()))
				self.fileLog.write(str(event[0].getData()))
				self.fileLog.write(")\n")
				
				event[0].execute()
			self.eventQueueReset()
			
			UNIT0.calcPlayerFOV()
			#print("============")
			self.turnCounter += 1
			#print("==Turn %s==" % self.turnCounter)
			self.fileLog.write("==Turn %s==\n" % self.turnCounter)
			
		def eventQueueReset(self):
			del self.eventQueue[:]
			
		def getTurnCounter(self):
			return self.turnCounter

#------------------------------------------

class Events:
	class GameEvent(object):
		statName = "prototypeEvent"
		
		def __init__(self, data):
			self.data = data

		def execute(self):
			print("This is a prototype event, get out!")
			
		#------------------
		def getData(self):
			return self.data
			
		def getName(self):
			return self.statName

	class EventUnitCreate(GameEvent):
		statName = "Unit Create"
		#takes a unit type (as a string) and [coordinates] as data
		def execute(self):
			UNIT0.unitCreate(self.data[0], self.data[1], self.data[2])
			#print("A new %s appeared!" %self.data[0])

	class EventUnitDestroy(GameEvent):
		statName = "Unit Destroy"
		
		#takes a unit queued for destruction as data
		def execute(self):
			UNIT0.unitDestroy(self.data)
			#print("Unit lost.")

	class EventUnitHPCheck(GameEvent):
		statName = "Units' HP Check"
		
		#takes priority modifier as data (if we don't set the priority manualy, it will add the event after the turn is resolved... 3 times in a row)
		def execute(self):
			priorityModSecondary = self.data
			for Unit in UNIT0.getAllUnits():
				if Unit.statCur["HP"] <= 0:
					EVENT0.eventAdd("EventUnitDestroy", Unit, self.data)
					
				if Unit.statCur["HP"] > Unit.statNom["HP"]:
					Unit.statCur["HP"] = Unit.statNom["HP"]
			##print("HP checked.")

	class EventUnitMove(GameEvent):
		statName = "Units Move"
		
		#takes a unit array as data
		def execute(self):
			if len(self.data) != 0:
				UNIT0.unitMoveStart(self.data)
				##print("Moved units.")

	class EventUnitAttack(GameEvent):
		statName = "Unit Attacks"
		
		#takes an attacking unit as data
		def execute(self):
			attacker = self.data
			targets = MAP0.getUnitByCoord(attacker.getTarget())
				
			if targets == None:
				if UNIT0.isArti(attacker):
					attacker.statCur["AMM"] -= 1
					attacker.resetTarget()
				return
				
			for target in targets:
				#tanks can target, but can't damage friendly units
				if UNIT0.isTank(attacker):
					if target.getOwnerId() == attacker.getOwnerId():
						continue
				target.statCur["HP"] -= self.data.statCur["DMG"] - target.statCur["AR"]
				
			attacker.statCur["AMM"] -= 1
			attacker.resetTarget()
				
			#print("A unit is (probably) under attack!")
			
	class EventUnitAbilityCast(GameEvent):
		statName = "Units Cast Abilities"
		
		#takes the prority modifier as data
		def execute(self):
			for unit in UNIT0.getAllUnits():
				if len(unit.instAbilities) > 0:
					for ability in unit.instAbilities:
						if ability.isActivated:
							if ability.priority == self.data:
								ability.execute()
								
	class EventEffectTick(GameEvent):
		statName = "Effects' Timers Tick"
		
		#takes no arguments
		def execute(self):
			for unit in UNIT0.getAllUnits():
				unit.effectsTick()