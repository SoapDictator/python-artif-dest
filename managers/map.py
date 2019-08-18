import math

class MapManager(object):
	#singleton implementation
	instance = None
	
	def __init__(self):
		if not MapManager.instance:
			MapManager.instance = MapManager.__MapManager()
			
	def __getattr__(self, name):
		return getattr(self.instance, name)
	
	class __MapManager():
		MAP = []
		NEIGHBOURS = {}
		MOARRAY = []
		VOARRAY = []
		
		def defineGlobals(self, DrawingManager, UnitManager):
			global WINDOW0, UNIT0
			WINDOW0 = DrawingManager
			UNIT0 = UnitManager
			
			self.createMap()
		
		def __init__(self):
			#this is currently the only way to add Movement Obsticles
			self.MOARRAY = []
		
		#generates a graph of all possible transitions from one tile to another and saves all the existing coordinates
		def createMap(self):
			self.DIRECTIONS = 	[[-1, 0], [-1, +1], [0, +1],
											[+1, 0], [+1, -1], [0, -1]]
		
			for Q in range(-WINDOW0.MAPRADIUS, WINDOW0.MAPRADIUS+1):
				for R in range(-WINDOW0.MAPRADIUS, WINDOW0.MAPRADIUS+1):
					if self.getDistance([Q, R], [0, 0]) > WINDOW0.MAPRADIUS:
						continue
					self.MAP.append([Q, R])
					self.NEIGHBOURS[Q, R] = []
					for hex in self.DIRECTIONS:
						newHex = [Q+hex[0], R+hex[1]]
						if self.getDistance(newHex, [0, 0]) <= WINDOW0.MAPRADIUS:
							self.NEIGHBOURS[Q, R].append([newHex[0], newHex[1]])
		
		def getDistance(self, origin, target):
			#true distance
			#return math.sqrt(math.pow(abs(target[0]-origin[0]), 2) + math.pow(abs(target[1]-origin[1]), 2))
			
			#calculates how many non-diagonal steps it will take to get from origin to target
			#return abs(target[0]-origin[0]) + abs(target[1]-origin[1])
			
			#calculates distance in axial hex coordinates
			aq = origin[0]
			ar = origin[1]
			bq = target[0]
			br = target[1]
			return (abs(aq-bq) + abs(aq+ar-bq-br) + abs(ar-br))/2
		
		#returns all hexes on the line between the 2 points
		def getLine(self, origin, target):
			N = self.getDistance(origin, target)
			if N != 0:	div = 1/float(N)
			else:		div = 0
			result = []
			
			#if your target is outside the map the line will go to the closest to your target hex
			for i in range(0, N+1):
				Q =  float(origin[0]) + float(target[0] - origin[0]) * div * i
				R = float(origin[1]) + float(target[1] - origin[1]) * div * i
				
				hex = WINDOW0.hexRound([Q, R])
				if hex not in self.MAP:
					continue
				result.append(hex)
			return result
		
		#returns a hexes in a ring of a given radius; width=0 returns the entire circle
		def getRing(self, limit, coord = [0, 0], width = 1, MO = False):
			if limit == 0:
				return [coord]
			
			frontier = [[coord[0], coord[1]]]
			current = frontier[0]
			visited = {}
			visited[coord[0], coord[1]] = 0
			
			while True:
				for next in self.NEIGHBOURS[current[0], current[1]]:
					if not visited.has_key((next[0], next[1])) and not (next in self.MOARRAY and MO):
						frontier.append(next)
						visited[next[0], next[1]] = visited[current[0], current[1]] + 1
				del frontier[0]
				current = frontier[0]
				if visited[current[0], current[1]] == limit or len(frontier) == 0:
					break
				
			if width == 1:
				return frontier
			elif width == 0:
				area = []
				for hex in visited:
					area.append(list(hex))
				return area
		
		#returns a rectangle of hexes
		def getRectangle(self, hexStart, hexStop):
			rectangle = []
			
			offset1 = hexStart[1] - hexStop[1] 
			for q in range(hexStart[0], hexStop[0]-offset1-1):
				offset2 = 0;
				temp = 0
				for r in range(hexStart[1], hexStop[1]+1):
					if self.getDistance([q+offset2, r], [0, 0]) <= WINDOW0.MAPRADIUS:
						rectangle.append([q+offset2, r])

					temp -= 0.5
					offset2 = int(math.floor(temp))
					
			return rectangle
		
		#returns a unit in a given coordiante if it's there, otherwise returns None
		def getUnitByCoord(self, coord):
			matchedUnits = []
			for unit in UNIT0.getAllUnits():
				if [unit.statCoord[0], unit.statCoord[1]] == [coord[0], coord[1]]:
					matchedUnits.append(unit)
			
			if len(matchedUnits) == 0:
				return None
			return matchedUnits
		
		def getPath(self, limit, origin, target):
			frontier = [[origin[0], origin[1]]]
			current = frontier[0]
			came_from = {}
			came_from[origin[0], origin[1]] = [[None], 0]
			
			while True:
				for next in self.NEIGHBOURS[current[0], current[1]]:
					if not came_from.has_key((next[0], next[1])) and next not in self.MOARRAY:
						frontier.append(next)
						depth = came_from[current[0], current[1]][1] + 1
						came_from[next[0], next[1]] = [[current[0], current[1]], depth]
				del frontier[0]
				current = frontier[0]
				depth = came_from[current[0], current[1]][1]
				if depth >= limit or len(frontier) == 0 or current == target:
					break

			#if your target is outside the limit pathfinder will rather make a path to the closest to your target hex
			if not came_from.has_key((target[0], target[1])):
				line = self.getLine(origin, target)
				for hex in line[::-1]:
					if came_from.has_key((hex[0], hex[1])):
						target = hex
						break
			
			current = target
			path = [current]
			while current != origin:
				current = came_from[current[0], current[1]][0]
				path.append(current)
			return path
		
		def getVisibility(self, limit, coord):
			isVisible = [[coord[0], coord[1]]]
			MOedges = []
			pixelOrigin = WINDOW0.hextopixel(coord)
			
			for hex in self.MOARRAY:
				pixelhex = WINDOW0.hextopixel(hex)
				for edge in WINDOW0.PIXELEDGES:
					Q = int(pixelhex[0] + edge[0])
					R = int(pixelhex[1] + edge[1])
					MOedges.append([Q, R])
			
			for k in range(0, limit+1): #for whatever reason getRing with width=0 does not work with this algoritm
				for target in self.getRing(k, coord, 1):
					breakFlag = 0
					pixelTarget = WINDOW0.hextopixel(target)
					
					N = self.getDistance(coord, target)*2
					pixelN = [pixelOrigin[0]-pixelTarget[0], pixelOrigin[1]-pixelTarget[1]]
					if N != 0:	
						pixelDiv = [float(pixelN[0])/N, float(pixelN[1])/N]
					else:		
						break
				
					for i in range(2, N+1):	#ignore the first value, it always will be the unit's coordinates
						flag = False
						Q = int(pixelOrigin[0] - pixelDiv[0]*i)
						R = int(pixelOrigin[1] - pixelDiv[1]*i)
						
						for edge in MOedges:
							if (Q-2 <= edge[0] and Q+2 >= edge[0]) and (R-2 <= edge[1] and R+2 >= edge[1]):
								flag = True
								break
						#just making sure; sometimes on big distanced the method above is buggy as hell
						if WINDOW0.pixeltohex([Q, R]) in self.MOARRAY:
							flag = True
						
						if flag: 
							break
						breakFlag += 1
					
					if breakFlag == N-1:
						isVisible.append([target[0], target[1]])
			
			return isVisible