"""
NetTracer - Floating Right Navigation Dock
Vertical pill dock allowing seamless switching between application views.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QColor

from gui.styles import COLOR_CARD_DARK, COLOR_ACCENT, COLOR_TEXT_MUTED, COLOR_TEXT_MAIN
from gui.widgets.icons import VectorIcons


class NavDockButton(QPushButton):
    """Circular icon navigation button using crisp vector icons."""

    def __init__(self, icon_name: str, tooltip: str, parent=None):
        super().__init__(parent)
        self.icon_name = icon_name
        self.setToolTip(tooltip)
        self.setFixedSize(46, 46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._is_active = False

    def setActive(self, active: bool):
        self._is_active = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        rect = QRectF(2, 2, w - 4, h - 4)

        if self._is_active:
            # Mint green subtle glowing circle background
            painter.setBrush(QColor(0, 210, 138, 38))  # ~15% opacity accent
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(rect)
            icon_color = COLOR_ACCENT
            fill = True
        elif self.underMouse():
            painter.setBrush(QColor(255, 255, 255, 18))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(rect)
            icon_color = COLOR_TEXT_MAIN
            fill = False
        else:
            icon_color = COLOR_TEXT_MUTED
            fill = False

        # Draw vector icon
        icon_size = 22
        pix = VectorIcons.render_pixmap(self.icon_name, size=icon_size, color=icon_color, fill=fill)
        ix = int((w - icon_size) / 2.0)
        iy = int((h - icon_size) / 2.0)
        painter.drawPixmap(ix, iy, pix)
        painter.end()


class NavigationDock(QFrame):
    """Vertical floating pill dock for tab selection."""

    tab_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(64)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(f"""
            QFrame#NavDockFrame {{
                background-color: {COLOR_CARD_DARK};
                border-radius: 32px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }}
        """)
        self.setObjectName("NavDockFrame")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(9, 22, 9, 22)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 0: Dashboard (Four squares / grid)
        self.btn_dashboard = NavDockButton("dashboard", "Dashboard")
        self.btn_dashboard.clicked.connect(lambda: self.set_active_tab(0))

        # 1: Charts (Analytics chart)
        self.btn_charts = NavDockButton("charts", "Traffic Analytics")
        self.btn_charts.clicked.connect(lambda: self.set_active_tab(1))

        # 2: History (Clock)
        self.btn_history = NavDockButton("history", "App Data Log")
        self.btn_history.clicked.connect(lambda: self.set_active_tab(2))

        # 3: Security (Shield)
        self.btn_security = NavDockButton("security", "Network Rules & Limits")
        self.btn_security.clicked.connect(lambda: self.set_active_tab(3))

        # Divider
        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setFixedWidth(26)
        divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);")

        # 4: Settings (Gear)
        self.btn_settings = NavDockButton("settings", "Preferences")
        self.btn_settings.clicked.connect(lambda: self.set_active_tab(4))

        self.buttons = [
            self.btn_dashboard,
            self.btn_charts,
            self.btn_history,
            self.btn_security,
            self.btn_settings
        ]

        layout.addWidget(self.btn_dashboard)
        layout.addWidget(self.btn_charts)
        layout.addWidget(self.btn_history)
        layout.addWidget(self.btn_security)
        layout.addWidget(divider, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.btn_settings)

        # Default active tab = 0 (Dashboard)
        self.set_active_tab(0)

    def set_active_tab(self, index: int):
        for i, btn in enumerate(self.buttons):
            btn.setActive(i == index)
        self.tab_changed.emit(index)
