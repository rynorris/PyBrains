"""PyBrains by Ryan Norris"""

import pygame
import math
from pygame.locals import *

try:
    import pygame.mixer
    pygame.mixer.pre_init(11025)
except:
    pygame.mixer = None

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

class Artist:
    def __init__(self, width=640, height=480, scale=1):
        """Init"""
        pygame.init()
        """Set Window Size"""
        self.width=width
        self.height=height
        self.scale = scale
        """Create Screen"""
        self.screen = pygame.display.set_mode((int(self.width*self.scale),int(self.height*self.scale)))
        self.canvas = pygame.Surface((width,height))

    def drawBackground(self, colour=(255,255,255)):
        pygame.draw.rect(self.canvas, colour,
                         [0,0,self.width,self.height])

    def drawBrain(self, brain, xPos, yPos, size=50, orientation = 0.0):
        s = pygame.Surface((size,size))
        s.set_colorkey((0,255,0))
        pygame.draw.rect(s,(0,255,0),[0,0,size,size])
        nodes = {}
        
        numInputs = len(brain.inputs)
        numInner = len(brain.innerNodes)
        numOutputs = len(brain.outputs)

        dy = size/(numInputs+1)
        x=5
        y = dy/2
        
        for node in brain.inputs:
            nodes[node] = (int(x),int(y))
            y += dy

        y = 0
        dy = size/(numInner+1)
        y += dy/2
        x += (size-10)/2

        for node in brain.innerNodes:
            nodes[node] = (int(x),int(y))
            y += dy

        y = 0
        dy = size/(numOutputs+1)
        y += dy/2
        x += (size-10)/2

        for node in brain.outputs:
            nodes[node] = (int(x),int(y))
            y += dy
        
        for node in nodes.keys():
            for synapse in node.outputs:
                brightness = min(int(synapse.currentCharge*155), 155)
                width = max(1,int(5*(synapse.permittivity/255.0)))
                start = nodes[node]
                end = nodes[synapse.outputs[0]]
                colour = (100,100+brightness,100+brightness)
                pygame.draw.line(s, colour, start, end, width)

        for node in nodes.keys():
            brightness = min(int(node.currentCharge*255), 255)
            pygame.draw.circle(s, (brightness,brightness,0),
                               nodes[node], 4, 0)

        s = pygame.transform.rotate(s, orientation)

        self.canvas.blit(s, (xPos, yPos))

    def drawCreatureBrain(self, creature, size=100, pos=None):
        s = pygame.Surface((size,size))
        s.set_colorkey((0,255,0))
        pygame.draw.rect(s,(0,255,0),[0,0,size,size])
        nodes = {}

        mid=size/2
        sep=size/5
        
        # nodes[creature.lAntenna] = (mid-sep, mid-sep)
        # nodes[creature.fAntenna] = (mid,sep)
        # nodes[creature.rAntenna] = (mid+sep,mid-sep)

        nodes[creature.lEye] = (mid-sep, mid-sep)
        nodes[creature.rEye] = (mid+sep, mid-sep)

        nodes[creature.pulser] = (mid,mid-sep/2)

        y = mid
        x = mid-sep
        dx = (2*sep)/(len(creature.brain.innerNodes)-1)
        for node in creature.brain.innerNodes:
            nodes[node] = (int(x),int(y))
            x += dx

        nodes[creature.lTurn] = (mid-sep, mid+sep)
        nodes[creature.fBooster] = (mid, size-sep)
        nodes[creature.rTurn] = (mid+sep, mid+sep)
        
        for node in nodes.keys():
            drawOrder = []

            for synapse in node.outputs:
                if synapse.currentCharge == 0:
                    drawOrder.insert(0, synapse)
                else:
                    drawOrder.append(synapse)
                    
            for synapse in drawOrder:
                brightness = min(int(synapse.currentCharge*155), 155)
                width = max(1,int((size/30)*(synapse.permittivity/127.0)))
                start = nodes[node]
                end = nodes[synapse.outputs[0]]
                if synapse.direction==1:
                    colour = (100,100+brightness,100+brightness)
                else:
                    colour = (100+brightness,100,100)
                pygame.draw.line(s, colour, start, end, width)

        for node in nodes.keys():
            brightness = min(int(node.currentCharge*255), 255)
            pygame.draw.circle(s, (brightness,brightness,0),
                               (int(nodes[node][0]),int(nodes[node][1])), int(size/30), 0)

        if pos==None:
            s = pygame.transform.rotate(s, math.degrees(creature.facing)-90)
            pos = (creature.x - s.get_width()/2,
                    creature.y -s.get_height()/2)
            

        self.canvas.blit(s, pos)

    def drawCreature(self, creature):
        size = 400
        s = pygame.Surface((size,size))
        s.set_colorkey((1,0,0))
        life = int(255*(creature.energy/creature.MAX_ENERGY))
        pygame.draw.rect(s,(1,0,0),(0,0,size,size))

        for eye in creature.eyes:
            for a in [eye.angle + eye.arc, eye.angle - eye.arc]:
                sin = math.sin(a+math.pi/2)
                cos = math.cos(a+math.pi/2)
                x = size/2 + eye.view_distance*cos
                y = size/2 - eye.view_distance*sin
                pygame.draw.line(s, (100,100,100),(size/2,size/2),
                                (int(x),int(y)),1)

        # l = creature.ANTENNA_LENGTH
        # t = creature.ANTENNA_ANGLE
        # for a in [t,0,-t]:
            # sin = math.sin(math.radians(a+90))
            # cos = math.cos(math.radians(a+90))
            # x = size/2 + l*cos
            # y = size/2 - l*sin
            
            # pygame.draw.line(s, (0,0,0),(size/2,size/2),
                             # (int(x),int(y)),2)
            # pygame.draw.circle(s, (200,0,0),
                               # (int(x),int(y)),5)

        tailLength = 5 + (min(1,creature.age/20000.0))*35
            
        pygame.draw.polygon(s, (0,life,0), [(size/2-25,size/2-25),
                                            (size/2+25,size/2-25),
                                            (size/2,size/2+tailLength)])
        
        s = pygame.transform.rotate(s,math.degrees(creature.facing)-90)

        self.canvas.blit(s, (creature.x - s.get_width()/2,
                             creature.y - s.get_height()/2))


    def highlight(self,creature):
        size = 400
        pygame.draw.circle(self.canvas,(200,200,0),
                           (int(creature.x),int(creature.y)),
                           int(size/10),4)
        
        FONT_SIZE = int(15/self.scale)
        FONT_COLOUR = (0,0,100)
        font = pygame.font.Font(None,FONT_SIZE)
        render = font.render(str(creature.age),True, FONT_COLOUR)
        self.canvas.blit(render,(int(creature.x)-25,int(creature.y)-50))

    def drawFood(self, food):
        pygame.draw.circle(self.canvas, (200,100,100),
                           (int(food.x),int(food.y)),int(food.size))
                           
    def highlightFood(self, food):
        pygame.draw.circle(self.canvas,(0,200,0),
                           (int(food.x),int(food.y)),
                           int(food.size+10))

    def drawTextLog(self, log):
        FONT_SIZE = int(20/self.scale)
        FONT_COLOUR = (0,0,100)
        font = pygame.font.Font(None,FONT_SIZE)

        dy = FONT_SIZE + 2
        y = self.height - dy - 5
        x = 5

        for line in log.lines:
            render = font.render(line, True, FONT_COLOUR)
            self.canvas.blit(render, (x,y))
            y -= dy

    def paint(self):
        pygame.transform.scale(self.canvas,(int(self.width*self.scale),int(self.height*self.scale)),self.screen)
        pygame.display.flip()

    def destroy(self):
        pygame.display.quit()

    
