"""
NetTracer - Floating Right Navigation Dock
Vertical pill dock allowing seamless switching between application views.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPainter, QColor, QFont, QPen

from gui.styles import COLOR_CARD_DARK, COLOR_ACCENT, COLOR_TEXT_MUTED, COLOR_TEXT_MAIN


class NavDockButton(QPushButton):
    """Circular icon navigation button within the right dock."""

    def __init__(self, icon_symbol: str, tooltip: str, parent=None):
        super().__init__(parent)
        self.icon_symbol = icon_symbol
        self.setToolTip(tooltip)
        self.setFixedSize(44, 44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._is_active = False

    def setActive(self, active: bool):
        self._is_active = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._is_active:
            # Mint green subtle glowing circle background
            painter.setBrush(QColor(0, 210, 138, 38))  # ~15% opacity accent
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(2, 2, self.width() - 4, self.height() - 4)
            painter.setPen(QColor(COLOR_ACCENT))
        elif self.underMouse():
            painter.setBrush(QColor(255, 255, 255, 16))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(2, 2, self.width() - 4, self.height() - 4)
            painter.setPen(QColor(COLOR_TEXT_MAIN))
        else:
            painter.setPen(QColor(COLOR_TEXT_MUTED))

        # Draw icon symbol
        font = QFont("Segoe UI Symbol", 16)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.icon_symbol)


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
        layout.setContentsMargins(10, 24, 10, 24)
        layout.setSpacing(18)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 0: Dashboard (Four squares / grid)
        self.btn_dashboard = NavDockButton("⊞", "Dashboard")
        self.btn_dashboard.clicked.connect(lambda: self.set_active_tab(0))

        # 1: Charts (Analytics chart)
        self.btn_charts = NavDockButton("📈", "Traffic Analytics")
        self.btn_charts.clicked.connect(lambda: self.set_active_tab(1))

        # 2: History (Clock)
        self.btn_history = NavDockButton("🕒", "App Data Log")
        self.btn_history.clicked.connect(lambda: self.set_active_tab(2))

        # 3: Security (Shield)
        self.btn_security = NavDockButton("🛡", "Network Rules & Limits")
        self.btn_security.clicked.connect(lambda: self.set_active_tab(3))

        # Divider
        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setFixedWidth(28)
        divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);")

        # 4: Settings (Gear)
        self.btn_settings = NavDockButton("⚙", "Preferences")
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

        # Set default active tab = 0 (Dashboard)
        self.set_active_tab(0)

    def set_active_tab(self, index: int):
        for i, btn in enumerate(self.buttons):
            btn.setActive(i == index)
        self.tab_changed.emit(index)
