from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import numpy as np
import sys, math, os

EXIT = -1
FIRST = 0

rotY = 1
rotX = 1
rotZ = 1

raw_points = []
gesamtmatrix = 0
xlist = []
ylist = []
zlist = []
rotation = np.array([[np.cos(rotY * np.pi / 180), 0, np.sin(rotY * np.pi / 180), 0],
                             [0, 1, 0, 0],
                             [-np.sin(rotY * np.pi / 180), 0, np.cos(rotY * np.pi / 180), 0],
                             [0, 0, 0, 1]])

def init(width, height):
    """ Initialize an OpenGL window """
    glClearColor(1.0, 1.0, 1.0, 0.0)  # background color
    glMatrixMode(GL_PROJECTION)  # switch to projection matrix
    glLoadIdentity()  # set to 1
    glOrtho(-1.5, 1.5, -1.5, 1.5, -1.0, 1.0)  # multiply with new p-matrix
    glMatrixMode(GL_MODELVIEW)  # switch to modelview matrix


def display():
    global raw_points, gesamtmatrix
    global rotY, rotX, rotZ, rotation



    bbmittelpunkt = np.array(
        [(min(xlist) + max(xlist)) / 2, (min(ylist) + max(ylist)) / 2, (min(zlist) + max(zlist)) / 2])

    biggestpoint = np.array([max(xlist), max(ylist), max(zlist)])
    smallestpoint = np.array([min(xlist), min(ylist), min(zlist)])

    # bb_kantenlänge = Skalierungsfaktor
    bb_kantenlaenge = 2 / max(biggestpoint - smallestpoint)
    sk = 1.5 * bb_kantenlaenge

    # Skalierungsmatrix
    skalierung = np.array([[sk, 0, 0, 0],
                           [0, sk, 0, 0],
                           [0, 0, sk, 0],
                           [0, 0, 0, 1]])

    transformation = np.array(
        [[1, 0, 0, -bbmittelpunkt[0]],
         [0, 1, 0, -bbmittelpunkt[1]],
         [0, 0, 1, -bbmittelpunkt[2]],
         [0, 0, 0, 1]])



    gesamtmatrix = rotation @ skalierung
    print(gesamtmatrix)

    """ Render all objects"""
    glClear(GL_COLOR_BUFFER_BIT)  # clear screen
    glColor(0.0, 0.0, 1.0)  # render stuff

    glBegin(GL_POINTS)
    for p in raw_points:
        #p = np.append(p, 1)
        print(p)
        pp = gesamtmatrix @ p
        glVertex3f(pp[0], pp[1], pp[2])

    glEnd()

    glutSwapBuffers()  # swap buffer


def reshape(width, height):
    """ adjust projection matrix to window size"""
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if width <= height:
        glOrtho(-1.5, 1.5,
                -1.5 * height / width, 1.5 * height / width,
                -1.0, 1.0)
    else:
        glOrtho(-1.5 * width / height, 1.5 * width / height,
                -1.5, 1.5,
                -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)


def keyPressed(key, x, y):
    """ handle keypress events """
    if key == 'x':  # chr(27) = ESCAPE
        print('X')


def mouse(button, state, x, y):
    """ handle mouse events """
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        print("left mouse button pressed at ", x, y)


def mouseMotion(x, y):
    """ handle mouse motion """
    print("mouse motion at ", x, y)


def rotationY():
    global rotY, rotation
    rotY += 10

    rotationAngle = rotY * np.pi / 180
    rotation = np.array([[np.cos(rotationAngle), 0, np.sin(rotationAngle), 0],
                         [0, 1, 0, 0],
                         [-np.sin(rotationAngle), 0, np.cos(rotationAngle), 0],
                         [0, 0, 0, 1]]) @ rotation


def rotationX():
    global rotX, rotation
    rotX += 10

    rotationAngle = rotX * np.pi / 180
    rotation = np.array([[1, 0, 0, 0],
                         [0, np.cos(rotationAngle), -np.sin(rotationAngle), 0],
                         [0, np.sin(rotationAngle), np.cos(rotationAngle), 0],
                         [0, 0, 0, 1]]) @ rotation


def rotationZ():
    global rotZ, rotation
    rotZ += 10

    rotationAngle = rotZ * np.pi / 180
    rotation = np.array([[np.cos(rotationAngle), -np.sin(rotationAngle), 0, 0],
                         [np.sin(rotationAngle), np.cos(rotationAngle), 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]]) @ rotation


def menu_func(value):
    """ handle menue selection """
    print("menue entry ", value, "choosen...")
    if value == EXIT:
        sys.exit()
    if value == FIRST:
        rotationY()
    if value == 2:
        rotationX()
    if value == 3:
        rotationZ()

    glutPostRedisplay()


def main():
    # Hack for Mac OS X
    cwd = os.getcwd()
    glutInit(sys.argv)
    os.chdir(cwd)

    #Punkte einlesen
    global raw_points, xlist, ylist, zlist

    data = open('cow.raw')
    raw_points = [np.append(np.array([float(y[0]), float(y[1]), float(y[2])]), 1) for y in
                  [x.split() for x in data.readlines()]]
    #raw_points = [np.array([float(y[0]), float([y[1]]), float([y[2]])]) for y in [x.split() for x in data.readlines()]]
    xlist = [x[0] for x in raw_points]
    ylist = [x[1] for x in raw_points]
    zlist = [x[1] for x in raw_points]




    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(500, 500)
    glutCreateWindow("simple openGL/GLUT template")

    glutDisplayFunc(display)  # register display function
    glutReshapeFunc(reshape)  # register reshape function
    glutKeyboardUpFunc(keyPressed)  # register keyboard function
    glutMouseFunc(mouse)  # register mouse function
    glutMotionFunc(mouseMotion)  # register motion function
    glutCreateMenu(menu_func)  # register menue function

    glutAddMenuEntry("rotY", FIRST)  # Add a menu entry
    glutAddMenuEntry("rotX", 2)
    glutAddMenuEntry("rotZ", 3)
    glutAddMenuEntry("EXIT", EXIT)  # Add another menu entry
    glutAttachMenu(GLUT_RIGHT_BUTTON)  # Attach mouse button to menue

    init(500, 500)  # initialize OpenGL state

    glutMainLoop()  # start even processing


if __name__ == "__main__":
    main()
