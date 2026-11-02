"""
NetTracer - Charts / Traffic Analytics View
Visualizes bandwidth trends and network telemetry metrics with numerical axes and live data.
"""

from collections import deque
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QLinearGradient, QFont

from gui.styles import (
    COLOR_CARD_DARK, COLOR_ACCENT, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED
)
from gui.widgets.icons import VectorIcons


class RealtimeBandwidthGraph(QWidget):
    """Real-time live bandwidth line chart with numerical Y-axis, time scale, and metrics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # 30 seconds history at 1s intervals
        self.dl_history = deque([1.2, 1.8, 2.4, 2.1, 2.8, 2.4, 3.1, 2.4, 2.0, 2.7, 2.4], maxlen=30)
        self.ul_history = deque([0.4, 0.6, 0.8, 0.5, 0.9, 0.8, 1.1, 0.8, 0.7, 0.9, 0.8], maxlen=30)

    def add_point(self, dl: float, ul: float):
        self.dl_history.append(dl)
        self.ul_history.append(ul)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = float(self.width())
        h = float(self.height())
        if w < 100 or h < 80:
            return

        # Margins for axes
        y_axis_w = 68.0
        x_axis_h = 24.0
        top_pad = 32.0
        right_pad = 16.0

        plot_w = w - y_axis_w - right_pad
        plot_h = h - top_pad - x_axis_h

        # Compute dynamic scale max (rounded to nice numbers: 1, 2, 5, 10...)
        raw_max = max(max(self.dl_history, default=1.0), max(self.ul_history, default=1.0), 1.0)
        if raw_max <= 2.0:
            max_val = 2.0
        elif raw_max <= 5.0:
            max_val = 5.0
        elif raw_max <= 10.0:
            max_val = 10.0
        elif raw_max <= 25.0:
            max_val = 25.0
        else:
            max_val = float(int(raw_max * 1.25) + 1)

        # 1. Top Badges / Legend with real live numbers
        curr_dl = self.dl_history[-1] if self.dl_history else 0.0
        curr_ul = self.ul_history[-1] if self.ul_history else 0.0
        peak = max(max(self.dl_history, default=0.0), max(self.ul_history, default=0.0))

        font_legend = QFont("Poppins", 9, QFont.Weight.Medium)
        painter.setFont(font_legend)

        # Download Legend
        painter.setBrush(QColor(COLOR_ACCENT))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(y_axis_w, 10, 8, 8))
        painter.setPen(QColor(COLOR_TEXT_MAIN))
        painter.drawText(QRectF(y_axis_w + 14, 5, 130, 20), Qt.AlignmentFlag.AlignVCenter, f"Download: {curr_dl:.1f} MB/s")

        # Upload Legend
        painter.setBrush(QColor(255, 255, 255, 180))
        painter.drawEllipse(QRectF(y_axis_w + 150, 10, 8, 8))
        painter.setPen(QColor(COLOR_TEXT_MUTED))
        painter.drawText(QRectF(y_axis_w + 164, 5, 130, 20), Qt.AlignmentFlag.AlignVCenter, f"Upload: {curr_ul:.1f} MB/s")

        # Peak indicator
        painter.setPen(QColor(COLOR_TEXT_MUTED))
        painter.drawText(QRectF(w - right_pad - 120, 5, 120, 20), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"Peak: {peak:.1f} MB/s")

        # 2. Draw Horizontal Grid Lines & Y-Axis Numerical Labels
        font_axis = QFont("Poppins", 8, QFont.Weight.Normal)
        painter.setFont(font_axis)

        grid_divisions = 4
        for i in range(grid_divisions + 1):
            fraction = i / float(grid_divisions)
            val = max_val * (1.0 - fraction)
            y = top_pad + fraction * plot_h

            # Grid Line
            painter.setPen(QPen(QColor(255, 255, 255, 14), 1, Qt.PenStyle.DashLine))
            painter.drawLine(int(y_axis_w), int(y), int(w - right_pad), int(y))

            # Y-Axis Label
            lbl_rect = QRectF(0, y - 8, y_axis_w - 10, 16)
            painter.setPen(QColor(COLOR_TEXT_MUTED))
            painter.drawText(lbl_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"{val:.1f} MB/s")

        # 3. Draw X-Axis Time Markers
        time_steps = [(-30, 0.0), (-20, 0.33), (-10, 0.66), (0, 1.0)]
        for sec, frac in time_steps:
            x = y_axis_w + frac * plot_w
            lbl = "now" if sec == 0 else f"{sec}s"
            txt_rect = QRectF(x - 25, top_pad + plot_h + 4, 50, 18)
            painter.drawText(txt_rect, Qt.AlignmentFlag.AlignCenter, lbl)

        # 4. Draw Download Curve with Mint Gradient Fill
        step_x = plot_w / max(1, len(self.dl_history) - 1)

        dl_path = QPainterPath()
        fill_path = QPainterPath()
        fill_path.moveTo(y_axis_w, top_pad + plot_h)

        for i, v in enumerate(self.dl_history):
            x = y_axis_w + i * step_x
            clamped_v = min(v, max_val)
            y = top_pad + plot_h - (clamped_v / max_val) * plot_h
            if i == 0:
                dl_path.moveTo(x, y)
                fill_path.lineTo(x, y)
            else:
                dl_path.lineTo(x, y)
                fill_path.lineTo(x, y)

        fill_path.lineTo(y_axis_w + (len(self.dl_history) - 1) * step_x, top_pad + plot_h)
        fill_path.closeSubpath()

        # Gradient fill
        grad = QLinearGradient(0, top_pad, 0, top_pad + plot_h)
        grad.setColorAt(0.0, QColor(0, 210, 138, 55))
        grad.setColorAt(1.0, QColor(0, 210, 138, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawPath(fill_path)

        # Line stroke
        painter.setPen(QPen(QColor(COLOR_ACCENT), 2.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(dl_path)

        # 5. Draw Upload Curve (Dashed White Line)
        ul_path = QPainterPath()
        for i, v in enumerate(self.ul_history):
            x = y_axis_w + i * step_x
            clamped_v = min(v, max_val)
            y = top_pad + plot_h - (clamped_v / max_val) * plot_h
            if i == 0:
                ul_path.moveTo(x, y)
            else:
                ul_path.lineTo(x, y)

        painter.setPen(QPen(QColor(255, 255, 255, 160), 2.0, Qt.PenStyle.DashLine))
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
        dash_layout.setContentsMargins(32, 24, 32, 24)
        dash_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dash_layout.setSpacing(10)

        # Vector presentation chart icon
        icon_lbl = QLabel()
        icon_lbl.setPixmap(VectorIcons.render_pixmap("presentation_chart", size=48, color=COLOR_TEXT_MUTED))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dash_layout.addWidget(icon_lbl)

        title_lbl = QLabel("Bandwidth Visualization")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 20px; font-weight: 700;")
        dash_layout.addWidget(title_lbl)

        desc_lbl = QLabel(
            "Interactive charts showing real-time network throughput across active processes."
        )
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_lbl.setWordWrap(True)
        desc_lbl.setMaximumWidth(480)
        desc_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px; line-height: 1.4;")
        dash_layout.addWidget(desc_lbl)

        dash_layout.addSpacing(6)

        # Embedded dynamic numerical realtime graph
        self.graph = RealtimeBandwidthGraph()
        dash_layout.addWidget(self.graph)

        card_layout.addWidget(dashed_box)
        main_layout.addWidget(card)

    def update_telemetry(self, dl: float, ul: float):
        self.graph.add_point(dl, ul)
