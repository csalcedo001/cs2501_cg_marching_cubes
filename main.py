import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import matplotlib.cm
import numpy as np
import pickle



def get_normal(triangle):
    side1 = triangle[1] - triangle[0]
    side2 = triangle[2] - triangle[0]
    normal = np.cross(side1, side2)
    normal = normal / np.linalg.norm(normal)

    return normal

blues = matplotlib.cm.get_cmap('Blues')

def get_color(triangle, light_color, color_map=blues):
    normal = get_normal(triangle)
    lighting = np.dot(normal, light_color / np.linalg.norm(light_color))
    color = color_map(1 - lighting)

    return light_color

light_pos = np.array([0, 0, 0])
light_color = np.array([1, 1, 1])


# pygame.init()
# display = (400,400)
# window = pygame.display.set_mode(display, DOUBLEBUF|OPENGL)


# gluPerspective(45, 1, 0.1, 50.0)
# glTranslatef(0.0,0.0, -5)
# glEnable(GL_CULL_FACE)
# glEnable(GL_DEPTH_TEST)
# glCullFace(GL_BACK)




with open("model.pkl", "rb") as f:
    model = np.array(pickle.load(f))
    print(model.shape)



pygame.init()
display = (1000, 800)
scree = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
# glDepthFunc(GL_LESS)
glShadeModel(GL_SMOOTH)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

glEnable(GL_LIGHT0)
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])

sphere = gluNewQuadric()

glMatrixMode(GL_PROJECTION)
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

glMatrixMode(GL_MODELVIEW)
gluLookAt(0, -8, 0, 0, 0, 0, 0, 0, 1)
viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
glLoadIdentity()

# init mouse movement and center mouse on screen
displayCenter = [scree.get_size()[i] // 2 for i in range(2)]
mouseMove = [0, 0]
pygame.mouse.set_pos(displayCenter)


up_down_angle = 0.0
paused = False
run = True

# Center model in center of coordinates
translation = np.array([
    (model[:, :, 0].max() + model[:, :, 0].min()) / 2,
    (model[:, :, 1].max() + model[:, :, 1].min()) / 2,
    (model[:, :, 2].max() + model[:, :, 2].min()) / 2,
])
model = model - translation

# Rotate model to face to the camera
x_angle = -90 * (np.pi / 180)
rot_x = np.array([
    [1, 0, 0],
    [0, np.cos(x_angle), -np.sin(x_angle)],
    [0, np.sin(x_angle), np.cos(x_angle)]
])

y_angle = -90 * (np.pi / 180)
rot_y = np.array([
    [np.cos(y_angle), 0, np.sin(y_angle)],
    [0, 1, 0],
    [-np.sin(y_angle), 0, np.cos(y_angle)]
])
rot = np.matmul(rot_y, rot_x)

model = np.einsum('km,ijk->ijm', rot, model)

# Scaling to make model smaller
model[:, :, 0] = model[:, :, 0] / model[:, :, 0].max()
model[:, :, 1] = model[:, :, 1] / model[:, :, 1].max()
model[:, :, 2] = model[:, :, 2] / model[:, :, 2].max()

clock = pygame.time.Clock()
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                run = False
            if event.key == pygame.K_PAUSE or event.key == pygame.K_p:
                paused = not paused
                pygame.mouse.set_pos(displayCenter) 
        if not paused: 
            if event.type == pygame.MOUSEMOTION:
                mouseMove = [event.pos[i] - displayCenter[i] for i in range(2)]
            pygame.mouse.set_pos(displayCenter)    

    if not paused:
        # get keys
        keypress = pygame.key.get_pressed()
        #mouseMove = pygame.mouse.get_rel()
    
        # init model view matrix
        glLoadIdentity()

        # apply the look up and down
        up_down_angle += mouseMove[1]*0.1
        glRotatef(up_down_angle, 1.0, 0.0, 0.0)

        # init the view matrix
        glPushMatrix()
        glLoadIdentity()

        # apply the movment
        speed = 0.2
        if keypress[pygame.K_w]:
            glTranslatef(0, 0, speed)
        if keypress[pygame.K_s]:
            glTranslatef(0, 0, -speed)
        if keypress[pygame.K_d]:
            glTranslatef(-speed, 0, 0)
        if keypress[pygame.K_a]:
            glTranslatef(speed, 0, 0)
        if keypress[pygame.K_SPACE]:
            glTranslatef(0, -speed, 0)
        if keypress[pygame.K_LSHIFT]:
            glTranslatef(0, speed, 0)

        # apply the left and right rotation
        rot_speed = 0.2
        glRotatef(mouseMove[0] * rot_speed, 0.0, 1.0, 0.0)

        # multiply the current matrix by the get the new view matrix and store the final vie matrix 
        glMultMatrixf(viewMatrix)
        viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

        # apply view matrix
        glPopMatrix()
        glMultMatrixf(viewMatrix)

        glLightfv(GL_LIGHT0, GL_POSITION, [1, -1, 1, 0])

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glPushMatrix()


        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glBegin(GL_TRIANGLES)
        for face in model:
            # color = get_color(face, light_color, blues)
            color = (1, 1, 1)
            for vertex in face:
                glColor3fv((color[0], color[1], color[2]))
                glVertex3fv(vertex)
                glNormal3fv(get_normal(face))
        glEnd()


        glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)

pygame.quit()