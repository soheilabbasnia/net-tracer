"""
NetTracer - Custom Animated Toggle Switch Widget
Interactive pill switch matching the prototype's toggles.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QPen

from gui.styles import COLOR_ACCENT, COLOR_BG_DARK, COLOR_TEXT_MUTED


class ToggleSwitch(QWidget):
    """Modern iOS/Tailwind-style pill toggle switch."""

    toggled = pyqtSignal(bool)

    def __init__(self, checked: bool = False, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 26)
        self._checked = checked
        self._thumb_position = 28.0 if checked else 4.0

        self._anim = QPropertyAnimation(self, b"thumb_position", self)
        self._anim.setDuration(160)

    @pyqtProperty(float)
    def thumb_position(self) -> float:
        return self._thumb_position

    @thumb_position.setter
    def thumb_position(self, pos: float):
        self._thumb_position = pos
        self.update()

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool):
        if self._checked != checked:
            self._checked = checked
            target = 28.0 if self._checked else 4.0
            self._anim.stop()
            self._anim.setStartValue(self._thumb_position)
            self._anim.setEndValue(target)
            self._anim.start()
            self.toggled.emit(self._checked)
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(0, 0, self.width(), self.height())
        radius = self.height() / 2.0

        if self._checked:
            # Active track (Mint Green)
            painter.setBrush(QColor(COLOR_ACCENT))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, radius, radius)

            # Active thumb (Dark knob)
            thumb_radius = 8.5
            thumb_rect = QRectF(self._thumb_position, (self.height() - thumb_radius * 2) / 2.0, thumb_radius * 2, thumb_radius * 2)
            painter.setBrush(QColor(COLOR_BG_DARK))
            painter.drawEllipse(thumb_rect)
        else:
            # Inactive track (Dark with subtle border)
            painter.setBrush(QColor(COLOR_BG_DARK))
            painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
            painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

            # Inactive thumb (Muted gray knob)
            thumb_radius = 8.5
            thumb_rect = QRectF(self._thumb_position, (self.height() - thumb_radius * 2) / 2.0, thumb_radius * 2, thumb_radius * 2)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(COLOR_TEXT_MUTED))
            painter.drawEllipse(thumb_rect)
