import sys
import os
from OpenGL.GLUT import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPainter, QLinearGradient, QColor, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from introduction import GLWidget as IntroductionWidget
from how_to import OpenGLContent as HowToWidget
from score import ScoreWidget  
from live import LiveWidget

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

class GradientBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel("MY BALL GAME", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(""" 
            color: white; 
            font-size: 24px; 
            font-weight: bold; 
            font-family: 'Arial';
        """)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(255, 0, 0))
        gradient.setColorAt(1, QColor(255, 165, 0))
        painter.fillRect(self.rect(), gradient)
        super().paintEvent(event)

class MyGameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My OpenGL and PyQt5 Game")
        self.setGeometry(100, 100, 800, 600)

        self.background_widget = BackgroundWidget(r"D:\fcg2024\Tutorial\FCG-2024_Mini Project\IMAGES_VIDEOS\main_background.png")
        self.setCentralWidget(self.background_widget)

        self.central_widget = QWidget(self.background_widget)
        self.central_layout = QVBoxLayout(self.background_widget)
        self.central_layout.addWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.gradient_box = GradientBox(self.central_widget)
        self.gradient_box.setFixedHeight(60)
        self.layout.addWidget(self.gradient_box)

        self.button_container = QWidget(self.central_widget)
        self.button_layout = QVBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(10)

        self.center_layout = QVBoxLayout()
        self.center_layout.addWidget(self.button_container)
        self.center_layout.setAlignment(Qt.AlignCenter)
        self.layout.addLayout(self.center_layout)

        self.buttons_info = [
            ("INTRO", IntroductionWidget),
            ("HOW TO", HowToWidget),
            ("SCORE", ScoreWidget),
            ("LIVE", LiveWidget),
            ("QUIT", None)
        ]

        self.widgets = {}
        self.buttons = []
        for name, widget_class in self.buttons_info:
            button = QPushButton(name, self.button_container)
            button.clicked.connect(lambda checked, wc=widget_class: self.on_button_click(wc))
            button.setStyleSheet(self.button_style())
            self.button_layout.addWidget(button)
            self.buttons.append(button)

        self.setup_background_music()

    def setup_background_music(self):
        self.player = QMediaPlayer()
        file_path = r"D:\fcg2024\Tutorial\FCG-2024_Mini Project\IMAGES_VIDEOS\main_music.mp3"
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        
        media = QMediaContent(QUrl.fromLocalFile(file_path))
        self.player.setMedia(media)
        self.player.setVolume(50)
        self.player.mediaStatusChanged.connect(self.handle_media_status_changed)
        self.player.play()

    def handle_media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.player.play()

    def on_button_click(self, widget_class):
        if widget_class is None:
            self.close()
            return

        if not hasattr(self, 'stacked_widget'):
            self.stacked_widget = QStackedWidget(self.central_widget)
            self.main_content_layout = QHBoxLayout()
            self.layout.addLayout(self.main_content_layout)
            self.main_content_layout.addWidget(self.button_container)
            self.main_content_layout.addWidget(self.stacked_widget)

        if widget_class not in self.widgets:
            widget = widget_class(self.stacked_widget)
            self.widgets[widget_class] = widget
            self.stacked_widget.addWidget(widget)

        self.stacked_widget.setCurrentWidget(self.widgets[widget_class])

        if hasattr(self, 'center_layout'):
            self.layout.removeItem(self.center_layout)
            self.center_layout = None

        # Start the video update timer if the IntroductionWidget is displayed
        if widget_class == IntroductionWidget:
            self.widgets[widget_class].start_video_timer()

        # Control music based on the button clicked
        if widget_class == LiveWidget:
            self.player.pause()
        else:
            if self.player.state() == QMediaPlayer.PausedState:
                self.player.play()

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

def main():
    glutInit()
    app = QApplication(sys.argv)
    window = MyGameWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
