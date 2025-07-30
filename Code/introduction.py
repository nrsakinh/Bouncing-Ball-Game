from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtOpenGL import QGLWidget
import cv2

class GLWidget(QGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.cap = cv2.VideoCapture(r"D:\fcg2024\Tutorial\FCG-2024_Mini Project\IMAGES_VIDEOS\welcome_video.mp4")
        if not self.cap.isOpened():
            print("Error: Could not open video.")
            sys.exit()
        self.frame = None
        self.texture_id = None
        self.timer = QtCore.QTimer(self)

    def initializeGL(self):
        glutInit(sys.argv)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        self.texture_id = glGenTextures(1)

    def update_frame(self):
        ret, self.frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, self.frame = self.cap.read()
        self.update()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        if self.frame is not None:
            self.draw_background_video()
        glFlush()

    def draw_background_video(self):
        frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.flip(frame_rgb, 0)
        height, width, _ = frame_rgb.shape

        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, frame_rgb)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(-1.0, -1.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(1.0, -1.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(1.0, 1.0)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(-1.0, 1.0)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(-1.0, 1.0, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def closeEvent(self, event):
        self.cap.release()
        super(GLWidget, self).closeEvent(event)

    def start_video_timer(self):
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
