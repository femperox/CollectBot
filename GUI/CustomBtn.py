from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QAbstractButton

class PicButton(QAbstractButton):
    def __init__(self, pixmap, pixmap_hover, pixmap_pressed, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmap_hover = pixmap_hover
        self.pixmap_pressed = pixmap_pressed

        self.pressed.connect(self.update)
        self.released.connect(self.update)
        self.toggled.connect(self.update)


    def paintEvent(self, event):
        pix = self.pixmap_hover if self.underMouse() else self.pixmap
        if self.isDown():
            pix = self.pixmap_pressed
        if self.isEnabled() == 0:
            pix = self.pixmap_pressed

        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return QSize(217, 212)

    def changePicPressed(self, pic):
        self.pixmap_pressed = pic
        self.update()

    def changePicNormal(self,pic):
        self.pixmap = pic
        self.update()