"""
NetTracer - Charts / Traffic Analytics View
Visualizes bandwidth trends and network telemetry metrics.
"""

from collections import deque
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QLinearGradient

from gui.styles import (
    COLOR_CARD_DARK, COLOR_ACCENT, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED
)
from gui.widgets.icons import VectorIcons


class RealtimeBandwidthGraph(QWidget):
    """Real-time live bandwidth line chart with gradient area fill."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.dl_history = deque([1.2, 1.8, 2.4, 2.1, 2.8, 2.4, 3.1, 2.4, 2.0, 2.7, 2.4], maxlen=40)
        self.ul_history = deque([0.4, 0.6, 0.8, 0.5, 0.9, 0.8, 1.1, 0.8, 0.7, 0.9, 0.8], maxlen=40)

    def add_point(self, dl: float, ul: float):
        self.dl_history.append(dl)
        self.ul_history.append(ul)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        if w < 20 or h < 20:
            return

        max_val = max(max(self.dl_history, default=1.0), max(self.ul_history, default=1.0), 3.5)

        # Subtle grid horizontal lines
        painter.setPen(QPen(QColor(255, 255, 255, 12), 1, Qt.PenStyle.DashLine))
        for frac in (0.25, 0.5, 0.75):
            y = int(h * frac)
            painter.drawLine(0, y, int(w), y)

        step_x = w / max(1, len(self.dl_history) - 1)

        # 1. Download Path (Mint Green) with subtle gradient fill
        dl_path = QPainterPath()
        fill_path = QPainterPath()
        fill_path.moveTo(0, h)

        for i, val in enumerate(self.dl_history):
            x = i * step_x
            y = h - (val / max_val) * (h - 24) - 12
            if i == 0:
                dl_path.moveTo(x, y)
                fill_path.lineTo(x, y)
            else:
                dl_path.lineTo(x, y)
                fill_path.lineTo(x, y)

        fill_path.lineTo(w, h)
        fill_path.closeSubpath()

        # Gradient area fill
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor(0, 210, 138, 45))
        grad.setColorAt(1.0, QColor(0, 210, 138, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawPath(fill_path)

        # Stroke line
        painter.setPen(QPen(QColor(COLOR_ACCENT), 2.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(dl_path)

        # 2. Upload Path (Muted White)
        ul_path = QPainterPath()
        for i, val in enumerate(self.ul_history):
            x = i * step_x
            y = h - (val / max_val) * (h - 24) - 12
            if i == 0:
                ul_path.moveTo(x, y)
            else:
                ul_path.lineTo(x, y)

        painter.setPen(QPen(QColor(255, 255, 255, 140), 1.8, Qt.PenStyle.DashLine))
        painter.drawPath(ul_path)
        painter.end()


class ChartsView(QWidget):
    """Charts tab matching the mockup presentation card."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
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

        # Header: TRAFFIC ANALYTICS with vector icon
        header_row = QHBoxLayout()
        header_icon = QLabel()
        header_icon.setPixmap(VectorIcons.render_pixmap("charts", size=16, color=COLOR_ACCENT))
        header_icon.setStyleSheet("border: none; background: transparent;")
        header_lbl = QLabel("TRAFFIC ANALYTICS")
        header_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-weight: 700; letter-spacing: 1.2px; border: none; background: transparent;")
        header_row.addWidget(header_icon)
        header_row.addWidget(header_lbl)
        header_row.addStretch()
        card_layout.addLayout(header_row)

        # Dashed container box - correctly scoped so borders don't leak into children!
        dashed_box = QFrame()
        dashed_box.setObjectName("DashedBox")
        dashed_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        dashed_box.setStyleSheet("""
            QFrame#DashedBox {
                background-color: rgba(31, 32, 36, 0.4);
                border: 2px dashed rgba(255, 255, 255, 0.1);
                border-radius: 28px;
            }
            QFrame#DashedBox QLabel {
                border: none;
                background: transparent;
            }
        """)

        dash_layout = QVBoxLayout(dashed_box)
        dash_layout.setContentsMargins(40, 36, 40, 36)
        dash_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dash_layout.setSpacing(14)

        # Vector presentation chart icon
        icon_lbl = QLabel()
        icon_lbl.setPixmap(VectorIcons.render_pixmap("presentation_chart", size=54, color=COLOR_TEXT_MUTED))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
