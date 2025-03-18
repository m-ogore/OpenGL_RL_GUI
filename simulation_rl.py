import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random

# Global variables for drone state
rotation_angle = 0
drone_x, drone_y, drone_z = 0.0, 0.0, 1.0
drone_pitch, drone_yaw, drone_roll = 0.0, 0.0, 0.0
target_x, target_y, target_z = 0.0, 0.0, 1.0
target_pitch, target_yaw, target_roll = 0.0, 0.0, 0.0
move_timer = 0

def init():
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Set light position and properties
    glLight(GL_LIGHT0, GL_POSITION, (5, 5, 5, 1))
    glLight(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))

def draw_motor(x, y, z):
    """Draw a motor with a propeller at the specified position"""
    global rotation_angle
    
    # Motor base (cylinder)
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.2, 0.2, 0.2)
    cylinder = gluNewQuadric()
    gluCylinder(cylinder, 0.15, 0.15, 0.1, 16, 8)
    
    # Propeller disc
    glTranslatef(0, 0, 0.1)
    glColor3f(0.5, 0.5, 0.5)
    gluDisk(cylinder, 0.0, 0.15, 16, 1)
    
    # Propellers
    glRotatef(rotation_angle, 0, 0, 1)  # Rotate propellers
    glColor3f(0.7, 0.7, 0.7)
    for i in range(3):
        glRotatef(120, 0, 0, 1)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, 0)
        glVertex3f(0.5, 0.1, 0)
        glVertex3f(0.5, -0.1, 0)
        glEnd()
    
    glPopMatrix()

def draw_drone_body():
    """Draw the main drone body"""
    # Center hub
    glPushMatrix()
    glColor3f(0.3, 0.3, 0.8)
    sphere = gluNewQuadric()
    gluSphere(sphere, 0.4, 16, 16)
    
    # Cross arms
    glColor3f(0.7, 0.3, 0.3)
    for i in range(4):
        glPushMatrix()
        glRotatef(i * 90, 0, 0, 1)
        
        # Arm
        glPushMatrix()
        glRotatef(90, 0, 1, 0)
        cylinder = gluNewQuadric()
        gluCylinder(cylinder, 0.1, 0.1, 1.0, 8, 4)
        glPopMatrix()
        
        glPopMatrix()
    
    # Camera/sensor at bottom
    glColor3f(0.2, 0.2, 0.2)
    glTranslatef(0, 0, -0.4)
    gluCylinder(sphere, 0.2, 0.1, 0.2, 16, 4)
    
    glPopMatrix()

def draw_drone():
    """Draw the complete drone"""
    global drone_x, drone_y, drone_z, drone_pitch, drone_yaw, drone_roll
    
    glPushMatrix()
    
    # Position the drone at its current location
    glTranslatef(drone_x, drone_y, drone_z)
    
    # Add orientation rotation to the drone
    glRotatef(drone_pitch, 1, 0, 0)
    glRotatef(drone_yaw, 0, 1, 0)
    glRotatef(drone_roll, 0, 0, 1)
    
    # Draw body
    draw_drone_body()
    
    # Draw motors at the ends of arms
    arm_length = 1.0
    draw_motor(arm_length, 0, 0)
    draw_motor(-arm_length, 0, 0)
    draw_motor(0, arm_length, 0)
    draw_motor(0, -arm_length, 0)
    
    glPopMatrix()

def draw_grid():
    """Draw a 4x4 grid on the ground"""
    glPushMatrix()
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINES)
    
    # Draw the grid lines
    for i in range(5):
        # Lines along X axis
        glVertex3f(-2.0, -2.0 + i, 0.0)
        glVertex3f(2.0, -2.0 + i, 0.0)
        
        # Lines along Y axis
        glVertex3f(-2.0 + i, -2.0, 0.0)
        glVertex3f(-2.0 + i, 2.0, 0.0)
    
    glEnd()
    
    # Draw grid cell markers
    for x in range(4):
        for y in range(4):
            glPushMatrix()
            glTranslatef(-1.5 + x, -1.5 + y, 0.01)
            glColor3f(0.8, 0.8, 0.8)
            glBegin(GL_QUADS)
            glVertex3f(-0.05, -0.05, 0)
            glVertex3f(0.05, -0.05, 0)
            glVertex3f(0.05, 0.05, 0)
            glVertex3f(-0.05, 0.05, 0)
            glEnd()
            glPopMatrix()
    
    glPopMatrix()

def update_drone_position():
    """Update the drone's position using the current target and interpolation"""
    global drone_x, drone_y, drone_z
    global target_x, target_y, target_z
    global drone_pitch, drone_yaw, drone_roll
    global target_pitch, target_yaw, target_roll
    global move_timer
    
    # Check if we need a new target
    move_timer -= 1
    if move_timer <= 0:
        # Set a new random target on the 4x4 grid
        grid_x = random.randint(0, 3)
        grid_y = random.randint(0, 3)
        target_x = -1.5 + grid_x
        target_y = -1.5 + grid_y
        target_z = 1.0 + random.random() * 0.5  # Random height between 1.0 and 1.5
        move_timer = 120  # Stay at each position for about 2 seconds (60 fps * 2)
        
        # Calculate new direction for the drone to face
        dx = target_x - drone_x
        dy = target_y - drone_y
        
        # Update yaw target to face the direction of movement
        if abs(dx) > 0.01 or abs(dy) > 0.01:
            target_yaw = math.degrees(math.atan2(dx, dy))
    
    # Smoothly interpolate towards the target
    drone_x += (target_x - drone_x) * 0.02
    drone_y += (target_y - drone_y) * 0.02
    drone_z += (target_z - drone_z) * 0.02
    
    # Get the direction of movement
    dx = target_x - drone_x
    dy = target_y - drone_y
    
    # Calculate appropriate banking angles based on movement
    target_pitch = dy * 20  # Bank forward/backward when moving along Y
    target_roll = -dx * 20  # Bank left/right when moving along X
    
    # Smooth the orientation changes
    drone_pitch += (target_pitch - drone_pitch) * 0.05
    drone_roll += (target_roll - drone_roll) * 0.05
    drone_yaw += (target_yaw - drone_yaw) * 0.05
    
    # Normalize yaw to 0-360
    if drone_yaw > 360:
        drone_yaw -= 360
    elif drone_yaw < 0:
        drone_yaw += 360

def main():
    global rotation_angle, drone_x, drone_y, drone_z
    global drone_pitch, drone_yaw, drone_roll
    global target_x, target_y, target_z
    global target_pitch, target_yaw, target_roll
    global move_timer
    
    # Initialize drone position and orientation
    rotation_angle = 0
    drone_x, drone_y, drone_z = 0.0, 0.0, 1.0
    drone_pitch, drone_yaw, drone_roll = 0.0, 0.0, 0.0
    
    # Initialize target position and orientation
    target_x, target_y, target_z = drone_x, drone_y, drone_z
    target_pitch, target_yaw, target_roll = 0.0, 0.0, 0.0
    move_timer = 0  # Immediately set a new target
    
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Drone Simulation - Random Grid Flight")
    
    init()
    
    # Set up perspective
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, -6, 4,  # Camera position - further back and higher
              0, 0, 1,   # Look at point
              0, 0, 1)   # Up vector
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update propeller rotation
        rotation_angle += 15
        if rotation_angle > 360:
            rotation_angle -= 360
        
        # Update drone position and orientation
        update_drone_position()
        
        # Clear the screen and draw
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Draw grid
        draw_grid()
        
        # Draw drone
        draw_drone()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()