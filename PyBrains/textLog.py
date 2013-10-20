class TextLog:
    lines = []
    MAX_LINES = 5

    def __init__(self):
        self.lines = []

    def push(self, line):
        if len(self.lines) < self.MAX_LINES:
            self.lines.append(None)
        for i in range(len(self.lines)-1):
            self.lines[-(i+1)] = self.lines[-(i+2)]
        self.lines[0] = line

    def reset(self):
        self.lines = []
