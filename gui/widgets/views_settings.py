"""
NetTracer - Settings / Preferences View
Configures startup daemon behavior, eBPF strictness, and database retention periods.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from gui.styles import (
    COLOR_CARD_DARK, COLOR_CARD_DARKER, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED
)
from gui.widgets.toggle_switch import ToggleSwitch


class SettingItemRow(QFrame):
    """Row widget for individual preference options."""

    def __init__(self, title: str, subtitle: str, control_widget: QWidget, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame#SettingItemRow {{
                background-color: {COLOR_CARD_DARKER};
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.04);
            }}
            QFrame#SettingItemRow:hover {{
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)
        self.setObjectName("SettingItemRow")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)

        text_col = QVBoxLayout()
        text_col.setSpacing(4)

        t_lbl = QLabel(title)
        t_lbl.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 15px; font-weight: 600;")

        s_lbl = QLabel(subtitle)
        s_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")

        text_col.addWidget(t_lbl)
        text_col.addWidget(s_lbl)

        layout.addLayout(text_col)
        layout.addStretch()
        layout.addWidget(control_widget, alignment=Qt.AlignmentFlag.AlignVCenter)


class SettingsView(QWidget):
    """Preferences tab matching the mockup."""

    setting_changed = pyqtSignal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame#SettingsCard {{
                background-color: {COLOR_CARD_DARK};
                border-radius: 36px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
        """)
        card.setObjectName("SettingsCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 28, 32, 28)
        card_layout.setSpacing(16)

        # Header: PREFERENCES
        header_lbl = QLabel("⚙ PREFERENCES")
        header_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-weight: 700; letter-spacing: 1.2px;")
        card_layout.addWidget(header_lbl)

        # Setting 1: Launch at Startup
        self.toggle_startup = ToggleSwitch(checked=True)
        self.toggle_startup.toggled.connect(lambda v: self.setting_changed.emit("launch_at_startup", v))
        row1 = SettingItemRow("Launch at Startup", "Start NetTracer daemon automatically on boot", self.toggle_startup)
        card_layout.addWidget(row1)

        # Setting 2: eBPF Strict Mode
        self.toggle_strict = ToggleSwitch(checked=False)
        self.toggle_strict.toggled.connect(lambda v: self.setting_changed.emit("ebpf_strict_mode", v))
        row2 = SettingItemRow("eBPF Strict Mode", "Drop packets without matching PID (Requires Root)", self.toggle_strict)
        card_layout.addWidget(row2)

        # Setting 3: Data Retention
        self.combo_retention = QComboBox()
        self.combo_retention.addItems(["7 Days", "30 Days", "Forever"])
        self.combo_retention.setCurrentIndex(1)  # 30 Days default
        self.combo_retention.currentTextChanged.connect(lambda v: self.setting_changed.emit("data_retention", v))
        row3 = SettingItemRow("Data Retention", "Keep application usage history for", self.combo_retention)
        card_layout.addWidget(row3)

        card_layout.addStretch()

        main_layout.addWidget(card)
