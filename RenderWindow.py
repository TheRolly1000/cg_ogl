
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
import numpy as np

startP = np.array([0.0, 0.0, 0.0])
actOri = 1
angle = 0
axis = np.array([0.0, 0.0, 0.0])

translateX = 0.0
translateY = 0.0

colortoggle = False
objectcolor = np.array([.0, .90, .80])

perspectiveswitch = False

shadow = False

class Scene:
    # initialization
    def __init__(self, width, height, window):
        # time
        self.t = 0
        self.window = window
        self.showVector = False
        self.point = np.array([0, 0])
        self.vector = np.array([10, 10])
        self.pointsize = 3
        self.width = width
        self.height = height

        self.xlight = 0.0
        self.ylight = 10.0
        self.zlight = -0.2

        self.rotY = 0
        self.p_light = np.array([1.0, 0, 0, 0, 0, 1.0, 0, -1.0/self.ylight, 0, 0, 1.0, 0, 0, 0, 0, 0], 'f')

        glPointSize(self.pointsize)
        glLineWidth(self.pointsize)

        # loading obj-data
        data = open("elephant.obj")

        self.vertices = []
        self.faces = []
        self.normals = []
        self.facevertarray = []

        xlist = []
        ylist = []
        zlist = []

        for line in data.readlines():
            split = line.split()

            # bei f split nach slash und schauen ob das mittlere element leer ist
            # f v/vt/vn v/vt/vn v/vt/vn

            if len(split) > 0:
                # bei kuh muessen selbst normalen berechnet werden fuer beleuchtung
                if split[0] == "v":
                    xlist.append(float(split[1]))
                    ylist.append(float(split[2]))
                    zlist.append(float(split[3]))
                    self.vertices.append(np.array([float(split[1]), float(split[2]), float(split[3])], dtype='float32'))
                elif split[0] == "f": # enthaelt indizes von vertexliste (im Fall 1.)
                    if split[1].__contains__("//"):
                        splitx = split[1].split("//")
                        splity = split[2].split("//")
                        splitz = split[3].split("//")
                        self.faces.append([int(splitx[0]), int(splity[0]), int(splitz[0])])
                        self.facevertarray.extend((self.vertices[int(splitx[0])-1], self.vertices[int(splitx[1])-1],
                                                   self.vertices[int(splity[0])-1], self.vertices[int(splity[1])-1],
                                                  self.vertices[int(splitz[0]) - 1], self.vertices[int(splitz[1]) - 1]))

                    else:
                        self.faces.append([int(split[1]), int(split[2]), int(split[3])])
                elif split[0] == "vn": # vertex-normalen
                    self.normals.append(np.array([float(split[1]), float(split[2]), float(split[3])], dtype='float32'))


        # array der normalen muss genauso lang sein wie vertices!!
        if len(self.normals) == 0:
            self.normals = [0 for x in self.vertices] # init mit nullen

            for f in self.faces: #berechne normalen jedes faces
                normal = np.cross((self.vertices[f[2]-1] - self.vertices[f[0]-1]), (self.vertices[f[2]-1] - self.vertices[f[1]-1]))
                self.normals[f[0]-1] += normal
                self.normals[f[1]-1] += normal
                self.normals[f[2]-1] += normal


        # Make an 1-D Array for VBO
        if len(self.facevertarray) == 0:
            for f in self.faces:
                self.facevertarray.append(self.vertices[f[0]-1])
                self.facevertarray.append(self.normals[f[0]-1])
                self.facevertarray.append(self.vertices[f[1]-1])
                self.facevertarray.append(self.normals[f[1]-1])
                self.facevertarray.append(self.vertices[f[2]-1])
                self.facevertarray.append(self.normals[f[2]-1])

        self.objectvbo = vbo.VBO(np.array(self.facevertarray, 'f'))

        # bounding box
        self.bb_center = np.array(
            [(min(xlist) + max(xlist)) / 2, (min(ylist) + max(ylist)) / 2, (min(zlist) + max(zlist)) / 2], 'f')

        self.biggestpoint = np.array([max(xlist), max(ylist), max(zlist)])
        self.smallestpoint = np.array([min(xlist), min(ylist), min(zlist)])

        bb_kantenlaenge = 2 / max(self.biggestpoint - self.smallestpoint)
        self.scale_factor = bb_kantenlaenge

    # step
    def step(self):
        # move point
        self.point = self.point + 0.1 * self.vector

        # check borders
        if self.point[0] < -self.width / 2:  # point hits left border
            # mirror at n = [1,0]
            n = np.array([1, 0])
            self.vector = self.mirror(self.vector, n)
        elif self.point[0] > self.width / 2:  # point hits right border
            # mirrot at n = [-1,0]
            n = np.array([-1, 0])
            self.vector = self.mirror(self.vector, n)
        elif self.point[1] < -self.height / 2:  # point hits upper border
            # mirrot at n = [0,1]
            n = np.array([0, 1])
            self.vector = self.mirror(self.vector, n)
        elif self.point[1] > self.height / 2:  # point hits lower border
            # mirrot at n = [0,-1]
            n = np.array([0, -1])
            self.vector = self.mirror(self.vector, n)

        # print(self.point, self.vector)

    # mirror a vector v at plane with normal n
    def mirror(self, v, n):
        # normalize n
        normN = n / np.linalg.norm(n)
        # project negative v on n
        l = np.dot(-v, n)
        # mirror v
        mv = v + 2 * l * n
        return mv

    def rotate(self, angle, axis):
        c, mc = np.cos(angle), 1-np.cos(angle)
        s = np.sin(angle)
        l = np.sqrt(np.dot(np.array(axis), np.array(axis)))

        if l == 0:
            return np.identity(4)

        x, y, z = np.array(axis) / l
        r = np.matrix([[x*x*mc+c, x*y*mc-z*s, x*z*mc+y*s, 0],
                        [x*y*mc+z*s, y*y*mc+c, y*z*mc-x*s, 0],
                        [x*z*mc-y*s, y*z*mc+x*s, z*z*mc+c, 0],
                        [0, 0, 0, 1]])

        return r.transpose()


    # render
    def render(self):
        global actOri, objectcolor, perspectiveswitch, translateX, translateY, shadow

        #glLoadIdentity()
        self.objectvbo.bind()

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        glVertexPointer(3, GL_FLOAT, 24, self.objectvbo)
        glNormalPointer(GL_FLOAT, 24, self.objectvbo + 12)

        # SCHATTEN --------------
        if shadow:
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()

            glTranslatef(0, self.smallestpoint[1], 0)  # Schatten an die richtige Y-Stelle schieben

            glTranslatef(self.xlight, self.ylight, self.zlight)
            glMultMatrixf(self.p_light)
            glTranslatef(-self.xlight, -self.ylight, -self.zlight)
            glColor3f(0.7, 0.7, 0.7)

            # Beleuchtung beim Drawn des Schattens ausschalten, weil schatten nicht beleuchtet werden soll
            glDisable(GL_DEPTH_TEST)
            glDisable(GL_LIGHTING)
            glDrawArrays(GL_TRIANGLES, 0, len(self.faces * 3))

            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
            glPopMatrix()
        #  -----------------------

        glLoadIdentity()

        glColor3f(objectcolor[0], objectcolor[1], objectcolor[2])

        glTranslatef(translateX, -translateY, 0) # Verschieben des Objekts auf der xy-ebene

        glMultMatrixf(actOri * self.rotate(angle, axis)) # Rotation wie VL

        glScalef(self.scale_factor, self.scale_factor, self.scale_factor)
        glTranslatef(-self.bb_center[0], -self.bb_center[1], -self.bb_center[2])
        glDrawArrays(GL_TRIANGLES, 0, len(self.faces*3))



        self.objectvbo.unbind()
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)

class RenderWindow:
    """GLFW Rendering window class"""

    def __init__(self):

        # save current working directory
        cwd = os.getcwd()

        # Initialize the library
        if not glfw.init():
            return

        # restore cwd
        os.chdir(cwd)

        self.action = 0

        self.mouseL = False
        self.mouseR = False

        self.startX = 0
        self.startY = 0

        # buffer hints
        glfw.window_hint(glfw.DEPTH_BITS, 32)

        # define desired frame rate
        self.frame_rate = 30

        # make a window
        self.width, self.height = 640, 480
        self.aspect = self.width / float(self.height)
        self.window = glfw.create_window(self.width, self.height, "2D Graphics", None, None)
        if not self.window:
            glfw.terminate()
            return

        # Make the window's context current
        glfw.make_context_current(self.window)

        # initialize GL
        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0, 0, 0, 1.0)
        glMatrixMode(GL_PROJECTION)

        # Enable Lights vorlesung
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)

        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

        glOrtho(-1.5 * self.aspect, 1.5 * self.aspect, -1.5, 1.5, -1, 10)

        glMatrixMode(GL_MODELVIEW)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_window_size_callback(self.window, self.onSize)

        # create 3D
        self.scene = Scene(self.width, self.height, self)

        # exit flag
        self.exitNow = False

        # animation flag
        self.animation = False


    def projectOnSphere(self, x, y, r):
        width, height = glfw.get_window_size(self.window)

        x, y = x-width/2.0, height/2.0-y
        a = min(r*r, x**2 + y**2)
        z = np.sqrt(r*r - a)
        l = np.sqrt(x**2 + y**2 + z**2)
        return x/l, y/l, z/l

    def mousemoved(self):
        global angle, axis, startP
        x, y = glfw.get_cursor_pos(self.window)

        r = min(self.width, self.height)/2.0
        moveP = self.projectOnSphere(x, y, r)
        angle = np.arccos(np.dot(startP, moveP))
        axis = np.cross(startP, moveP)

        print("mouseMoved")
        print(axis)
        print(angle)

    def onMouseButton(self, win, button, action, mods):
        global startP, translateX, translateY, angle, axis, actOri
        print("mouse button: ", win, button, action, mods)
        # button = Maustaste,  action=1 ist klick

        if button is 0 and action is 1:
            self.mouseL = True
            x, y = glfw.get_cursor_pos(self.window)
            width, height = glfw.get_window_size(self.window)
            r = min(width, height)/2 #ballradius
            startP = self.projectOnSphere(x, y, r)

            # Damit sich die Position nicht wieder bei jedem klick zurücksetzt
            actOri = np.dot(actOri, self.scene.rotate(angle, axis))
            angle = 0

        elif button is 0 and action is 0:
            self.mouseL = False
        elif button is 1 and action is 1:
            self.mouseR = True
            self.startX, self.startY = glfw.get_cursor_pos(self.window)

            print(startP)
            print("Schieb")

        elif button is 1 and action is 0:
            self.mouseR = False



    def onKeyboard(self, win, key, scancode, action, mods):
        print("keyboard: ", win, key, scancode, action, mods)
        global colortoggle, objectcolor, perspectiveswitch, shadow

        if action == glfw.PRESS:
            # T to switch between object and background color
            if key == glfw.KEY_T:
                if colortoggle:
                    colortoggle = False
                else:
                    colortoggle = True

            # ESC to quit
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True
            if key == glfw.KEY_S:
                if colortoggle:
                    glClearColor(0, 0, 0, 1.0)
                else:
                    objectcolor = np.array([.0, .0, .0])
            if key == glfw.KEY_W:
                if colortoggle:
                    glClearColor(1.0, 1.0, 1.0, 1.0)
                else:
                    objectcolor = np.array([1.0, 1.0, 1.0])
            if key == glfw.KEY_R:
                if colortoggle:
                    glClearColor(1.0, 0, 0, 1.0)
                else:
                    objectcolor = np.array([1.0, .0, .0])
            if key == glfw.KEY_G:
                if colortoggle:
                    glClearColor(0, 1.0, 0, 1.0)
                else:
                    objectcolor = np.array([.0, 1.0, .0])
            if key == glfw.KEY_B:
                if colortoggle:
                    glClearColor(0, 0, 1.0, 1.0)
                else:
                    objectcolor = np.array([.0, .0, 1.0])

            if key == glfw.KEY_H:
                if shadow:
                    shadow = False
                    print("SHADOW OFF")
                else:
                    shadow = True
                    print("SHADOW ON")

            # Switch PERSPECTIVE
            if key == glfw.KEY_O:
                self.switchPerspective(0)

            if key == glfw.KEY_P:
                self.switchPerspective(1)

    def switchPerspective(self, b):
        global perspectiveswitch

        if b == 0: # Ortho
            perspectiveswitch = False
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(-1.5 * self.aspect, 1.5 * self.aspect, -1.5, 1.5, -1, 10)
            gluLookAt(0, 0, 3, 0, 0, 0, 0, 1, 0)
            glMatrixMode(GL_MODELVIEW)
        elif b == 1: # Frustum
            perspectiveswitch = True
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glFrustum(-1.5 * self.aspect, 1.5 * self.aspect, -1.5, 1.5, 2.5, 10)
            gluLookAt(0, 0, 4, 0, 0, 0, 0, 1, 0)
            glMatrixMode(GL_MODELVIEW)
        else:
            print("Not supported mode")


    def onSize(self, win, width, height):
        global perspectiveswitch
        print("onsize: ", win, width, height)
        self.width = width
        self.height = height

        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if self.width >= self.height:
            self.aspect = width / float(height)

            if perspectiveswitch:
                self.switchPerspective(1)
            else:
                glOrtho(-1.5 * self.aspect, 1.5 * self.aspect, -1.5, 1.5, -1.0, 10)
        else:
            self.aspect = height / float(width)

            if perspectiveswitch:
                self.switchPerspective(1)
            else:
                glOrtho(-1.5, 1.5, -1.5 * self.aspect, 1.5 * self.aspect, -1.0, 10)

        #glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_MODELVIEW)

    def run(self):
        global translateX, translateY
        # initializer timer
        glfw.set_time(0.0)
        t = 0.0
        while not glfw.window_should_close(self.window) and not self.exitNow:
            # update every x seconds
            currT = glfw.get_time()
            if currT - t > 1.0 / self.frame_rate:
                # update time
                t = currT
                # clear
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                # render scene
                if self.animation:
                    self.scene.step()

                # Wenn bestimmte Maustaste gedrückt gehalten wird
                if self.mouseL:
                    self.mousemoved()

                if self.mouseR:
                    x, y = glfw.get_cursor_pos(self.window)
                    # startP = np.array([x, y, 0])

                    translateX = translateX + float(float((x - self.startX)) / self.width)
                    translateY = translateY + float(float((y - self.startY)) / self.height)

                self.scene.render()

                glfw.swap_buffers(self.window)

                # Poll for and process events
                glfw.poll_events()
        # end
        glfw.terminate()


# main() function
def main():
    print("Simple glfw render Window")
    rw = RenderWindow()
    rw.run()


# call main
if __name__ == '__main__':
    main()