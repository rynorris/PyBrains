"""PyBrains by Ryan Norris"""

import os, sys
from artist import Artist
from creature import Creature
from food import Food
from textLog import TextLog
import brainUtils
import pygame
import random
import math
from pygame.locals import *

class Main:
    def __init__(self):
        self.textLog = TextLog()
        self.clear()
        self.limitSpeed = True
        self.draw = True
        self.drawBrains = True
        self.paused = False
        self.ARENA_WIDTH = 2000
        self.ARENA_HEIGHT = 1400
        self.DRAW_SCALE = 0.5
        self.MAX_FOOD = 50
        self.artist = Artist(self.ARENA_WIDTH, self.ARENA_HEIGHT, scale=self.DRAW_SCALE)
        self.focusedCreature = None
        self.filename = None
        self.generation = 1
        self.genTime = 1

    def clear(self):
        self.creatures = []
        self.dying = []
        self.dead = []
        self.food = []

    def randomiseCreatures(self, mother=None, father=None):
        self.creatures = []
        for i in range(10):
            if (mother==None) or (father==None):
                c = Creature(DNA=brainUtils.randBinary((5 + 6*5+3*5)*8))
            else:
                c = mother.breed(father)
            c.x = (random.random()*(self.ARENA_WIDTH-50) + 50)
            c.y = (random.random()*(self.ARENA_HEIGHT-50) + 50)
            self.creatures.append(c)

    def randomiseFood(self):
        for i in range(self.MAX_FOOD):
            self.spawnFood()

    def spawnFood(self):
        x = (random.random()*(self.ARENA_WIDTH-50) + 50)
        y = (random.random()*(self.ARENA_HEIGHT-50) + 50)
        f = Food(x,y,40)
        self.food.append(f)

    def save(self):
        f = open("save.txt",'w')
        f.write(str(self.generation)+'\n')
        for c in self.creatures:
            f.write(c.saveToString()+'\n')
        f.close()

    def load(self):
        self.creatures = []
        f = open(self.filename,'r')
        gen = f.readline()[:-1]
        self.generation = int(gen)
        for line in f:
            c = Creature(saveState=line[:-1])
            self.creatures.append(c)
        f.close()
        self.textLog.push("Loading from file at generation "+gen+".")

    def breedIfNecessaryOLD(self):
        if len(self.creatures)==0:
            best1 = self.dead[-1]
            best2 = self.dead[-2]

            self.clear()
            self.randomiseCreatures(best1,best2)
            self.randomiseFood()

            self.textLog.push("Generation "+str(self.generation)+" survived "+str(self.genTime)+" steps.")
            self.generation += 1
            self.genTime = 0
            
            self.textLog.push("Spawning generation "+str(self.generation))
            self.artist.drawBackground()
            self.artist.drawTextLog(self.textLog)

    def breedIfNecessary(self):
        if len(self.creatures) == 0:
            self.textLog.push("No creatures available to breed.")
            self.textLog.push("Species extinct.")
            self.paused = 1
        elif len(self.creatures)<=5:
            for i in range(5):
                a = random.randint(0,len(self.creatures)-1)
                b = a
                if len(self.creatures)>1:
                    while b==a:
                        b = random.randint(0,len(self.creatures)-1)
                mother = self.creatures[a]
                father = self.creatures[b]
                c = mother.breed(father)
                c.x = (random.random()*525 + 100)*self.ARENA_SCALE
                c.y = (random.random()*400 + 50)*self.ARENA_SCALE
                self.creatures.append(c)

            self.textLog.push("Generation "+str(self.generation)+" survived "+str(self.genTime)+" steps.")
            self.generation += 1
            self.genTime = 0
            
            self.textLog.push("Spawning generation "+str(self.generation))
            if not self.draw:
                self.artist.drawBackground()
                self.artist.drawTextLog(self.textLog)

            self.save()


    def main(self, filename):
        self.filename = filename
        clock = pygame.time.Clock()
        counter = 0
        self.genTime = 0
        self.textLog.push("Beginning life simulation.")
        
        try:
            self.textLog.push("Attempting to load saved state.")
            self.load()
        except:
            self.textLog.push("Saved state missing or corrupted.")
            generation = 1
            self.textLog.push("Generating random creatures.")
            self.randomiseCreatures()
        finally:
            self.randomiseFood()
            
        running = True

        while running:
            if self.limitSpeed and self.draw:
                clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        self.clear()
                        self.randomiseCreatures()
                        self.randomiseFood()
                        self.generation = 1
                        self.textLog.push("Restarting simulation from generation 1.")
                        self.textLog.push("Spawning 10 random creatures.")
                    elif event.key == K_z:
                        self.limitSpeed = not self.limitSpeed
                    elif event.key == K_x:
                        self.draw = not self.draw
                    elif event.key == K_b:
                        self.drawBrains = not self.drawBrains
                    elif event.key == K_p:
                        self.paused = not self.paused
                    elif event.key == K_s:
                        self.save()
                        self.textLog.push("Simulation state saved.")
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button==1:
                        d = 100000000
                        closest = None
                        x = event.pos[0] / self.DRAW_SCALE
                        y = event.pos[1] / self.DRAW_SCALE
                        for c in self.creatures:
                            dist = (c.x-x)**2+(c.y-y)**2
                            if dist < d:
                                d = dist
                                closest = c

                        if d < 1000:
                            self.focusedCreature = closest
                        else:
                            self.focusedCreature = None

            if not self.paused:
                for d in self.dying:
                    self.creatures.remove(d)
                    self.dead.append(d)
                    if len(self.dead)>5:
                        self.dead.pop(0)
                self.dying = []

                for f in self.food:
                    if f.size<=20:
                        self.food.remove(f)
                        self.spawnFood()

                for c in self.creatures:
                    if c.update() == 0:
                        self.dying.append(c)
                    c.x = min(self.ARENA_WIDTH-25,max(25,c.x))
                    c.y = min(self.ARENA_HEIGHT-25,max(25,c.y))

                    for f in self.food:
                        if c.canEat(f):
                            c.eat(f)
                    for a in c.antennae+c.eyes:
                        a.lookAt(self.food)

                self.genTime += 1

            counter += 1
            if self.draw and (self.limitSpeed or counter == 20):
                self.artist.drawBackground()
                    
                for f in self.food:
                    self.artist.drawFood(f)

                for d in self.dead:
                    self.artist.drawCreature(d)

                if self.focusedCreature!=None:
                    self.artist.highlight(self.focusedCreature)
                        
                for c in self.creatures:
                    self.artist.drawCreature(c)
                    if self.drawBrains:
                        self.artist.drawCreatureBrain(c)

                if self.focusedCreature!=None:
                    s = 200/self.DRAW_SCALE
                    loc = (int(-s/5), int(-s/8))
                    self.artist.drawCreatureBrain(self.focusedCreature,
                                              size=s,pos=loc)

                self.artist.drawTextLog(self.textLog)
                
                counter = 0
                    
            self.breedIfNecessary()
                        
            self.artist.paint()

        self.artist.destroy()

m = Main()
m.main("save.txt")
    
