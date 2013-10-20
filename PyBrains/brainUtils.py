"""PyBrains by Ryan Norris"""
from random import random

def binToInt(b):
    i = 0
    n = 2**(len(b)-1)
    for c in b:
        if c == "1":
            i += n
        n /= 2
        
    return i

def intToBin(i, digits=0):
    b = ""

    while i!=0:
        if i%2 == 1:
            b = "1" + b
            i -= 1
        else:
            b = "0" + b
        i /= 2

    if (digits!=0) & (len(b)<digits):
        b = ("0"*(digits-len(b))) + b
    return b

def randBinary(l):
    s = ""
    for i in range(l):
        if random() > 0.5:
            s += "0"
        else:
            s += "1"

    return s
