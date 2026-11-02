"""
NetTracer - Custom Circular Progress Ring Widget
Renders animated/static circular percentage progress indicators with app labels.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

from gui.styles import COLOR_ACCENT, COLOR_PROGRESS_BG, COLOR_CARD_DARK, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED


class CircularProgressRing(QWidget):
    """Circular ring progress widget matching the 'Top Consumers' style."""

    def __init__(self, app_name: str = "App", percentage: int = 50, parent=None):
        super().__init__(parent)
        self.app_name = app_name
        self._percentage = max(0, min(100, percentage))
        self.setFixedSize(68, 76)

    @property
    def percentage(self) -> int:
        return self._percentage

    @percentage.setter
    def percentage(self, value: int):
        self._percentage = max(0, min(100, int(value)))
        self.update()

    def set_data(self, app_name: str, percentage: int):
        self.app_name = app_name
        self.percentage = percentage

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        ring_size = 48.0
        x = (self.width() - ring_size) / 2.0
        y = 2.0
        rect = QRectF(x, y, ring_size, ring_size)

        pen_width = 4.0
        adjusted_rect = rect.adjusted(pen_width / 2, pen_width / 2, -pen_width / 2, -pen_width / 2)

        # 1. Background Track Arc
        bg_pen = QPen(QColor(COLOR_PROGRESS_BG), pen_width, Qt.PenStyle.SolidLine)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(adjusted_rect, 0, 360 * 16)

        # 2. Active Accent Arc
        if self._percentage > 0:
            accent_pen = QPen(QColor(COLOR_ACCENT), pen_width, Qt.PenStyle.SolidLine)
            accent_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(accent_pen)
            # Qt angles are in 1/16th of a degree; 90 degrees starts from top (12 o'clock)
            start_angle = 90 * 16
            span_angle = -int((self._percentage / 100.0) * 360 * 16)
            painter.drawArc(adjusted_rect, start_angle, span_angle)

        # 3. Inner Center Percentage Text
        painter.setPen(QColor(COLOR_TEXT_MAIN))
        font_pct = QFont("Poppins", 8, QFont.Weight.DemiBold)
        painter.setFont(font_pct)
        painter.drawText(adjusted_rect, Qt.AlignmentFlag.AlignCenter, f"{self._percentage}%")

        # 4. App Name Label Below Ring
        label_rect = QRectF(0, ring_size + 6, self.width(), 18)
        painter.setPen(QColor(COLOR_TEXT_MUTED))
        font_label = QFont("Poppins", 8, QFont.Weight.Normal)
        painter.setFont(font_label)
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, self.app_name)
