class Food(object):
    x = y = 0
    size = 50

    def __init__(self, x, y, size=50):
        self.x = x
        self.y = y
        self.size = size

    def contains(self, x, y):
        if (x-self.x)**2 + (y-self.y)**2 < self.size**2:
            return True
        return False
