import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLUT import *
from LEVEL3 import OpenGLWidget as Level3OpenGLWidget  
import math

class HardLevelWidget(QWidget):
    def __init__(self, central_widget, stacked_widget, parent=None):
        super(HardLevelWidget, self).__init__(parent)
        self.setWindowTitle("HARD")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = central_widget
        self.stacked_widget = stacked_widget
        
        self.opengl_widget = Level3OpenGLWidget(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.opengl_widget)
        self.setLayout(layout)

        self.back_button = QPushButton("Back", self)
        self.back_button.setGeometry(23, 20, 90, 40)
        self.back_button.clicked.connect(self.on_back_button_click)
        
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: black;
                border: 2px solid black;  /* Black border */
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6692;
            }
        """)
        
    def on_back_button_click(self):
        self.central_widget.show()  
        self.stacked_widget.hide() 

if __name__ == "__main__":
    glutInit()  
    app = QApplication(sys.argv)
    window = HardLevelWidget(None, None)  
    window.show()
    sys.exit(app.exec_())
