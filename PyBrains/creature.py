"""PyBrains by Ryan Norris"""
from node import Node
from brain import Brain
import brainUtils
import math
import random

SPEED_DECAY = 0.05
ANGULAR_SPEED_DECAY = 0.005

class Antenna(Node):
    x = y = 0.0 #absolute
    radius = 10
    mCreature = None

    def __init__(self, creature, x, y):
        super(Antenna,self).__init__()
        mCreature = creature
        self.x = x
        self.y = y

    def checkFood(self, food):
        if food.contains(self.x,self.y):
            self.charge(0.2)

class Eye(Node):
    MAX_CHARGE = 0.2

    def __init__(self, creature, angle, arc=30, distance=100):
        super(Eye,self).__init__()
        self.mCreature = creature
        self.angle = math.radians(angle)
        self.arc = math.radians(arc)
        self.view_distance = distance
    
    def lookAt(self, foods):
        maxChargeAmount = 0
        for f in foods:
            c = self.checkFood(f)
            if c > maxChargeAmount:
                maxChargeAmount = c
        self.charge(maxChargeAmount)
    
    def checkFood(self, food):
        chargeAmount = 0
        
        dx = food.x - self.mCreature.x
        dy = food.y - self.mCreature.y
        dist = math.sqrt(dx*dx + dy*dy)
        actual_dist = max(dist, dist-food.size)
         
        if actual_dist < self.view_distance:
            food_angle = math.atan2(dy,dx)
            rel_angle = food_angle + self.mCreature.facing
            extra_angle = math.atan2(float(food.size), dist)
            if abs(rel_angle - self.angle) < self.arc + extra_angle:
                chargeAmount = self.MAX_CHARGE * (self.view_distance - actual_dist)/self.view_distance

        return chargeAmount        

class Pulser(Node):
    chargeSpeed = 0.04

    def __init__(self):
        super(Pulser,self).__init__()
        self.chargeSpeed = 0.04

    def update(self):
        self.charge(self.chargeSpeed)

class Booster(Node):
    force = 3.0
    mCreature = None

    def __init__(self, creature, force=1.0):
        super(Booster,self).__init__()
        self.mCreature = creature
        self.force = force

    def fire(self):
        self.mCreature.velocity = self.force

class AngularBooster(Booster):
    def fire(self):
        self.mCreature.angularVelocity += self.force
        if self.mCreature.angularVelocity > 0.2:
            self.mCreature.angularVelocity = 0.2
        elif self.mCreature.angularVelocity < -0.2:
            self.mCreature.angularVelocity = -0.2
            
class Creature(object):
    x = y = 0.0
    facing = 0.0 #In radians, 0 is facing east
    velocity = 0.0
    angularVelocity = 0.0 #positive is turning anticlockwise
    brain = None
    mouthPos = (0,0)
    age = 0
    EAT_RATE = 1
    MAX_ENERGY = 200
    energy = MAX_ENERGY
    ENERGY_USE_RATE = 0.07
    MAX_BOOST_FORCE = 5.0
    MAX_TURN_FORCE = 0.1
    MAX_ANTENNA_ANGLE = 90.0
    MAX_ANTENNA_LENGTH = 200

    ANTENNA_ANGLE = 40 #Degrees
    ANTENNA_LENGTH = 60

    def __init__(self, DNA=None, saveState=None):
        self.x = self.y = 0.0
        self.facing = 0.0 #In radians, 0 is facing east
        self.velocity = 0.0
        self.angularVelocity = 0.0 #positive is turning anticlockwise
        self.mouthPos = (0,0)
        self.energy = self.MAX_ENERGY

        self.pulser = Pulser()
        
        self.fAntenna = Antenna(self,0,10)
        self.lAntenna = Antenna(self,-5,7)
        self.rAntenna = Antenna(self,5,7)
        self.antennae = []
        
        self.lEye = Eye(self,10,20,500)
        self.rEye = Eye(self,-10,20,500)
        self.eyes = [self.lEye, self.rEye]

        self.fBooster = Booster(self)
        self.lTurn = AngularBooster(self, 0.05)
        self.rTurn = AngularBooster(self, -0.05)

        self.brain = Brain([self.pulser]+self.antennae+self.eyes,
                           5,
                           [self.lTurn, self.fBooster, self.rTurn])

        if saveState!=None:
            self.loadFromString(saveState)
        elif DNA!=None:
            self.loadFromDNA(DNA)

    def update(self):
        self.age += 1
        self.energy -= self.ENERGY_USE_RATE
        if self.energy < 0:
            self.energy = 0
            self.die()
            return 0
        
        self.brain.update()
        self.brain.update()
        
        cos = math.cos(self.facing)
        sin = math.sin(self.facing)

        dx = self.velocity * cos
        dy = - self.velocity * sin

        self.x += dx
        self.y += dy

        self.facing += self.angularVelocity
        if self.facing > math.pi:
            self.facing -= math.pi*2
        elif self.facing < -math.pi:
            self.facing += math.pi*2
        
        self.mouthPos = (self.x + 20*cos, self.y - 20*sin)

        l = self.ANTENNA_LENGTH
        a = math.radians(self.ANTENNA_ANGLE)
        
        self.fAntenna.x = self.x + l*cos
        self.fAntenna.y = self.y - l*sin

        cos2 = math.cos(self.facing+a)
        sin2 = math.sin(self.facing+a)
        self.lAntenna.x = self.x + l*cos2
        self.lAntenna.y = self.y - l*sin2

        cos2 = math.cos(self.facing-a)
        sin2 = math.sin(self.facing-a)
        self.rAntenna.x = self.x + l*cos2
        self.rAntenna.y = self.y - l*sin2

        self.velocity -= SPEED_DECAY
        if self.velocity < 0:
            self.velocity = 0

        if self.angularVelocity < 0:
            self.angularVelocity = min(0,
                            self.angularVelocity + ANGULAR_SPEED_DECAY)
        elif self.angularVelocity > 0:
            self.angularVelocity = max(0,
                            self.angularVelocity - ANGULAR_SPEED_DECAY)

        return 1

    def canEat(self, food):
        if food.contains(self.mouthPos[0],self.mouthPos[1]):
            return True
        return False

    def eat(self, food):
        if food.size < self.EAT_RATE:
            self.energy += food.size
            food.size = 0
        else:
            food.size -= self.EAT_RATE
            self.energy += self.EAT_RATE

        if self.energy > self.MAX_ENERGY:
            self.energy = self.MAX_ENERGY

    def die(self):
        self.brain.die()

    def getDNA(self):
        DNA = ""

        a = (self.fBooster.force/self.MAX_BOOST_FORCE) * 255
        DNA += brainUtils.intToBin(int(a),8)

        a = (self.lTurn.force/self.MAX_TURN_FORCE) * 255
        DNA += brainUtils.intToBin(int(a),8)
        
        a = (self.ANTENNA_ANGLE/self.MAX_ANTENNA_ANGLE) * 255
        DNA += brainUtils.intToBin(int(a),8)

        a = (self.ANTENNA_LENGTH/self.MAX_ANTENNA_LENGTH) * 255
        DNA += brainUtils.intToBin(int(a),8)

        a = (self.fANTENNA_LENGTH/self.MAX_ANTENNA_LENGTH) * 255
        DNA += brainUtils.intToBin(int(a),8)
        
        DNA += self.brain.getDNA()

        return DNA

    def loadFromDNA(self, DNA):
        self.fBooster.force = self.MAX_BOOST_FORCE * (brainUtils.binToInt(DNA[:8])/255.0)
        self.fBooster.force = 3.0
        DNA = DNA[8:]
        
        turnSpeed = self.MAX_TURN_FORCE * (brainUtils.binToInt(DNA[:8])/255.0)
        turnSpeed = 0.05
        self.lTurn.force = turnSpeed
        self.rTurn.force = -turnSpeed
        DNA = DNA[8:]
        
        self.ANTENNA_ANGLE = self.MAX_ANTENNA_ANGLE * (brainUtils.binToInt(DNA[:8])/255.0)
        self.ANTENNA_ANGLE = 40
        DNA = DNA[8:]
        
        self.ANTENNA_LENGTH = self.MAX_ANTENNA_LENGTH * (brainUtils.binToInt(DNA[:8])/255.0)
        self.ANTENNA_LENGTH = 80
        DNA = DNA[8:]
        
        self.fANTENNA_LENGTH = self.MAX_ANTENNA_LENGTH * (brainUtils.binToInt(DNA[:8])/255.0)
        self.fANTENNA_LENGTH = 80
        DNA = DNA[8:]
        
        self.brain.loadFromDNA(DNA)

    def saveToString(self):
        save = ""
        save += str(self.age)+" "
        save += str(self.energy)+" "
        save += str(int(self.x))+" "
        save += str(int(self.y))+" "
        save += str(self.facing)+" "

        save += self.getDNA()

        return save

    def loadFromString(self, save):
        vals = save.split()
        self.age = int(vals[0])
        self.energy = float(vals[1])
        self.x = float(vals[2])
        self.y = float(vals[3])
        self.facing = float(vals[4])

        self.loadFromDNA(vals[5])

    def breed(self, other):
        MUTATION_RATE = 0.01
        
        DNA1 = self.getDNA()
        DNA2 = other.getDNA()

        #choose bytes at random from each parent
        DNA = ""
        i = 0
        while i<=len(DNA1):
            if random.random() > 0.5:
                DNA += DNA1[i:i+8]
            else:
                DNA += DNA2[i:i+8]
            i += 8


        bits = []
        for c in DNA:
            bits.append(int(c))
        #mutate
        for i in range(len(bits)):
            if random.random() < MUTATION_RATE:
                bits[i] = bits[i] ^ 1

        DNA = ""
        for bit in bits:
            DNA += str(bit)

        i=0
        while i<=len(DNA):
            #print DNA1[i:i+8], DNA2[i:i+8], DNA[i:i+8]
            i += 8

        return Creature(DNA=DNA)
        
