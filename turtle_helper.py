import turtle

s = turtle.getscreen()

t = turtle.Turtle() # starts at right:


size = t.turtlesize()
increase = (2 * num for num in size)
t.turtlesize(*increase)

t.pensize(5)
t.shapesize()
t.pencolor("green")

def go_right():
    # target = 0
    current = t.heading()
    if current == 0:
        pass
    elif current == 90:
        t.right(90)
    elif current == 180:
        t.right(180)
    elif current == 270:
        t.left(90)
    else:
        raise ValueError('not a right angle!')

def go_up():
    # target = 90
    current = t.heading()
    if current == 0:
        t.left(90)
    elif current == 90:
        pass
    elif current == 180:
        t.right(90)
    elif current == 270:
        t.left(180)
    else:
        raise ValueError('not a right angle!')
    
def go_left():
    # target = 180
    current = t.heading()
    if current == 0:
        t.left(180)
    elif current == 90:
        t.left(90)
    elif current == 180:
        pass
    elif current == 270:
        t.right(90)
    else:
        raise ValueError('not a right angle!')
    
def go_down():
    # target = 270
    current = t.heading()
    if current == 0:
        t.right(90)
    elif current == 90:
        t.right(180)
    elif current == 180:
        t.left(90)
    elif current == 270:
        pass
    else:
        raise ValueError('not a right angle!')


def move_turtle(command):
    if command == 'Up':
        go_up()
    elif command == 'Down':
        go_down()
    elif command == 'Left':
        go_left()
    elif command == 'Right':
        go_right()
    elif command in  ['Go','go', "Let ' s Go","Let ' s"]:
        t.forward(80)
    elif command == 'stop':
        print('Stopping the turtle')
