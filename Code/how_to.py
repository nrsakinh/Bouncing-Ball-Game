from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
from PyQt5 import QtWidgets
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from PIL import Image
import numpy as np

class OpenGLContent(QWidget):
    def __init__(self, parent=None):
        super(OpenGLContent, self).__init__(parent)
        self.glWidget = GLWidget(self)
        self.initUI()

    def initUI(self):
        self.vbox = QVBoxLayout(self)
        self.hbox = QHBoxLayout()

        self.nextButton = QPushButton("Next", self)
        self.nextButton.setStyleSheet(self.button_style())
        self.nextButton.clicked.connect(self.glWidget.nextFace)
        
        self.hbox.addStretch()
        self.hbox.addWidget(self.nextButton)

        self.vbox.addWidget(self.glWidget)
        self.vbox.addLayout(self.hbox)

    def button_style(self):
        return """
        QPushButton {
            background-color: #FF4500;
            border: 2px solid #8B0000;
            border-radius: 15px;
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            margin: 5px;
        }
        QPushButton:hover {
            background-color: #FF6347;
        }
        QPushButton:pressed {
            background-color: #FF0000;
        }
        """

class GLWidget(QGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.angle = 0
        self.zoom = 8
        self.stop_animation = False
        self.rotating = False
        self.target_angle = 0
        self.current_face = 0
        self.textures = []
        
    def initializeGL(self):
        glutInit(sys.argv)  
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        
        glEnable(GL_TEXTURE_2D)
        self.loadTextures()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, 4.0 / 3.0, 1, 100)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(8, 8, 8, 0, 0, 0, 0, 1, 0)

    def loadTextures(self):
        texture_files = [
            r"D:\fcg2024\Tutorial\FCG-2024_Mini Project\IMAGES_VIDEOS\1.png",
            r"D:\fcg2024\Tutorial\FCG-2024_Mini Project\IMAGES_VIDEOS\2.png",
            r"D:\fcg2024\Tutorial\FCG-2024_Mini Project\IMAGES_VIDEOS\3.png",
            r"D:\fcg2024\Tutorial\FCG-2024_Mini Project\IMAGES_VIDEOS\4.png",
            r"D:\fcg2024\Tutorial\FCG-2024_Mini Project\IMAGES_VIDEOS\5.png",
            r"D:\fcg2024\Tutorial\FCG-2024_Mini Project\IMAGES_VIDEOS\6.png"
        ]
        self.textures = glGenTextures(len(texture_files))

        for i, texture_file in enumerate(texture_files):
            glBindTexture(GL_TEXTURE_2D, self.textures[i])
            
            # Load image
            image = Image.open(texture_file)
            image = image.convert("RGB")  
            
            # Convert image to texture
            img_data = np.array(image).tobytes()
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)  

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        gluLookAt(0, 0, self.zoom, 0, 0, 0, 0, 1, 0)
        
        glRotatef(self.angle, 0, 1, 0)
        
        vertices = [
            [-2.0, -2.0, -2.0],
            [ 2.0, -2.0, -2.0],
            [ 2.0,  2.0, -2.0],
            [-2.0,  2.0, -2.0],
            [-2.0, -2.0,  2.0],
            [ 2.0, -2.0,  2.0],
            [ 2.0,  2.0,  2.0],
            [-2.0,  2.0,  2.0]
        ]
        
        faces = [
            [0, 1, 2, 3],  # back face
            [4, 5, 6, 7],  # front face
            [0, 1, 5, 4],  # bottom face
            [2, 3, 7, 6],  # top face
            [0, 3, 7, 4],  # left face
            [1, 2, 6, 5]   # right face
        ]
        
        normals = [
            [ 0,  0, -1],  # back face
            [ 0,  0,  1],  # front face
            [ 0, -1,  0],  # bottom face
            [ 0,  1,  0],  # top face
            [-1,  0,  0],  # left face
            [ 1,  0,  0]   # right face
        ]
        
        tex_coords = [
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0]
        ]
        
        for i in range(6):
            glBindTexture(GL_TEXTURE_2D, self.textures[i])
            self.drawFace(vertices, faces[i], tex_coords, normals[i])
        
        glFlush()

    def drawFace(self, vertices, face, tex_coords, normal):
        glBegin(GL_QUADS)
        glNormal3fv(normal)
        for i, vertex in enumerate(face):
            glTexCoord2fv(tex_coords[i])
            glVertex3fv(vertices[vertex])
        glEnd()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, w / h, 1, 100)
        glMatrixMode(GL_MODELVIEW)

    def nextFace(self):
        self.target_angle += 90
        self.current_face = (self.current_face + 1) % 6  
        self.rotating = True
        self.zoom = 8  
        self.stop_animation = False  
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self.rotateToNextFace)
        self.rotation_timer.start(30)

    def rotateToNextFace(self):
        if self.angle < self.target_angle:
            self.angle += 5
            if self.angle >= self.target_angle:
                self.angle = self.target_angle
                self.rotating = False
                self.rotation_timer.stop()
                self.animateZoomIn()
            self.update()
        else:
            self.rotating = False
            self.rotation_timer.stop()
            self.animateZoomIn()

    def animateZoomIn(self):
        self.zoom_timer = QTimer(self)
        self.zoom_timer.timeout.connect(self.zoomIn)
        self.zoom_timer.start(30)

    def zoomIn(self):
        if self.zoom > 4:
            self.zoom -= 0.2
            self.update()
        else:
            self.zoom_timer.stop()
            self.stop_animation = True
            self.update()

class BasicWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(BasicWindow, self).__init__()
        self.setWindowTitle("How To Window")
        self.setGeometry(100, 100, 800, 600)

        self.content = OpenGLContent(self)
        self.setCentralWidget(self.content)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = BasicWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
