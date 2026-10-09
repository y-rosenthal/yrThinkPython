import math
def staircase(steps, size):
    """Draw a staircase going up and to the right.

    steps: number of steps (a positive integer)
    size: height and depth of each step
    """
help(staircase)
def describe(shape, sides):
    print('A', shape, 'has', sides, 'sides')
describe('hexagon', 6); describe(sides=5, shape='pentagon')
for r in (30, 300):
    c = 2*math.pi*r; print(r, c, int(c/3), int(c/3)+10)
print(360/4.5, 360/-4)
try: describe('square', size=4)
except TypeError as e: print(e)
