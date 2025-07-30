import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QFont, QPainterPath, QColor, QFontMetrics
from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy

class BackgroundWidget(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = QPixmap(self.image_path)
        painter.drawPixmap(self.rect(), pixmap)
        
class OutlinedLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.outline_color = Qt.black
        self.outline_thickness = 2.4

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        font = self.font()
        text = self.text()
        
        fm = QFontMetrics(font)
        text_rect = fm.boundingRect(self.rect(), self.alignment(), text)
        
        x_offset = (self.rect().width() - text_rect.width()) / 2
        y_offset = (self.rect().height() + text_rect.height()) / 2 - fm.descent()
        
        path = QPainterPath()
        path.addText(x_offset, y_offset, font, text)
        
        painter.setPen(QPen(self.outline_color, self.outline_thickness, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
        
        painter.setPen(QPen(self.palette().text(), 0))
        painter.setBrush(self.palette().text())
        painter.drawText(self.rect(), self.alignment(), text)

class TitleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title_label = OutlinedLabel("GAME SCORING", self)
        self.title_label.setFont(QFont("Arial", 30, QFont.Bold))
        self.title_label.setStyleSheet("color: #FFFFFF;")

        self.title_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.setAlignment(Qt.AlignCenter)  
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.setFixedSize(400, 70)  

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(Qt.black, 4)
        painter.setPen(pen)
        
        purple = QColor(128, 0, 128) 
        gradient = QBrush(purple)
        painter.setBrush(gradient)

        rect = QRectF(0, 0, self.width(), self.height())
        painter.drawRoundedRect(rect, 15, 15)

class LevelWidget(QWidget):
    def __init__(self, level_text, score, points, parent=None):
        super().__init__(parent)
        
        self.level_label = OutlinedLabel(level_text, self)
        self.level_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.level_label.setStyleSheet("color: #FFFFFF;")
        self.level_label.setAlignment(Qt.AlignCenter)

        self.score_label = OutlinedLabel(f"Score: {score}", self)
        self.score_label.setFont(QFont("Arial", 18))
        self.score_label.setStyleSheet("color: #FFFFFF;")
        self.score_label.setAlignment(Qt.AlignCenter)

        self.stars_label = OutlinedLabel("", self)
        self.stars_label.setFont(QFont("Arial", 30))
        self.stars_label.setStyleSheet("color: #FFD700;")
        self.stars_label.setAlignment(Qt.AlignCenter)
        self.update_stars(points)

        layout = QVBoxLayout()
        layout.addWidget(self.level_label)
        layout.addWidget(self.score_label)
        layout.addWidget(self.stars_label)
        
        spacer_item = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer_item)
        
        layout.setContentsMargins(10, 20, 10, 10)
        self.setLayout(layout)

        self.setFixedSize(220, 150)
    def update_stars(self, points):
        stars = '★' * (points // 10) + '☆' * (3 - (points // 10))
        self.stars_label.setText(stars)

    def update_score(self, score):
        self.score_label.setText(f"Score: {score}")

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
        
        custom_blue = QColor(17, 99, 190)  
        gradient = QBrush(custom_blue)
        painter.setBrush(gradient)

        rect = QRectF(0, 0, self.width(), self.height())
        painter.drawRoundedRect(rect, 10, 10)

def read_score(file_path):
    try:
        with open(file_path, 'r') as file:
            score = file.readline().strip()
            return score
    except Exception as e:
        return "N/A"

def read_points(file_path):
    try:
        with open(file_path, 'r') as file:
            points = int(file.readline().strip())
            return points
    except Exception as e:
        return 0

class ScoreWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(800, 600)  

        self.background_widget = BackgroundWidget(r"D:\fcg2024\Tutorial\FCG-2024_Mini Project\IMAGES_VIDEOS\score_background.png")
        self.background_layout = QVBoxLayout(self)
        self.background_layout.addWidget(self.background_widget)
        self.setLayout(self.background_layout)

        self.title_widget = TitleWidget(self)
        self.title_widget.setFixedWidth(400)  

        self.title_layout = QVBoxLayout()
        self.title_layout.addWidget(self.title_widget, alignment=Qt.AlignCenter)  
        self.title_layout.setContentsMargins(100, 80, 50, 0)  
        self.title_layout.setAlignment(Qt.AlignTop)

        self.level1_widget = LevelWidget("LEVEL 1", "", 0, self)
        self.level2_widget = LevelWidget("LEVEL 2", "", 0, self)
        self.level3_widget = LevelWidget("LEVEL 3", "", 0, self)

        self.levels_layout = QHBoxLayout()
        self.levels_layout.addWidget(self.level1_widget)
        self.levels_layout.addWidget(self.level2_widget)
        self.levels_layout.addWidget(self.level3_widget)
        self.levels_layout.setAlignment(Qt.AlignCenter)
        self.levels_layout.setContentsMargins(50, 55, 0, 0)  

        self.overlay_widget = QWidget(self)
        self.overlay_layout = QVBoxLayout(self.overlay_widget)
        self.overlay_layout.addLayout(self.title_layout)
        self.overlay_layout.addLayout(self.levels_layout)
        self.overlay_layout.setContentsMargins(0, 0, 0, 20)  
        self.overlay_widget.setLayout(self.overlay_layout)

        self.overlay_widget.setParent(self.background_widget)
        self.overlay_widget.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_scores_and_points)
        self.timer.start(1000)  

        self.refresh_scores_and_points()

    def refresh_scores_and_points(self):
        score1 = read_score('high_score.txt')
        score2 = read_score('high_score_lv2.txt')
        score3 = read_score('high_score_lv3.txt')

        points1 = read_points('points_collected.txt')
        points2 = read_points('points_collected_lv2.txt')
        points3 = read_points('points_collected_lv3.txt')

        self.level1_widget.update_score(score1)
        self.level1_widget.update_stars(points1)
        self.level2_widget.update_score(score2)
        self.level2_widget.update_stars(points2)
        self.level3_widget.update_score(score3)
        self.level3_widget.update_stars(points3)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScoreWidget()
    window.show()
    sys.exit(app.exec_())
