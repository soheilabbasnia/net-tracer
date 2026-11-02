"""
NetTracer - Left Sidebar Widget
Renders profile card, interface metrics, circular progress consumers, and action buttons.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath, QIcon

from gui.styles import (
    COLOR_CARD_DARK, COLOR_CARD_DARKER, COLOR_ACCENT, COLOR_ACCENT_HOVER,
    COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, COLOR_PROGRESS_BG, COLOR_BG_DARK
)
from gui.widgets.circular_progress import CircularProgressRing
from gui.widgets.icons import VectorIcons


class PillButton(QPushButton):
    """Pill action button with guaranteed mathematical half-circle round edges.
    Completely immune to Qt QSS engine border-radius bugs or Linux desktop styles."""

    def __init__(self, text: str, icon_name: str, fill_icon: bool = False, parent=None):
        super().__init__(parent)
        self.btn_text = text
        self.icon_name = icon_name
        self.fill_icon = fill_icon
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setStyleSheet("border: none; background: transparent;")

    def setText(self, text: str):
        self.btn_text = text
        self.update()

    def setIconName(self, icon_name: str, fill: bool = False):
        self.icon_name = icon_name
        self.fill_icon = fill
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = float(self.width())
        h = float(self.height())
        rect = QRectF(0, 0, w, h)
        radius = h / 2.0  # Exact half-circle pill edges

        if self.isDown():
            bg_color = QColor("#00b074")
        elif self.underMouse():
            bg_color = QColor(COLOR_ACCENT_HOVER)
        else:
            bg_color = QColor(COLOR_ACCENT)

        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        # Draw centered icon + text
        painter.setFont(QFont("Poppins", 10, QFont.Weight.Bold))
        text_w = painter.fontMetrics().horizontalAdvance(self.btn_text)
        icon_size = 16
        spacing = 6
        total_w = icon_size + spacing + text_w
        start_x = (w - total_w) / 2.0
        start_y = (h - icon_size) / 2.0

        if self.icon_name:
            pix = VectorIcons.render_pixmap(self.icon_name, size=icon_size, color=COLOR_BG_DARK, fill=self.fill_icon)
            painter.drawPixmap(int(start_x), int(start_y), pix)

        text_rect = QRectF(start_x + icon_size + spacing, 0, text_w + 4, h)
        painter.setPen(QColor(COLOR_BG_DARK))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.btn_text)
        painter.end()


class ActivityAvatar(QWidget):
    """Circular ECG pulse icon matching the HTML activity avatar."""

    def __init__(self, size: int = 86, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(2, 2, self.width() - 4, self.height() - 4)

        # Background circle
        painter.setBrush(QColor(COLOR_CARD_DARKER))
        painter.setPen(QPen(QColor(COLOR_PROGRESS_BG), 1.5))
        painter.drawEllipse(rect)

        # Draw ECG / Activity pulse path in accent green
        painter.setPen(QPen(QColor(COLOR_ACCENT), 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        cx = self.width() / 2.0
        cy = self.height() / 2.0

        path = QPainterPath()
        path.moveTo(cx - 24, cy)
        path.lineTo(cx - 14, cy)
        path.lineTo(cx - 8, cy - 14)
        path.lineTo(cx + 2, cy + 16)
        path.lineTo(cx + 10, cy - 8)
        path.lineTo(cx + 16, cy)
        path.lineTo(cx + 24, cy)

        painter.drawPath(path)
        painter.end()


class SidebarWidget(QFrame):
    """Left sidebar widget of NetTracer."""

    suspend_clicked = pyqtSignal(bool)
    export_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._is_suspended = False

        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            QFrame#SidebarFrame {{
                background-color: {COLOR_CARD_DARK};
                border-radius: 36px;
                border: 1px solid rgba(255, 255, 255, 0.04);
            }}
        """)
        self.setObjectName("SidebarFrame")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 26, 22, 24)
        layout.setSpacing(0)

        # Header / Avatar Area
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.avatar = ActivityAvatar(84)
        header_layout.addWidget(self.avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        header_layout.addSpacing(14)

        # Title: NetTracer
        title_lbl = QLabel()
        title_lbl.setTextFormat(Qt.TextFormat.RichText)
        title_lbl.setText(f'<span style="color:{COLOR_TEXT_MAIN}; font-size:24px; font-weight:700;">Net</span><span style="color:{COLOR_ACCENT}; font-size:24px; font-weight:700;">Tracer</span>')
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_lbl)

        # Subtitle: Status badge
        self.status_lbl = QLabel("LIVE DAEMON ACTIVE | ROOT")
        self.status_lbl.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 10px; font-weight: 700; letter-spacing: 1.5px;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.status_lbl)

        layout.addLayout(header_layout)
        layout.addSpacing(26)

        # Interface Metrics Table
        metrics_box = QVBoxLayout()
        metrics_box.setSpacing(10)

        self.lbl_iface_val = QLabel("wlan0")
        metrics_box.addWidget(self._create_metric_row("Interface:", self.lbl_iface_val))

        self.lbl_ip_val = QLabel("192.168.1.104")
        metrics_box.addWidget(self._create_metric_row("Local IP:", self.lbl_ip_val))

        self.lbl_total_val = QLabel("4.2 GB")
        metrics_box.addWidget(self._create_metric_row("Total Data Today:", self.lbl_total_val))

        layout.addLayout(metrics_box)
        layout.addSpacing(28)

        # Top Consumers Section
        consumers_title = QLabel("Top Consumers")
        consumers_title.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 13px; font-weight: 600;")
        layout.addWidget(consumers_title)
        layout.addSpacing(14)

        # 4 Circular Progress Rings
        self.rings_layout = QHBoxLayout()
        self.rings_layout.setSpacing(2)
        self.rings_layout.setContentsMargins(0, 0, 0, 0)

        self.ring1 = CircularProgressRing("App", 0)
        self.ring2 = CircularProgressRing("App", 0)
        self.ring3 = CircularProgressRing("App", 0)
        self.ring4 = CircularProgressRing("App", 0)

        self.rings = [self.ring1, self.ring2, self.ring3, self.ring4]
        for ring in self.rings:
            self.rings_layout.addWidget(ring)

        # Initial baseline top consumers from real running processes
        self._populate_initial_real_consumers()

        layout.addLayout(self.rings_layout)

        layout.addStretch()

        # Bottom Action Buttons with guaranteed 100% round pill curvature
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_suspend = PillButton("Suspend", "suspend", fill_icon=True)
        self.btn_suspend.clicked.connect(self._toggle_suspend)

        self.btn_export = PillButton("Export", "export", fill_icon=False)
        self.btn_export.clicked.connect(self.export_clicked.emit)

        btn_layout.addWidget(self.btn_suspend)
        btn_layout.addWidget(self.btn_export)

        layout.addLayout(btn_layout)

    def _populate_initial_real_consumers(self):
        """Immediately display real active applications in circular rings."""
        import psutil
        app_totals = {}
        try:
            for p in psutil.process_iter(["pid", "name"]):
                try:
                    name = p.info["name"] or ""
                    if name.startswith(("kworker", "pool_", "rcu")):
                        continue
                    io = p.io_counters() if hasattr(p, "io_counters") else None
                    if io:
                        tot = io.read_bytes + io.write_bytes
                        if tot > 0:
                            clean = name.split()[0].title()
                            app_totals[clean] = app_totals.get(clean, 0) + tot
                except Exception:
                    pass
        except Exception:
            pass

        sorted_apps = sorted(app_totals.items(), key=lambda x: x[1], reverse=True)
        total_sum = sum(app_totals.values()) or 1
        for i, ring in enumerate(self.rings):
            if i < len(sorted_apps):
                app_name, val = sorted_apps[i]
                pct = max(1, int(round((val / total_sum) * 100)))
                ring.set_data(app_name, pct)

    def paintEvent(self, event):
        super().paintEvent(event)
        # Subtle top-left folder tab accent like in prototype:
        # absolute top-0 left-0 w-24 h-1 bg-accent/50 rounded-br-full
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 210, 138, 128))
        painter.drawRoundedRect(QRectF(30, 0, 75, 3.5), 2, 2)
        painter.end()

    def _create_metric_row(self, label_text: str, val_widget: QLabel) -> QWidget:
        row = QWidget()
        row.setStyleSheet("border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 4px;")
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 4)

        lbl = QLabel(label_text)
        lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px; border: none;")

        val_widget.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 13px; font-weight: 500; border: none;")
        val_widget.setAlignment(Qt.AlignmentFlag.AlignRight)

        h.addWidget(lbl)
        h.addWidget(val_widget)
        return row

    def _toggle_suspend(self):
        self._is_suspended = not self._is_suspended
        if self._is_suspended:
            self.btn_suspend.setText("Resume")
            self.btn_suspend.setIconName("resume", fill=True)
            self.status_lbl.setText("DAEMON SUSPENDED")
            self.status_lbl.setStyleSheet("color: #f59e0b; font-size: 10px; font-weight: 700; letter-spacing: 1.5px;")
        else:
            self.btn_suspend.setText("Suspend")
            self.btn_suspend.setIconName("suspend", fill=True)
            self.status_lbl.setText("LIVE DAEMON ACTIVE | ROOT")
            self.status_lbl.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 10px; font-weight: 700; letter-spacing: 1.5px;")
        self.suspend_clicked.emit(self._is_suspended)

    def update_metrics(self, iface: str, ip: str, total_today_formatted: str, top_consumers: list, is_live: bool):
        self.lbl_iface_val.setText(iface)
        self.lbl_ip_val.setText(ip)
        self.lbl_total_val.setText(total_today_formatted)

        if not self._is_suspended:
            if is_live:
                self.status_lbl.setText("LIVE DAEMON ACTIVE | ROOT")
                self.status_lbl.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 10px; font-weight: 700; letter-spacing: 1.5px;")
            else:
                self.status_lbl.setText("SIMULATION MODE | DEV")
                self.status_lbl.setStyleSheet("color: #60a5fa; font-size: 10px; font-weight: 700; letter-spacing: 1.5px;")

        for i, ring in enumerate(self.rings):
            if i < len(top_consumers):
                c = top_consumers[i]
                short_name = c.get("name", "").split()[0]
                ring.set_data(short_name, c.get("percentage", 0))
