import math

def replaceZeros(line):
    return line.replace("0.000000","0")

def isZero(value):
    isZero = math.isclose(0, value, abs_tol=0.000000001)
    return isZero