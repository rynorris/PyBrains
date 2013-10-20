"""PyBrains by Ryan Norris"""

from node import Node
from brainUtils import *

class Neuron(Node):
    pass

class Synapse(Node):
    permittivity = 100
    direction = 1 #-1 for inhibitory, +1 for excitory
    
    def __init__(self, start, end, p):
        super(Synapse,self).__init__()
        start.outputs.append(self)
        self.outputs.append(end)
        self.permittivity = p
        self.direction = 1
        
    def charge(self, strength):
        self.currentCharge = strength * ((self.permittivity)/128.0)

    def update(self):
        for output in self.outputs:
            output.charge(self.currentCharge * 0.1 * self.direction)

        super(Synapse,self).update()

class Brain(object):
    inputs = []
    innerNodes = []
    outputs = []
    synapses = []

    def __init__(self, inputs, innerNo, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.innerNodes = []
        self.synapses = []
        
        for i in range(innerNo):
            neuron = Neuron()
            self.innerNodes.append(neuron)

        for inp in self.inputs:
            for inner in self.innerNodes:
                s = Synapse(inp, inner, 1.0)
                self.synapses.append(s)

        for inner in self.innerNodes:
            for out in self.outputs:
                s = Synapse(inner, out, 1.0)
                self.synapses.append(s)

    def update(self):
        for s in self.synapses:
            s.update()
        for node in self.inputs:
            node.update()
        for node in self.innerNodes:
            node.update()
        for node in self.outputs:
            node.update()

    def die(self):
        for node in self.inputs:
            node.currentCharge = 0
        for node in self.innerNodes:
            node.currentCharge = 0
        for node in self.outputs:
            node.currentCharge = 0
        for synapse in self.synapses:
            synapse.currentCharge = 0

    def getDNA(self):
        DNA = ""
        for s in self.synapses:
            if s.direction == -1:
                DNA += "1"
            else:
                DNA += "0"
            DNA += intToBin(s.permittivity,7)

        return DNA

    def loadFromDNA(self, DNA):
        for s in self.synapses:
            s.permittivity = binToInt(DNA[1:8])
            if DNA[0]=='1':
                s.direction = -1
            DNA = DNA[8:]
