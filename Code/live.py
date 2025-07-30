import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QStackedWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from OpenGL.GLUT import *

from level_easy import EasyLevelWidget  
from level_medium import MediumLevelWidget
from level_hard import HardLevelWidget

class BackgroundWidget(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.image = QPixmap(self.image_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        scaled_image = self.image.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        x = (self.width() - scaled_image.width()) // 2
        y = (self.height() - scaled_image.height()) // 2
        painter.drawPixmap(x, y, scaled_image)
        super().paintEvent(event)

class LiveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("GAME LEVEL")
        self.setGeometry(100, 100, 800, 600)
        
        self.background_widget = BackgroundWidget(r"D:\fcg2024\Tutorial\FCG-2024_Mini Project\IMAGES_VIDEOS\live_background.png")
        layout = QVBoxLayout(self)
        layout.addWidget(self.background_widget)
        self.setLayout(layout)

        self.central_widget = QWidget(self.background_widget)
        self.central_layout = QVBoxLayout(self.background_widget)
        self.central_layout.addWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.label_title = QLabel("GAME LEVEL", self.central_widget)
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_title.setStyleSheet(""" 
            color: white; 
            font-size: 48px; 
            font-weight: bold; 
            font-family: 'Arial';
            margin-top: 10px; /* Added margin for spacing from top */
        """)
        self.layout.addWidget(self.label_title, alignment=Qt.AlignTop) 

        self.button_container = QWidget(self.central_widget)
        self.button_container.setGeometry(0, 0, 800, 600)  

        self.buttons_info = [
            ("HARD", HardLevelWidget, 440, 100),
            ("MEDIUM", MediumLevelWidget, 240, 200),
            ("EASY", EasyLevelWidget, 40, 300),
        ]

        self.widgets = {}
        self.buttons = []
        for name, widget_class, x, y in self.buttons_info:
            button = QPushButton(name, self.button_container)
            button.setGeometry(x, y, 150, 70)
            button.clicked.connect(lambda checked, wc=widget_class: self.on_button_click(wc))
            button.setStyleSheet(self.button_style())
            self.apply_shadow(button)
            self.buttons.append(button)

    def on_button_click(self, widget_class):
        self.central_widget.hide()

        if not hasattr(self, 'stacked_widget'):
            self.stacked_widget = QStackedWidget(self.background_widget)
            self.stacked_widget.setGeometry(0, 0, 800, 600)  
            self.central_layout.addWidget(self.stacked_widget)
            self.stacked_widget.lower()  

        if widget_class not in self.widgets:
            widget = widget_class(self.central_widget, self.stacked_widget)
            self.widgets[widget_class] = widget
            self.stacked_widget.addWidget(widget)

        self.stacked_widget.setCurrentWidget(self.widgets[widget_class])
        self.stacked_widget.show()

    def button_style(self):
        return """
        QPushButton {
            background-color: rgba(173, 216, 230, 0.9); 
            border: 2px solid #4682B4;
            border-radius: 15px;
            color: black; 
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
            margin: 5px;
        }
        QPushButton:hover {
            background-color: rgba(135, 206, 250, 1.0);
        }
        QPushButton:pressed {
            background-color: rgba(70, 130, 180, 1.0);
        }
        """

    def apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(5)
        shadow.setYOffset(5)
        shadow.setColor(Qt.black)
        widget.setGraphicsEffect(shadow)

class MyGameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GAME INTERFACE LEVEL")
        self.setGeometry(100, 100, 800, 600)

        self.live_widget = LiveWidget(self)
        self.setCentralWidget(self.live_widget)

def main():
    glutInit()  
    app = QApplication(sys.argv)
    window = MyGameWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
