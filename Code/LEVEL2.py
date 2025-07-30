import sys
from PyQt5.QtWidgets import QApplication, QOpenGLWidget, QMainWindow, QPushButton
from PyQt5.QtCore import QTimer, Qt, QPoint, QUrl, QRect
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtGui import QImage, QOpenGLTexture, QKeyEvent, QFont, QColor, QPainter
from PyQt5.QtWidgets import QLabel
from OpenGL.GLUT import glutBitmapCharacter, GLUT_BITMAP_HELVETICA_12
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

# Colors
WHITE = [1, 1, 1]
PURPLE = [0.5, 0, 0.5]
LIGHT_PURPLE = [0.6, 0.1, 0.6]
LIGHT_YELLOW = [1.0, 1.0, 0.5]
RED = [1.0, 0.0, 0.0]
DARK_RED = [0.5, 0.0, 0.0]
LIGHT_BLUE = [0.5, 0.5, 1.0, 1.0]
BLUE = [0.0, 0.0, 0.4, 1.0]

texture = None  # Global variable for texture

class Ball:
    def __init__(self, r, c, h, x, z, path, widget):
        self.radius = r
        self.color = c
        self.maximumHeight = h
        self.baseHeight = h
        self.y = h
        self.x = x
        self.z = z + 0.05
        self.path = path
        self.widget = widget
        self.jumping = False
        self.jump_velocity = 0.15
        self.gravity = -0.007
        self.horizontal_speed = 0.02
        self.rotation_angle = 0
        self.waiting_for_start = False
        self.on_block_or_stair = False
        self.landing_offset = 0.03

    def update(self, blocks, reset_scene_callback, running):
        if not running:
            return

        self.on_block_or_stair = False  # Reset the flag

        self.x += self.horizontal_speed
        self.rotation_angle += 10

        if self.x > 15:
            self.widget.game_won = True
            self.widget.running = False
            self.widget.restart_button.show()
            return

        self.widget.distance_traveled += self.horizontal_speed

        if self.jumping:
            self.y += self.jump_velocity
            self.jump_velocity += self.gravity
            if self.y <= self.baseHeight:
                self.y = self.baseHeight
                self.jumping = False
                self.jump_velocity = 0.0

        # Collision detection with blocks
        for block in blocks:
            if (block.x - block.size < self.x < block.x + block.size and
                block.y - block.size < self.y < block.y + block.size and
                block.z - block.size < self.z < block.z + block.size):
                self.widget.game_over = True
                self.widget.running = False
                self.widget.restart_button.show()
                break

        # Collision detection with stairs
        for stair in self.path.stairs:
            if (stair.x - stair.size < self.x < stair.x + stair.size and
                stair.z - stair.size < self.z < stair.z + stair.size):
                if stair.y <= self.y <= stair.y + stair.height:
                    self.on_block_or_stair = True
                    if self.y > stair.y + stair.height - self.radius:
                        self.y = stair.y + stair.height - self.radius + 0.065
                        self.jumping = False  # End the jumping state upon landing
                        self.jump_velocity = 0.0
                        break

        # Apply gravity if the ball is not on any block or stair and is above the base height
        if not self.on_block_or_stair and not self.jumping:
            self.y += self.gravity * 15
            if self.y <= self.baseHeight:
                self.y = self.baseHeight
                self.jump_velocity = 0.0

        # Allow jumping if on a block or stair
        if self.on_block_or_stair and not self.jumping:
            self.jump_velocity = 0.0  # Ensure jump velocity is reset when landing

        # Collision detection with stars
        for star in self.path.stars:
            if not star.collected:
                distance = math.sqrt((self.x - star.x) ** 2 + (self.y - star.y) ** 2 + (self.z - star.z) ** 2)
                if distance < self.radius + star.size:
                    star.collected = True
                    self.widget.score += 10
                    self.widget.points_collected_label.setText(f'Points Collected: {self.widget.score}')

        for cone in self.path.cones:
            if (self.x - cone.x)**2 + (self.z - cone.z)**2 < (self.radius + cone.base_radius)**2:
                if cone.is_hanging:
                    if cone.y - cone.height < self.y < cone.y:
                        self.widget.game_over = True
                        self.widget.running = False
                        self.widget.restart_button.show()
                        break
                else:
                    if self.y < cone.y + cone.height:
                        self.widget.game_over = True
                        self.widget.running = False
                        self.widget.restart_button.show()
                        break

        for half_sphere in self.path.half_spheres:
            if (self.x - half_sphere.x)**2 + (self.z - half_sphere.z)**2 < (self.radius + half_sphere.radius)**2:
                if self.y <= half_sphere.y + half_sphere.radius:
                    self.double_jump()

    def draw(self):
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.color)
        glTranslated(self.x, self.y, self.z)
        glRotatef(self.rotation_angle, 0, 0, 1)
        self.draw_sphere(self.radius, 30, 30)
        glPopMatrix()

    def double_jump(self):
        if not self.jumping:
            self.jumping = True
            self.jump_velocity = 0.09 * 2  # Higher initial jump velocity for double jump

    def draw_shadow(self):
        if texture is not None and isinstance(texture, QOpenGLTexture):
            texture.bind()

        glPushMatrix()
        glDisable(GL_LIGHTING)
        glColor4f(0.0, 0.0, 0.0, 0.5)

        shadow_y = self.baseHeight - 0.08

        shadow_offset = 0.05
        shadow_x = self.x - shadow_offset
        shadow_z = self.z

        glTranslatef(shadow_x, shadow_y, shadow_z)
        glScalef(1.0, 0.0, 1.0)

        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluQuadricTexture(quad, GL_TRUE)
        gluSphere(quad, self.radius, 32, 32)
        gluDeleteQuadric(quad)

        if texture is not None:
            glBindTexture(GL_TEXTURE_2D, 0)

        glEnable(GL_LIGHTING)
        glPopMatrix()

    def draw_sphere(self, radius, slices, stacks):
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluQuadricTexture(quadric, GL_TRUE)

        if texture is not None:
            glEnable(GL_TEXTURE_2D)
            texture.bind()

        gluSphere(quadric, radius, slices, stacks)
        gluDeleteQuadric(quadric)

        if texture is not None:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

    def jump(self):
        if self.on_block_or_stair or not self.jumping:
            self.jumping = True
            self.jump_velocity = 0.113  # Adjust jump velocity as needed

    def reset(self):
        self.x = 1.2
        self.y = self.baseHeight
        self.jumping = False
        self.jump_velocity = 0.0
        self.rotation_angle = 0
        self.waiting_for_start = True
        self.widget.score = 0  # Reset the score
        self.widget.points_collected_label.setText(f'Points Collected: {self.widget.score}')  # Update the label
        for star in self.path.stars:
            star.collected = False  # Reset stars collection status

class Star:
    def __init__(self, x, y, z, size, color):
        self.x = x
        self.y = y
        self.z = z
        self.size = size
        self.color = color
        self.collected = False  # Flag to check if the star is collected

    def draw(self):
        if not self.collected:
            glPushMatrix()
            glColor3fv(self.color)  # Set the color using glColor4fv
            glTranslatef(self.x, self.y, self.z)
            glScalef(self.size, self.size, self.size)
            self.draw_star()
            glPopMatrix()

    def draw_star(self):
        glBegin(GL_TRIANGLES)
        for i in range(5):
            angle1 = i * 2 * math.pi / 5
            angle2 = (i + 2) * 2 * math.pi / 5
            glVertex3f(0, 0, 0)
            glVertex3f(math.cos(angle1), math.sin(angle1), 0)
            glVertex3f(math.cos(angle2), math.sin(angle2), 0)
        glEnd()

class Block:
    def __init__(self, x, y, z, size, color):
        self.x = x
        self.y = y
        self.z = z
        self.size = size
        self.color = color

    def draw(self):
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.color)
        glTranslated(self.x, self.y, self.z)
        self.draw_cube(self.size)
        glPopMatrix()

    def draw_cube(self, size):
        half_size = size / 2.0

        vertices = [
            [-half_size, -half_size, -half_size],
            [half_size, -half_size, -half_size],
            [half_size, half_size, -half_size],
            [-half_size, half_size, -half_size],
            [-half_size, -half_size, half_size],
            [half_size, -half_size, half_size],
            [half_size, half_size, half_size],
            [-half_size, half_size, half_size]
        ]

        faces = [
            [0, 1, 2, 3],  # Back face
            [4, 5, 6, 7],  # Front face
            [0, 1, 5, 4],  # Bottom face
            [2, 3, 7, 6],  # Top face
            [0, 3, 7, 4],  # Left face
            [1, 2, 6, 5]   # Right face
        ]

        normals = [
            [0, 0, -1],  # Back face normal
            [0, 0, 1],   # Front face normal
            [0, -1, 0],  # Bottom face normal
            [0, 1, 0],   # Top face normal
            [-1, 0, 0],  # Left face normal
            [1, 0, 0]    # Right face normal
        ]

        # Draw filled faces
        glBegin(GL_QUADS)
        for face, normal in zip(faces, normals):
            glNormal3fv(normal)
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()

        # Draw edges with black color
        glDisable(GL_LIGHTING)  # Disable lighting
        glColor3f(0, 0, 0)  # Set color to black
        glLineWidth(3.0)  # Set line width (optional, for better visibility)
        glBegin(GL_LINES)
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Back face edges
            (4, 5), (5, 6), (6, 7), (7, 4),  # Front face edges
            (0, 4), (1, 5), (2, 6), (3, 7)   # Side edges
        ]
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()
        glEnable(GL_LIGHTING)  # Re-enable lighting

        # Reset color to white (or any default color) to avoid affecting other objects
        glColor3f(1, 1, 1)
        
class StairBlock(Block):
    def __init__(self, x, y, z, width, height, depth, color):
        super().__init__(x, y, z, width, color)
        self.height = height
        self.depth = depth

    def draw(self):
        glPushMatrix()
        glTranslated(self.x, self.y, self.z)
        glScalef(self.size, self.height, self.depth)  # Scale the block with different height
        self.draw_stair(1, 1, 1)  # Draw a unit stair block scaled appropriately
        glPopMatrix()

    def draw_stair(self, width, height, length):
        half_width = width / 2.0
        half_height = height / 2.0
        half_length = length / 2.0

        vertices = [
            [-half_width, -half_height, -half_length],
            [half_width, -half_height, -half_length],
            [half_width, half_height, -half_length],
            [-half_width, half_height, -half_length],
            [-half_width, -half_height, half_length],
            [half_width, -half_height, half_length],
            [half_width, half_height, half_length],
            [-half_width, half_height, half_length]
        ]

        faces = [
            [0, 1, 2, 3],  # Back face
            [4, 5, 6, 7],  # Front face
            [0, 1, 5, 4],  # Bottom face
            [2, 3, 7, 6],  # Top face
            [0, 3, 7, 4],  # Left face
            [1, 2, 6, 5]   # Right face
        ]

        normals = [
            [0, 0, -1],  # Back face normal
            [0, 0, 1],   # Front face normal
            [0, -1, 0],  # Bottom face normal
            [0, 1, 0],   # Top face normal
            [-1, 0, 0],  # Left face normal
            [1, 0, 0]    # Right face normal
        ]

        # Draw filled faces with black material
        black = [0.0, 0.0, 0.0, 1.0]
        glMaterialfv(GL_FRONT, GL_AMBIENT, black)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, black)
        glMaterialfv(GL_FRONT, GL_SPECULAR, black)
        glMaterialf(GL_FRONT, GL_SHININESS, 0.0)

        glBegin(GL_QUADS)
        for face, normal in zip(faces, normals):
            glNormal3fv(normal)
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()

        # Draw edges with white color
        glDisable(GL_LIGHTING)  # Disable lighting
        glColor3f(1, 1, 1)  # Set color to white
        glLineWidth(2.0)  # Set line width (optional, for better visibility)
        glBegin(GL_LINES)
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Back face edges
            (4, 5), (5, 6), (6, 7), (7, 4),  # Front face edges
            (0, 4), (1, 5), (2, 6), (3, 7)   # Side edges
        ]
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()
        glEnable(GL_LIGHTING)  # Re-enable lighting

        # Reset color to white (or any default color) to avoid affecting other objects
        glColor3f(1, 1, 1)

class Cone:
    def __init__(self, x, y, z, base_radius, height, color, is_hanging=False):
        self.x = x
        self.y = y
        self.z = z
        self.base_radius = base_radius
        self.height = height
        self.color = color
        self.is_hanging = is_hanging  # Add is_hanging attribute to indicate if the cone is hanging

    def draw(self):
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.color)
        glTranslatef(self.x, self.y, self.z)
        self.draw_cone(self.base_radius, self.height)
        glPopMatrix()

    def draw_cone(self, base_radius, height):
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluQuadricTexture(quad, GL_TRUE)

        glPushMatrix()
        if self.is_hanging:
            glRotatef(180, 1, 0, 0)  # Rotate around the x-axis by 180 degrees if the cone is hanging

        glRotatef(-90, 1, 0, 0)  # Rotate around the x-axis to stand upright

        gluCylinder(quad, base_radius, 0.0, height, 30, 30)
        gluDisk(quad, 0.0, base_radius, 30, 1)  # Draw base disk

        gluDeleteQuadric(quad)
        glPopMatrix()

        # Draw edges with black color
        self.draw_edges(base_radius, height)
        self.draw_base_outline(base_radius)

    def draw_edges(self, base_radius, height):
        # Disable lighting to draw the edges
        glDisable(GL_LIGHTING)
        glColor3f(0, 0, 0)  # Set color to black
        glLineWidth(3.0)  # Set line width (optional, for better visibility)

        glPushMatrix()
        if self.is_hanging:
            glRotatef(180, 1, 0, 0)  # Rotate the edges if the cone is hanging

        # Calculate the positions for the edges
        angle1 = 0  # First edge
        angle2 = math.pi + 0.3  # Opposite side for the second edge

        x1 = base_radius * math.cos(angle1)
        y1 = base_radius * math.sin(angle1)
        x2 = base_radius * math.cos(angle2)
        y2 = base_radius * math.sin(angle2)

        # Draw first edge
        glBegin(GL_LINES)
        glVertex3f(x1, 0, y1)
        glVertex3f(0, height, 0)
        glEnd()

        # Draw second edge
        glBegin(GL_LINES)
        glVertex3f(x2, 0, y2)
        glVertex3f(0, height, 0)
        glEnd()

        glPopMatrix()

        # Re-enable lighting
        glEnable(GL_LIGHTING)

        # Reset color to white (or any default color) to avoid affecting other objects
        glColor3f(1, 1, 1)

    def draw_base_outline(self, base_radius):
        # Disable lighting to draw the outline
        glDisable(GL_LIGHTING)
        glColor3f(0, 0, 0)  # Set color to black
        glLineWidth(2.0)  # Set line width (optional, for better visibility)

        num_segments = 30  # Number of segments to approximate the circle

        glBegin(GL_LINE_LOOP)
        for i in range(num_segments):
            angle = 2 * math.pi * i / num_segments
            x = base_radius * math.cos(angle)
            z = base_radius * math.sin(angle)
            glVertex3f(x, 0, z)
        glEnd()

        # Re-enable lighting
        glEnable(GL_LIGHTING)

        # Reset color to white (or any default color) to avoid affecting other objects
        glColor3f(1, 1, 1)
        
class HalfSphere:
    def __init__(self, x, y, z, radius, color):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.color = color
        self.animation_phase = 0  # Add this line to track the animation phase

    def update_color(self):
        # Update the animation phase
        self.animation_phase += 5
        if self.animation_phase > 360:
            self.animation_phase -= 360
        
        # Calculate color based on sine wave for smooth transition
        t = self.animation_phase / 360.0
        r = 0.5 * (1 + math.sin(2 * math.pi * (t + 0 / 3)))
        g = 0.5 * (1 + math.sin(2 * math.pi * (t + 1 / 3)))
        b = 0.5 * (1 + math.sin(2 * math.pi * (t + 2 / 3)))
        self.color = [r, g, b]

    def draw(self):
        self.update_color()  # Add this line to update the color before drawing
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.color)
        glTranslatef(self.x, self.y, self.z)
        self.draw_half_sphere(self.radius, 30, 30)
        glPopMatrix()

    def draw_half_sphere(self, radius, slices, stacks):
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluQuadricTexture(quadric, GL_TRUE)

        for i in range(stacks // 2):
            theta1 = i * 2 * math.pi / stacks - (math.pi / 2)
            theta2 = (i + 1) * 2 * math.pi / stacks - (math.pi / 2)

            glBegin(GL_TRIANGLE_STRIP)
            for j in range(slices + 1):
                theta3 = j * 2 * math.pi / slices

                x1 = radius * math.cos(theta2) * math.cos(theta3)
                y1 = radius * math.sin(theta2)
                z1 = radius * math.cos(theta2) * math.sin(theta3)
                glColor3f(*self.color)  # Set vertex color
                glNormal3f(x1 / radius, y1 / radius, z1 / radius)
                glVertex3f(x1, y1, z1)

                x2 = radius * math.cos(theta1) * math.cos(theta3)
                y2 = radius * math.sin(theta1)
                z2 = radius * math.cos(theta1) * math.sin(theta3)
                glColor3f(*self.color)  # Set vertex color
                glNormal3f(x2 / radius, y2 / radius, z2 / radius)
                glVertex3f(x2, y2, z2)
            glEnd()
        gluDeleteQuadric(quadric)

class Path:
    def __init__(self):
        self.displayListId = None
        self.blocks = [
            Block(3.5, 0.2, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Red block
            #Block(4.5, 0.2, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Green block
            Block(10, 1.1, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Green block
            Block(11, 1.1, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Green block
            Block(6, 0.2, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Grey stair block
            Block(6.2, 0.2, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Another stair block
            Block(6.4, 0.2, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Another stair block
            Block(6.6, 0.2, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Another stair block
            Block(6.8, 0.2, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Another stair block
            Block(7, 0.2, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Another stair block
            Block(7.6, 0.2, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Another stair block
            Block(7.8, 0.2, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Another stair block
            Block(8, 0.2, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Another stair block
            Block(8.2, 0.2, 0.6, 0.2,[1.0, 1.0, 0.5]),  # Another stair block
            Block(8.4, 0.2, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Another stair block
            Block(8.6, 0.2, 0.6, 0.2, [1.0, 1.0, 0.5]),  # Another stair block
        ]
        self.stairs = [
            StairBlock(6, 0.4, 0.6, 0.2, 0.2, 0.2, [0.0, 0.0, 0.]),  # Grey stair block
            StairBlock(6.2, 0.4, 0.6, 0.2, 0.2, 0.2, [0.0, 0.0, 0.]),  # Another stair block
            StairBlock(6.4, 0.4, 0.6, 0.2, 0.2, 0.2, [0.0, 0.0, 0.0]),  # Another stair block
            StairBlock(6.6, 0.4, 0.6, 0.2, 0.2, 0.2, [0.0, 0.0, 0.0]),  # Another stair block
            StairBlock(6.8, 0.4, 0.6, 0.2, 0.2, 0.2, [0.0, 0.0, 0.0]),  # Another stair block
            StairBlock(7, 0.4, 0.6, 0.2, 0.2, 0.2, [0.0, 0.0, 0.0]),  # Another stair block
            StairBlock(7.6, 0.4, 0.6, 0.2, 0.2, 0.2, [0.0,0.0, 0.0]),  # Another stair block
            StairBlock(7.8, 0.4, 0.6, 0.2, 0.2, 0.2, [0.0, 0.0, 0.0]),  # Another stair block
            StairBlock(8, 0.4, 0.6, 0.2, 0.2, 0.2, [0.0, 0.0, 0.0]),  # Another stair block
            StairBlock(8.2, 0.4, 0.6, 0.2, 0.2, 0.2, [0.0, 0.0, 0.0]),  # Another stair block
            StairBlock(8.4, 0.4, 0.6, 0.2, 0.2, 0.2, [0.0, 0.0, 0.0]),  # Another stair block
            StairBlock(8.6, 0.4, 0.6, 0.2, 0.2, 0.2, [0.0, 0.0, 0.0]),  # Another stair block
            StairBlock(13.5, 0.6, 0.6, 0.2, 0.1, 0.2, [0.0, 0.0, 0.0]),  # Another stair block
            StairBlock(13.9, 0.5, 0.6, 0.2, 0.1, 0.2, [0.0, 0.0, 0.0]),  # Another stair block
            StairBlock(14.3, 0.4, 0.6, 0.2, 0.1, 0.2, [0.0, 0.0, 0.0]),  # Another stair block

        ]
        self.stars = [
            Star(6, 0.8, 0.6, 0.1, LIGHT_YELLOW),  # Add a star to the path
            Star(11, 0.2, 0.6, 0.1, LIGHT_YELLOW),  # Add another star
            Star(14.3, 0.8, 0.6, 0.1, LIGHT_YELLOW)  # Add another star

        ]
        self.cones = [
            Cone(2.5, 0.1, 0.6, 0.1, 0.3, [0.8, 0.4, 0.6]),
            Cone(4.5, 0.1, 0.6, 0.1, 0.3, [0.8, 0.4, 0.6]),
            Cone(10, 1, 0.6, 0.1, 0.3, [0.8, 0.4, 0.6], is_hanging=True),   # New upside-down cone
            Cone(11, 1, 0.6, 0.1, 0.3, [0.8, 0.4, 0.6], is_hanging=True),   # New upside-down cone
            Cone(7.2, 0.1, 0.6, 0.1, 0.3, [0.8, 0.4, 0.6]),
            Cone(7.4, 0.1, 0.6, 0.1, 0.3, [0.8, 0.4, 0.6]),
            Cone(8, 0.6, 0.65, 0.1, 0.3, [0.8, 0.4, 0.6]),
            Cone(10.5, 0.1, 0.6, 0.1, 0.3, [0.8, 0.4, 0.6]),
            Cone(11.5, 0.1, 0.6, 0.1, 0.3, [0.8, 0.4, 0.6]),


        ]
        self.half_spheres = [
            HalfSphere(13, 0.01, 0.5, 0.1, LIGHT_YELLOW),
        ]
                
    def create(self):
        self.displayListId = glGenLists(1)
        glNewList(self.displayListId, GL_COMPILE)

        # Enable smooth shading
        glShadeModel(GL_SMOOTH)

        # Draw top faces of the path
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)
        glBegin(GL_QUADS)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, RED)
        
        # Extend the top_coords to make the path longer
        top_coords = [
            ((0, 0, 0), (6, 0, 0), (6, 0, 1), (0, 0, 1)),   # Top face of platform
            ((6, 0, 0), (12, 0, 0), (12, 0, 1), (6, 0, 1)), # Top face of path segment
            ((10, 0, 0), (16, 0, 0), (16, 0, 1), (10, 0, 1)) # Extend by 6 units
            # Add more segments as needed
        ]
        normals = [(0, 1, 0)] * len(top_coords)  # Normals for the top faces
        for quad, normal in zip(top_coords, normals):
            glNormal3f(*normal)
            for vertex in quad:
                glVertex3f(*vertex)
        glEnd()
        glDisable(GL_POLYGON_OFFSET_FILL)

        # Draw the black outline on the top faces
        glLineWidth(2.0)
        glDisable(GL_LIGHTING)  # Disable lighting to ensure color is accurate
        glColor3f(0.0, 0.0, 0.0)  # Set color to black for the outline
        glBegin(GL_LINES)
        for quad in top_coords:
            for i in range(4):
                start_vertex = quad[i]
                end_vertex = quad[(i + 1) % 4]
                # Only draw vertical lines (left and right edges)
                if i == 0 or i == 2:
                    glVertex3f(*start_vertex)
                    glVertex3f(*end_vertex)
        glEnd()
        glEnable(GL_LIGHTING)  # Re-enable lighting

        # Draw side faces of the path
        glBegin(GL_QUADS)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, DARK_RED)  # Set material for side faces
        
        # Extend the side_coords to make the path longer vertically
        side_coords = [
            # Left side face of platform
            ((0, 0, 1), (0, -1, 1.5), (6, -1, 1.5), (6, 0, 1)),
            # Right side face of platform
            ((0, 0, 0), (0, -1, 0.5), (6, -1, 0.5), (6, 0, 0)),
            # Left side face of path segment
            ((6, 0, 1), (6, -1, 1.5), (12, -1, 1.5), (12, 0, 1)),
            # Right side face of path segment
            ((6, 0, 0), (6, -1, 0.5), (12, -1, 0.5), (12, 0, 0)),
            # Additional segments to extend the path vertically
            ((12, 0, 1), (12, -1, 1.5), (16, -1, 1.5), (16, 0, 1)),
            ((12, 0, 0), (12, -1, 0.5), (16, -1, 0.5), (16, 0, 0)),
            
        ]
        side_normals = [
            (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0),
            (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0)
        ] * (len(side_coords) // 4)
        for quad, normal in zip(side_coords, side_normals):
            glNormal3f(*normal)
            for vertex in quad:
                glVertex3f(*vertex)
        glEnd()

        glEndList()

    def draw(self):
        glCallList(self.displayListId)
        for block in self.blocks:
            block.draw()
        for stair in self.stairs:
            stair.draw()
        for cone in self.cones:
            cone.draw()
        for half_sphere in self.half_spheres:
            half_sphere.draw()
        for star in self.stars:
            star.draw()
        self.draw_portal()
            
    def draw_portal(self):
        glPushMatrix()
        glTranslatef(15, 0.8, 0.5)  # Position the torus in the scene
        glRotatef(90, 7, 90, 0)  # Rotate 90 degrees around the x-axis to face the path
        glColor3f(0.5, 0.0, 0.5)  # Set the portal color to purple

        glutSolidTorus(0.09, 0.3, 30, 30)

        glPopMatrix()

class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(OpenGLWidget, self).__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)  # Set focus policy to receive keyboard events
        self.background_texture = None  # Separate texture for the background
        self.path = Path()
        self.scene_x = 0  # Variable to control the scene's horizontal movement
        self.running = False  # Control whether the scene is running
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateScene)
        self.timer.start(16)  # ~60 FPS
        
        # Initialize the media player and playlist
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        
        # Set the media file and play it
        url = QUrl.fromLocalFile(r"D:\fcg2024\Tutorial\FCG-2024_Mini Project\IMAGES_VIDEOS\SONG2.mp3")
        content = QMediaContent(url)
        self.playlist.addMedia(content)  # Add QMediaContent to the playlist
        self.playlist.setCurrentIndex(0)
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)  # Set the playback mode to loop
        self.player.setPlaylist(self.playlist)
        self.player.play()
        self.distance_traveled = 0.0
        self.high_score = 0.0
        self.running = False
        self.game_over = False  # Add this line        
        self.ball = Ball(0.1, WHITE, 0.1, 1.2, 0.5, self.path, self)  # Instantiate Ball object here
        self.restart_button = QPushButton('Restart', self)
        self.restart_button.setGeometry(247, 241, 100, 50)
        self.restart_button.clicked.connect(self.restart_game)
        self.restart_button.hide()  # Hide it initially
        self.game_won = False
        
        # Add the QLabel for "LEVEL 2" title
        self.level_label = QLabel('MEDIUM', self)
        self.level_label.setAlignment(Qt.AlignCenter)
        self.level_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 200);
                border: 2px solid black;  
                border-radius: 15px;
                padding: 10px;
                font-size: 20px;
                color: black;
            }
        """)
        self.level_label.setGeometry(230, 13, 150, 50)  # Adjusted width and height
        self.score = 0  # Add score attribute
        self.high_score = self.load_high_score()  # Load high score from file
        self.points_collected_label = QLabel('Points Collected: 0', self)
        self.points_collected_label.setAlignment(Qt.AlignCenter)
        self.points_collected_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 200);
                border: 2px solid black;  
                border-radius: 15px;
                padding: 10px;
                font-size: 16px;
                color: black;
            }
        """)
        self.points_collected_label.setGeometry(220, 73, 170, 50)  # Adjust these values as needed
        self.points_collected = self.load_points_collected()  # Load points collected from file
        self.points_collected_label.setText(f'Points Collected: {self.points_collected}')


    def load_high_score(self):
        try:
            with open('high_score_lv2.txt', 'r') as file:
                return float(file.read().strip())
        except FileNotFoundError:
            return 0.0

    def save_high_score(self):
        with open('high_score_lv2.txt', 'w') as file:
            file.write(f"{self.high_score:.2f}")
            
    def save_points_collected(self):
        with open('points_collected_lv2.txt', 'w') as file:
            file.write(f"{self.score}")
            
    def load_points_collected(self):
        try:
            with open('points_collected_lv2.txt', 'r') as file:
                return int(file.read().strip())
        except FileNotFoundError:
            return 0

    def restart_game(self):
        self.game_over = False
        self.running = False
        self.ball.reset()
        self.distance_traveled = 0.0
        self.restart_button.hide()
        
    def closeEvent(self, event):
        global texture
        self.makeCurrent()
        if texture is not None:
            texture.destroy()
            texture = None
        if self.background_texture is not None:
            self.background_texture.destroy()
            self.background_texture = None
        self.doneCurrent()
        super().closeEvent(event)
        
    def cleanupTextures(self):
        global texture
        if texture is not None:
            texture.destroy()
            texture = None
        if self.background_texture is not None:
            self.background_texture.destroy()
            self.background_texture = None
            
    def initializeGL(self):
        self.makeCurrent()
        glEnable(GL_DEPTH_TEST)  # Enable depth testing
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_TEXTURE_2D)
        
        glShadeModel(GL_SMOOTH)  # Enable smooth shading

        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])  # Increase diffuse reflection intensity
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.4, 0.4, 0.4, 1.0])  # Increase ambient light intensity

        # Set the position of the light source to shine directly on the path
        glLightfv(GL_LIGHT0, GL_POSITION, [-3.0, 2.0, -1.0, 0.0])  # Directional light from below

        # Set material properties
        glMaterialfv(GL_FRONT, GL_SPECULAR, WHITE)
        glMaterialf(GL_FRONT, GL_SHININESS, 30)

        self.path.create()
        
        self.ball.path = self.path  # Pass the Path instance to the Ball after Path creation
        
        # Load and set up texture
        self.load_texture()
        self.load_background_texture()  # Load the background texture separately
        self.doneCurrent()

    def load_texture(self):
        global texture
        file_path = r"D:\fcg2024\Tutorial\FCG-2024_Mini Project\IMAGES_VIDEOS\ball_level2.png"
        image = QImage(file_path)

        texture = QOpenGLTexture(image)
        texture.setMinificationFilter(QOpenGLTexture.Linear)
        texture.setMagnificationFilter(QOpenGLTexture.Linear)
        texture.setWrapMode(QOpenGLTexture.ClampToEdge)

    def load_background_texture(self):
        file_path = r"D:\fcg2024\Tutorial\FCG-2024_Mini Project\IMAGES_VIDEOS\background_level2.png"
        image = QImage(file_path)
    
        self.background_texture = QOpenGLTexture(image)
        self.background_texture.setMinificationFilter(QOpenGLTexture.Linear)
        self.background_texture.setMagnificationFilter(QOpenGLTexture.Linear)
        self.background_texture.setWrapMode(QOpenGLTexture.ClampToEdge)
        
    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(10.0, float(w) / float(h), 1.0, 150.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Adjust the camera position
        gluLookAt(-2 + self.scene_x, 9, 10,
                2 + self.scene_x, 0, 0,
                0.0, 1.0, 0.0)

        # Draw the background
        self.drawBackground()

        # Draw the path and other objects
        self.path.draw()  # This will also draw the portal

        # Draw the ball and its shadow
        self.ball.draw_shadow()
        self.ball.draw()

        # Update the ball's position and handle game logic
        self.ball.update(self.path.blocks, self.reset_scene, self.running)

        # Draw overlays if the game is over or won
        if self.game_over:
            self.show_game_over_overlay()
        elif self.game_won:
            self.show_game_won_overlay()

        # Draw the score bar
        self.draw_score_bar()

        glFlush()


    def draw_ball(self):
        self.ball.draw()
        
    def show_game_over_overlay(self):
        self.player.stop()  # Stop the music

        if self.distance_traveled > self.high_score:
            self.high_score = self.distance_traveled
            self.save_high_score()  # Save the new high score
            
        self.save_points_collected()  # Save the points collected

        glPushMatrix()
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Draw semi-transparent black rectangle to act as overlay
        glColor4f(0.0, 0.0, 0.0, 0.6)
        glBegin(GL_QUADS)
        glVertex2f(-1, 1)
        glVertex2f(1, 1)
        glVertex2f(1, -1)
        glVertex2f(-1, -1)
        glEnd()

        # Draw "GAME OVER!" text
        glColor3f(1.0, 1.0, 1.0)
        self.render_text("GAME OVER!", -0.19, - 0.01)

        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        # Show the restart button
        self.restart_button.show()

    def show_game_won_overlay(self):
        self.player.stop()  # Stop the music

        if self.distance_traveled > self.high_score:
            self.high_score = self.distance_traveled
            self.save_high_score()  # Save the new high score
        
        self.save_points_collected()  # Save the points collected

        glPushMatrix()
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Draw semi-transparent black rectangle to act as overlay
        glColor4f(0.0, 0.0, 0.0, 0.6)
        glBegin(GL_QUADS)
        glVertex2f(-1, 1)
        glVertex2f(1, 1)
        glVertex2f(1, -1)
        glVertex2f(-1, -1)
        glEnd()

        # Draw "YOU WIN!" text
        glColor3f(1.0, 1.0, 1.0)
        self.render_text("YOU WIN!", -0.158, -0.01)

        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        # Show the restart button
        self.restart_button.show()

    def draw_shadow(self):
        self.ball.draw_shadow()

    def drawBackground(self):
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)  # Enable texturing
        if self.background_texture is not None:
            glBindTexture(GL_TEXTURE_2D, self.background_texture.textureId())

            glBegin(GL_QUADS)
            glColor3f(1.0, 1.0, 1.0)  # Set the color to white for texture mapping

            # Calculate aspect ratio of the background image
            image_width = self.background_texture.width()
            image_height = self.background_texture.height()
            aspect_ratio = image_width / image_height

            # Define texture coordinates and vertices to maintain aspect ratio
            quad_height = 2.3

            # Adjust this scaling factor to increase or decrease height
            height_scaling_factor = 1.0  # Keep the height scaling factor the same
            quad_height *= height_scaling_factor

            # Define width scaling factor to make the background wider
            width_scaling_factor = 2.5  # Increase this value to make the background wider

            # Define quad width based on adjusted height and width scaling factor
            quad_width = quad_height * aspect_ratio * width_scaling_factor

            # Horizontal offset to move the background to the right
            offset_x = 5.7 # Adjust this value if needed

            glTexCoord2f(0.0, 1.0)
            glVertex3f(-quad_width + offset_x, -quad_height, -2)  # Bottom-left corner
            glTexCoord2f(1.0, 1.0)
            glVertex3f(quad_width + offset_x, -quad_height, -2)   # Bottom-right corner
            glTexCoord2f(1.0, 0.0)
            glVertex3f(quad_width + offset_x, quad_height, -2)    # Top-right corner
            glTexCoord2f(0.0, 0.0)
            glVertex3f(-quad_width + offset_x, quad_height, -2)   # Top-left corner

            glEnd()
            glBindTexture(GL_TEXTURE_2D, 0)  # Unbind the texture
        glDisable(GL_TEXTURE_2D)  # Disable texturing
        glEnable(GL_LIGHTING)

    def draw_score_bar(self):
        glPushMatrix()
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        glColor3f(0.8, 0.8, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(-0.95, 0.6)
        glVertex2f(-0.65, 0.6)
        glVertex2f(-0.65, 0.5)
        glVertex2f(-0.95, 0.5)
        glEnd()

        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(-0.95, 0.6)
        glVertex2f(-0.65, 0.6)
        glVertex2f(-0.65, 0.5)
        glVertex2f(-0.95, 0.5)
        glEnd()

        glColor3f(1.0, 1.0, 1.0)
        self.render_text("Progress :", -0.95, 0.65)

        if self.ball.x <= 15:
            progress = (self.ball.x - 1.2) / (15 - 1.2)
        else:
            progress = 1.0

        progress_height_adjustment = 0.005

        glColor3f(0.0, 0.5, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(-0.95, 0.6 - progress_height_adjustment)
        glVertex2f(-0.95 + 0.3 * progress, 0.6 - progress_height_adjustment)
        glVertex2f(-0.95 + 0.3 * progress, 0.5 + progress_height_adjustment)
        glVertex2f(-0.95, 0.5 + progress_height_adjustment)
        glEnd()

        glColor3f(1.0, 1.0, 1.0)
        self.render_text(f"Dist: {self.distance_traveled:.2f}", 0.55, 0.87)

        glColor3f(1.0, 1.0, 1.0)
        self.render_text(f"Highest: {self.high_score:.2f}", 0.55, 0.78)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
    def render_text(self, text, x, y):
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    def updateScene(self):
        if self.running:
            self.scene_x += self.ball.horizontal_speed  # Adjust the scene's horizontal movement
            self.distance_traveled += self.ball.horizontal_speed  # Update the distance traveled
            if self.scene_x > 15:  # Check if the ball has reached the end of the path
                self.reset_scene()  # Reset the scene
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if not self.running:
                self.running = True  # Start the scene on the first spacebar press
                self.waiting_for_start = False  # Set waiting_for_start to False
            if not self.game_over:
                self.ball.jump()
            else:
                self.restart_game()

    def reset_scene(self):
        self.scene_x = 0
        self.ball.reset()
        self.path.create()  # Recreate the path if needed

    def restart_game(self):
        self.running = False
        self.scene_x = 0
        self.distance_traveled = 0.0  # Reset distance traveled
        self.ball.reset()
        self.path.create()
        self.restart_button.hide()
        
        self.points_collected = 0  # Reset the points collected
        self.points_collected_label.setText(f'Points Collected: {self.points_collected}')
        
        self.game_over = False
        self.game_won = False  # Reset game_won state

        # Restart the music
        self.player.stop()
        self.playlist.setCurrentIndex(0)
        self.player.play()
        self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("3D Path with PyQt5")
        self.opengl_widget = OpenGLWidget(self)
        self.setCentralWidget(self.opengl_widget)
        self.resize(800, 600)
        self.opengl_widget.setFocus()

def main():
    glutInit()  # Initialize GLUT
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
