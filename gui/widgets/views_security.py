"""
NetTracer - Security / Network Rules & Limits View
Provides rules and interactive configuration for daily bandwidth quota limits.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSpinBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

from gui.styles import (
    COLOR_CARD_DARK, COLOR_CARD_DARKER, COLOR_ACCENT,
    COLOR_TEXT_MAIN, COLOR_TEXT_MUTED
)
from gui.widgets.toggle_switch import ToggleSwitch
from gui.widgets.icons import VectorIcons


class SecurityView(QWidget):
    """Security rules and quota warnings view."""

    quota_changed = pyqtSignal(int)
    background_block_toggled = pyqtSignal(bool)
    quota_warning_toggled = pyqtSignal(bool)

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
            QFrame#SecurityCard {{
                background-color: {COLOR_CARD_DARK};
                border-radius: 36px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
        """)
        card.setObjectName("SecurityCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 28, 32, 28)
        card_layout.setSpacing(24)

        # Header: NETWORK RULES & LIMITS with vector shield icon
        header_row = QHBoxLayout()
        header_icon = QLabel()
        header_icon.setPixmap(VectorIcons.render_pixmap("security", size=16, color=COLOR_ACCENT))
        header_icon.setStyleSheet("border: none; background: transparent;")

        header_lbl = QLabel("NETWORK RULES & LIMITS")
        header_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-weight: 700; letter-spacing: 1.2px; border: none;")

        header_row.addWidget(header_icon)
        header_row.addWidget(header_lbl)
        header_row.addStretch()
        card_layout.addLayout(header_row)

        # Two Rule Cards Row
        rules_row = QHBoxLayout()
        rules_row.setSpacing(20)

        # 1. Block Background Data Card
        card1 = QFrame()
        card1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        card1.setStyleSheet(f"""
            QFrame#RuleCard1 {{
                background-color: {COLOR_CARD_DARKER};
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
            QFrame#RuleCard1:hover {{
                border: 1px solid rgba(255, 255, 255, 0.12);
            }}
        """)
        card1.setObjectName("RuleCard1")
        card1_lay = QHBoxLayout(card1)
        card1_lay.setContentsMargins(22, 20, 22, 20)

        info1 = QVBoxLayout()
        info1.setSpacing(4)
        title1 = QLabel("Block Background Data")
        title1.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 16px; font-weight: 600; border: none; background: transparent;")
        sub1 = QLabel("Prevent apps from using data when minimized")
        sub1.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px; border: none; background: transparent;")
        info1.addWidget(title1)
        info1.addWidget(sub1)

        self.toggle_bg = ToggleSwitch(checked=False)
        self.toggle_bg.toggled.connect(self.background_block_toggled.emit)

        card1_lay.addLayout(info1)
        card1_lay.addStretch()
        card1_lay.addWidget(self.toggle_bg, alignment=Qt.AlignmentFlag.AlignVCenter)

        # 2. Daily Quota Warning Card (Highlighted with mint border)
        card2 = QFrame()
        card2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        card2.setStyleSheet(f"""
            QFrame#RuleCard2 {{
                background-color: rgba(0, 210, 138, 0.04);
                border-radius: 24px;
                border: 1px solid rgba(0, 210, 138, 0.28);
            }}
        """)
        card2.setObjectName("RuleCard2")
        card2_lay = QHBoxLayout(card2)
        card2_lay.setContentsMargins(22, 20, 22, 20)

        info2 = QVBoxLayout()
        info2.setSpacing(6)
        title2 = QLabel("Daily Quota Warning")
        title2.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 16px; font-weight: 600; border: none; background: transparent;")

        # Interactive editable quota input row
        quota_input_row = QHBoxLayout()
        quota_input_row.setSpacing(8)

        sub2_prefix = QLabel("Alert when usage exceeds")
        sub2_prefix.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px; border: none; background: transparent;")

        self.spin_quota = QSpinBox()
        self.spin_quota.setRange(1, 999)
        self.spin_quota.setValue(5)
        self.spin_quota.setFixedWidth(64)
        self.spin_quota.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_quota.valueChanged.connect(self.quota_changed.emit)

        sub2_suffix = QLabel("GB/day")
        sub2_suffix.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px; border: none; background: transparent;")

        quota_input_row.addWidget(sub2_prefix)
        quota_input_row.addWidget(self.spin_quota)
        quota_input_row.addWidget(sub2_suffix)
        quota_input_row.addStretch()

        info2.addWidget(title2)
        info2.addLayout(quota_input_row)

        self.toggle_quota = ToggleSwitch(checked=True)
        self.toggle_quota.toggled.connect(self.quota_warning_toggled.emit)

        card2_lay.addLayout(info2)
        card2_lay.addStretch()
        card2_lay.addWidget(self.toggle_quota, alignment=Qt.AlignmentFlag.AlignVCenter)

        rules_row.addWidget(card1)
        rules_row.addWidget(card2)

        card_layout.addLayout(rules_row)
        card_layout.addStretch()

        main_layout.addWidget(card)

    def set_quota_value(self, quota_gb: int):
        self.spin_quota.setValue(quota_gb)
