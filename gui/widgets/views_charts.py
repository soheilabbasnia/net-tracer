"""
NetTracer - Charts / Traffic Analytics View
Visualizes bandwidth trends and network telemetry metrics.
"""

from collections import deque
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath

from gui.styles import (
    COLOR_CARD_DARK, COLOR_CARD_DARKER, COLOR_ACCENT,
    COLOR_TEXT_MAIN, COLOR_TEXT_MUTED
)


class RealtimeBandwidthGraph(QWidget):
    """Real-time live bandwidth line chart drawn natively with QPainter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self.dl_history = deque([1.2, 1.8, 2.4, 2.1, 2.8, 2.4, 3.1, 2.4, 2.0, 2.7, 2.4], maxlen=30)
        self.ul_history = deque([0.4, 0.6, 0.8, 0.5, 0.9, 0.8, 1.1, 0.8, 0.7, 0.9, 0.8], maxlen=30)

    def add_point(self, dl: float, ul: float):
        self.dl_history.append(dl)
        self.ul_history.append(ul)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        if w < 10 or h < 10:
            return

        max_val = max(max(self.dl_history, default=1.0), 4.0)

        # Draw grid lines
        painter.setPen(QPen(QColor(255, 255, 255, 12), 1, Qt.PenStyle.DashLine))
        painter.drawLine(0, int(h * 0.25), w, int(h * 0.25))
        painter.drawLine(0, int(h * 0.50), w, int(h * 0.50))
        painter.drawLine(0, int(h * 0.75), w, int(h * 0.75))

        step_x = w / max(1, len(self.dl_history) - 1)

        # 1. Download Path (Mint Green)
        dl_path = QPainterPath()
        for i, val in enumerate(self.dl_history):
            x = i * step_x
            y = h - (val / max_val) * (h - 20) - 10
            if i == 0:
                dl_path.moveTo(x, y)
            else:
                dl_path.lineTo(x, y)

        painter.setPen(QPen(QColor(COLOR_ACCENT), 2.5))
        painter.drawPath(dl_path)

        # 2. Upload Path (White)
        ul_path = QPainterPath()
        for i, val in enumerate(self.ul_history):
            x = i * step_x
            y = h - (val / max_val) * (h - 20) - 10
            if i == 0:
                ul_path.moveTo(x, y)
            else:
                ul_path.lineTo(x, y)

        painter.setPen(QPen(QColor(255, 255, 255, 180), 2, Qt.PenStyle.DashLine))
        painter.drawPath(ul_path)


class ChartsView(QWidget):
    """Charts tab matching the mockup presentation card."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame#ChartsCard {{
                background-color: {COLOR_CARD_DARK};
                border-radius: 36px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
        """)
        card.setObjectName("ChartsCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 28, 32, 28)
        card_layout.setSpacing(20)

        # Header: TRAFFIC ANALYTICS
        header_lbl = QLabel("📈 TRAFFIC ANALYTICS")
        header_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-weight: 700; letter-spacing: 1.2px;")
        card_layout.addWidget(header_lbl)

        # Dashed container box matching screenshot
        dashed_box = QFrame()
        dashed_box.setStyleSheet(f"""
            background-color: rgba(31, 32, 36, 0.4);
            border: 2px dashed rgba(255, 255, 255, 0.1);
            border-radius: 28px;
        """)

        dash_layout = QVBoxLayout(dashed_box)
        dash_layout.setContentsMargins(40, 36, 40, 36)
        dash_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dash_layout.setSpacing(14)

        icon_lbl = QLabel("📊")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 54px; opacity: 0.5;")
        dash_layout.addWidget(icon_lbl)

        title_lbl = QLabel("Bandwidth Visualization")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 22px; font-weight: 700;")
        dash_layout.addWidget(title_lbl)

        desc_lbl = QLabel(
            "Interactive charts will be rendered here. Shows daily and weekly bandwidth trends across all monitored processes."
        )
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_lbl.setWordWrap(True)
        desc_lbl.setMaximumWidth(460)
        desc_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px; line-height: 1.5;")
        dash_layout.addWidget(desc_lbl)

        dash_layout.addSpacing(10)

        # Embedded dynamic realtime graph
        self.graph = RealtimeBandwidthGraph()
        dash_layout.addWidget(self.graph)

        card_layout.addWidget(dashed_box)
        main_layout.addWidget(card)

    def update_telemetry(self, dl: float, ul: float):
        self.graph.add_point(dl, ul)
