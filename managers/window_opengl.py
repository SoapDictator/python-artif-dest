import sys, math, pygame, OpenGL
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from utils import util

class WindowManager(object):
    #singleton implementation
    instance = None
    
    def __init__(self):
        if not WindowManager.instance:
            WindowManager.instance = WindowManager.__WindowManager()
            
    def __getattr__(self, name):
        return getattr(self.instance, name)

    class __WindowManager():
        FPS = None
        FPSCLOCK = None
        WINDOWWIDTH = None
        WINDOWHEIGHT = None
        DISPLAYSURF = None
        BASICFONT = None
        
        #fps, windowwidth, windowheight, cellsize, mapradius
        DEFAULTSETTINGS = [60, 800, 600, 50, 20]
        
        SCROLLSPEED = 10
        
        COLORMAP = {}
        
        playerSelectedID = None
        
        def defineGlobals(self, InputManager, MapManager, UnitManager):
            global INPUT0, MAP0, UNIT0, WINDOW0
            INPUT0 = InputManager
            MAP0 = MapManager
            UNIT0 = UnitManager
            WINDOW0 = self
            
            self.playerSelectedID = UNIT0.getPlayerSelectedID()
        
        def __init__(self):
            self.screenConfig()
            self.screenColors()
            
            pygame.init()
            self.FPSCLOCK = pygame.time.Clock()
            pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT), DOUBLEBUF|OPENGL)
            pygame.display.set_caption('AD')
            
            # self.DISPLAYSURF = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT))
            self.BASICFONT = util.loadFont('freesansbold.ttf', 12)
            
            gluPerspective(45, float(self.WINDOWWIDTH)/self.WINDOWHEIGHT, 0.1, 100.0)
            glTranslatef(0.0,0.0, -30)
            
            h = float(self.CELLSIZE*0.90)
            w = math.sqrt(3)/2 * h
            self.EDGES =                [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]]
            self.PIXELPOINTS =    [[0, 0.5*h, 0], [0.5*w, 0.25*h, 0], [0.5*w, -0.25*h, 0], 
                                            [0, -0.5*h, 0], [-0.5*w, -0.25*h, 0], [-0.5*w, 0.25*h, 0]]
            self.PIXELEDGES =    [[-0.25*w, 0.375*h], [-0.5*w, 0], [-0.25*w, -0.375*h], 
                                            [0.25*w, -0.375*h], [0.5*w, 0], [0.25*w, 0.375*h]]

        #takes settings frrom config.txt
        def screenConfig(self):
            try:
                config = open("config.txt", "r")
                
                for line in config:
                    if "FPS = " in line:
                        self.FPS = float(line[6:9])
                    elif "WINDOWWIDTH = " in line:
                        self.WINDOWWIDTH = int(line[14:])
                    elif "WINDOWHEIGHT = " in line:
                        self.WINDOWHEIGHT = int(line[15:])
                    elif "CELLSIZE = " in line:
                        self.CELLSIZE = int(line[11:])
                    elif "MAPRADIUS = " in line:
                        self.MAPRADIUS = int(line[12:])
            except:
                self.FPS = self.DEFAULTSETTINGS[0]
                self.WINDOWWIDTH = self.DEFAULTSETTINGS[1]
                self.WINDOWHEIGHT = self.DEFAULTSETTINGS[2]
                self.CELLSIZE = self.DEFAULTSETTINGS[3]
                self.MAPRADIUS = self.DEFAULTSETTINGS[4]

            self.CELLWIDTH = int(self.WINDOWWIDTH / self.CELLSIZE)
            self.CELLHEIGHT = int(self.WINDOWHEIGHT / self.CELLSIZE)
            
            self.POINTCENTER = [self.WINDOWWIDTH/2, self.WINDOWHEIGHT/2]
        
        def screenColors(self):
            #                         R     G     B
            self.WHITE            = (1.00, 1.00, 1.00)
            self.BLACK            = (   0,    0,    0)
            self.LIGHTBLUE        = (0.71, 0.71, 1.00)
            self.BLUE             = (0.47, 0.47, 1.00)
            self.LIGHTRED         = (0.80, 0.36, 0.36)
            self.RED              = (0.86,    0,    0)
            self.DARKRED          = (0.47,    0,    0)
            self.GREEN            = (0.13, 0.71, 0.13)
            self.YELLOW           = (0.80, 0.80,    0)
            self.GREENYELLOW      = (0.68, 0.80, 0.18)
            self.LIGHTGRAY        = (0.59, 0.59, 0.59)
            self.DARKGREY         = (0.24, 0.24,  0.24)
            self.BGCOLOR          = self.DARKGREY
            
        def hextopixel(self, hex):
            x = self.CELLSIZE/2 * math.sqrt(3) * (hex[0] +hex[1]*0.5)
            y = self.CELLSIZE/2 * 1.5 * hex[1]
            
            return [x, y, 0]
            
        def pixeltohex(self, pixelHex):
            y = (pixelHex[1]) / (self.CELLSIZE/2 * 1.5)
            x = (pixelHex[0]) / (self.CELLSIZE/2 * math.sqrt(3)) - y*0.5
            return self.hexRound([x, y])
        
        #takes float hex coordinates and rounds it to the nearest hex
        def hexRound(self, hex):
            rx = round(hex[0])
            ry = round(-hex[0]-hex[1])    #since axial coordinates are used Y has to be calculated
            rz = round(hex[1])
            
            dx = abs(rx - hex[0])
            dy = abs(ry + hex[0] + hex[1])
            dz = abs(rz - hex[1])
            
            if dx > dy and dx > dz:
                rx = -ry-rz
            elif dy > dz:
                #ry = -rx-rz
                pass
            else:
                rz = -rx-ry
                
            return [int(rx), int(rz)]
        
        #draws a single hex; width=1 will draw an outline, width=0 draws a solid figure
        def drawHex(self, hex, color = (0.81, 0.81, 0.81), width = 1):
            pixelhex = self.hextopixel(hex)
            points = []
            
            for i in range(0, 6):
                points.append(
                    [self.PIXELPOINTS[i][0] + pixelhex[0],
                     self.PIXELPOINTS[i][1] + pixelhex[1]]
                )
                
            if width == 0:                
                glBegin(GL_POLYGON)
                glColor3fv(color)
                
                for point in points:
                    glVertex2fv(point)
                glEnd()
                
            else:
                glBegin(GL_LINE_LOOP)
                
                for point in points:
                    glVertex2fv(point)
                glEnd()
        
        #draws a direct line from origin to target
        def drawLine(self, origin, target, color = [1.00, 1.00, 1.00]):
            pixelOrigin = self.hextopixel(origin)
            pixelTarget = self.hextopixel(target)
            
            N = util.getDistance(origin, target)
            pixelN = [pixelOrigin[0]-pixelTarget[0],pixelOrigin[1]-pixelTarget[1]]
            if N != 0:    pixelDiv = [float(pixelN[0])/N, float(pixelN[1])/N]
            else:         pixelDiv = [0, 0]
            
            glBegin(GL_LINE_STRIP)
            glColor3fv(color)
            for i in range(0, N+1):
                X = pixelOrigin[0] - int(pixelDiv[0]*i)
                Y = pixelOrigin[1] - int(pixelDiv[1]*i)
                glVertex2fv(X, Y)
            glEnd()
        
        #draws all hexes or their outlines fitting on the screen using one color
        def drawGrid(self, color = [1.00, 1.00, 1.00], width = 1):
            # hexStart = self.pixeltohex([-self.CELLSIZE, -self.CELLSIZE])
            # hexStop = self.pixeltohex([self.WINDOWWIDTH+self.CELLSIZE, self.WINDOWHEIGHT+self.CELLSIZE])
            
            # for hex in MAP0.getRectangle(hexStart, hexStop):
            for hex in MAP0.MAP:
                if width == 1:
                    self.drawHex(hex, color, width)
                else:
                    self.drawHex(hex, self.COLORMAP[hex[0], hex[1]], width)
        
        def drawText(self, text, pos0, pos1, color = (1.00, 1.00, 1.00)):
            blending = False 
            if glIsEnabled(GL_BLEND):
                blending = True

            #glEnable(GL_BLEND)
            glColor3fv([1.00, 1.00, 1.00])
            glWindowPos2f(pos0,pos1)
            for ch in text:
                glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ctypes.c_int(ord(ch)))

            if not blending :
                glDisable(GL_BLEND) 
            
        def colorMapReset(self):
            for hex in MAP0.MAP:
                self.COLORMAP[hex[0], hex[1]] = self.LIGHTGRAY
        
        def colorMapInsert(self, hex, color):
            self.COLORMAP[hex[0], hex[1]] =  color
            
        def screenScrollDown(self):
            self.screenScroll(0, 1)
            
        def screenScrollUp(self):
            self.screenScroll(0, -1)
            
        def screenScrollLeft(self):
            self.screenScroll(1, 0)
            
        def screenScrollRight(self):
            self.screenScroll(-1, 0)
            
        def screenScroll(self, x, y):
            glTranslatef(x, y, 0)
            
        #draws EVERYTHING again on each frame
        def screenRefresh(self):
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            self.colorMapReset()
            unitSelected = UNIT0.getUnitSelected()
            mousePos = pygame.mouse.get_pos()
            
            #draws visible for the selected player hexes
            for hex in UNIT0.getPlayerFOV(self.playerSelectedID):
                self.colorMapInsert(hex, (200, 200, 200))
            
            #draws possible movement options and a calculated path to chosen destination
            if INPUT0.getInputState() == 'unitSelected' and unitSelected != None:
                speed = unitSelected.getStatCur("SPD")
                coord = unitSelected.getCoord()
                for hex in MAP0.getRing(speed, coord, width = 0, MO = True):
                    self.colorMapInsert(hex, self.LIGHTBLUE)
                for hex in MAP0.getPath(speed, coord, self.pixeltohex(mousePos)):
                    self.colorMapInsert(hex, self.BLUE)
            
            #draws all hexes a selected unit can attack
            if INPUT0.getInputState() == 'unitTarget':
                if unitSelected.canAttack:
                    INPUT0.setState(1)
                
                    tempMaxArea = MAP0.getRing(unitSelected.getStatCur("FRmax"), unitSelected.getCoord(), width = 0)
                    tempMinArea = MAP0.getRing(unitSelected.getStatCur("FRmin"), unitSelected.getCoord(), width = 0)
                    for hex in tempMaxArea:
                        # we don't need to draw tiles unit can't attack because of min Fire Range
                        if hex not in tempMinArea:
                            self.colorMapInsert(hex, self.LIGHTRED)
            
            #draws all MOs
            for hex in MAP0.MOARRAY:
                self.colorMapInsert(hex, self.DARKGREY)
            
            #draws units visible for the selected player
            for unit in UNIT0.getAllUnits():
                if unit.getOwnerId() == self.playerSelectedID:
                    self.colorMapInsert(unit.statCoord, self.GREENYELLOW)
                else:
                    if unit.getCreationId() in UNIT0.getPlayerVisibleUnits(self.playerSelectedID):
                        # redraws the units with a different color so they're visible during unit's attack targeting
                        if INPUT0.getInputState() == 'unitTarget':
                            self.colorMapInsert(unit.statCoord, self.RED)
                        else:
                            self.colorMapInsert(unit.statCoord, self.LIGHTRED)
            
            #simply draws a hex grid of all hexes on the map
            self.drawGrid(width = 0)
            # self.drawGrid()
            
            for unit in UNIT0.getAllUnits():
                #draws movement queues and attack targets for owned units
                if unit.getOwnerId() == self.playerSelectedID:
                    if unit.getTarget() != None:
                        if UNIT0.isTank(unit):
                            self.drawLine(unit.getCoord(), unit.getTarget().statCoord, self.RED)
                        elif UNIT0.isArti(unit):
                            self.drawLine(unit.getCoord(), unit.getTarget(), self.RED)
                    
                    path = unit.getMoveQueue()
                    for i in range(1, len(path)):
                        self.drawLine(path[i-1], path[i], self.BLUE)
                
                #draws stats of the unit, if mouse is hovered over it
                if unit.getCoord() == WINDOW0.pixeltohex(mousePos):
                    if unit.getCoord() in UNIT0.getPlayerFOV(self.playerSelectedID):
                    
                        text = "%s" % unit.getName()                        
                        i = 0
                        for key in unit.statCur.keys():
                            if unit.getStatCur(key) != None:
                                self.drawText(text, self.WHITE, mousePos[0]+10, mousePos[1]+i*12)
                                text = "%s: %s/%s" % (key, unit.getStatCur(key), unit.getStatNom(key))
                                i += 1
            
            #display FPS
            actualFps = str(int(self.FPSCLOCK.get_fps()))
            self.drawText(actualFps, 0, 0)
            
            #display controls for current input state
            i = 2
            for key in INPUT0.mapKeyUpUniversal.keys():
                text = "%s: %s" % (key, INPUT0.mapKeyUpUniversal[key])
                self.drawText(text, 10, i*12)
                i += 1
            i += 2
            for key in INPUT0.mapKeyUpDict.keys():
                text = "%s: %s" % (key, INPUT0.mapKeyUpDict[key])
                self.drawText(text, 10, i*12)
                i += 1
            
            pygame.display.flip()
            self.FPSCLOCK.tick(self.FPS)
            glutSwapBuffers()