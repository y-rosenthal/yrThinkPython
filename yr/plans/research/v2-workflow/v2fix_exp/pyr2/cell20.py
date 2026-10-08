# @title Output
def branch(length):
    if length > 10:
        forward(length)
        left(30)
        branch(length * 0.6)
        right(60)
        branch(length * 0.6)
        left(30)
        forward(-length)

make_turtle(delay=0, height=220)
left(90)            # face up
penup()
forward(-100)       # move down without drawing
pendown()
branch(70)
