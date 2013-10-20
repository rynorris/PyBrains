"""PyBrains by Ryan Norris"""

class Node(object):
    """The Node class is a base class for all node types.
    it contains default behaviour for charging, firing and updating."""
    
    FIRING_THRESHOLD = 1.0
    FIRING_STRENGTH = 1.0
    CHARGE_DECAY_RATE = 0.02
    currentCharge = 0
    outputs = []
    
    def __init__(self):
        self.currentCharge = 0
        self.outputs = []

    def fire(self):
        for output in self.outputs:
            output.charge(self.FIRING_STRENGTH)

    def charge(self, strength):
        self.currentCharge += strength
        while self.currentCharge >= self.FIRING_THRESHOLD:
            self.fire()
            self.currentCharge -= self.FIRING_THRESHOLD

    def update(self):
        self.currentCharge -= self.CHARGE_DECAY_RATE
        if self.currentCharge < 0:
            self.currentCharge = 0
