"""
NetTracer - History / App Data Log View
Displays persisted 1-minute historical bandwidth records retrieved from SQLite.
"""

from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal

from gui.styles import (
    COLOR_CARD_DARK, COLOR_CARD_DARKER, COLOR_ACCENT,
    COLOR_TEXT_MAIN, COLOR_TEXT_MUTED
)


class HistoryLogItem(QFrame):
    """Row widget representing a single historical log entry."""

    def __init__(self, time_str: str, app_name: str, icon_str: str, dl_str: str, ul_str: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame#HistoryLogItem {{
                background-color: {COLOR_CARD_DARKER};
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.04);
            }}
            QFrame#HistoryLogItem:hover {{
                border: 1px solid rgba(255, 255, 255, 0.12);
            }}
        """)
        self.setObjectName("HistoryLogItem")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # 1. Timestamp (25% width)
        time_lbl = QLabel(time_str)
        time_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(time_lbl, stretch=1)

        # 2. App Name & Icon (25% width)
        app_lbl = QLabel(f"{icon_str}  {app_name}")
        app_lbl.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 13px; font-weight: 600;")
        layout.addWidget(app_lbl, stretch=1)

        # 3. Download (25% width, aligned right)
        dl_lbl = QLabel(dl_str)
        dl_lbl.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 13px; font-weight: 500;")
        dl_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(dl_lbl, stretch=1)

        # 4. Upload (25% width, aligned right)
        ul_lbl = QLabel(ul_str)
        ul_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")
        ul_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(ul_lbl, stretch=1)


class HistoryView(QWidget):
    """History view showing logged bandwidth usage."""

    clear_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame#HistoryCard {{
                background-color: {COLOR_CARD_DARK};
                border-radius: 36px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
        """)
        card.setObjectName("HistoryCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 28, 32, 28)
        card_layout.setSpacing(20)

        # Top Bar: APP DATA LOG + Clear History Button
        top_bar = QHBoxLayout()
        header_lbl = QLabel("🕒 APP DATA LOG")
        header_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-weight: 700; letter-spacing: 1.2px;")

        self.btn_clear = QPushButton("Clear History")
        self.btn_clear.setProperty("class", "subtle-btn")
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_requested.emit)

        top_bar.addWidget(header_lbl)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_clear)
        card_layout.addLayout(top_bar)

        # Scroll Area for Log Items
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.items_layout = QVBoxLayout(self.scroll_content)
        self.items_layout.setContentsMargins(0, 0, 8, 0)
        self.items_layout.setSpacing(12)
        self.items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll.setWidget(self.scroll_content)
        card_layout.addWidget(self.scroll)

        main_layout.addWidget(card)

        # Populate initial default rows matching mockup
        self._populate_mockup_items()

    def _populate_mockup_items(self):
        sample_logs = [
            ("Today, 10:30 AM", "Firefox", "🦊", "+450 MB (DL)", "12 MB (UL)"),
            ("Today, 09:15 AM", "Docker Daemon", "🐳", "+1.2 GB (DL)", "300 MB (UL)"),
            ("Yesterday", "System Updates", "🐧", "+800 MB (DL)", "2 MB (UL)"),
        ]
        for t, app, icon, dl, ul in sample_logs:
            item = HistoryLogItem(t, app, icon, dl, ul)
            self.items_layout.addWidget(item)

    def set_history_records(self, records: List[Dict[str, Any]]):
        """Refreshes history list with live records from SQLite."""
        # Clear existing items
        while self.items_layout.count() > 0:
            child = self.items_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not records:
            empty_lbl = QLabel("No history records yet.")
            empty_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px; padding: 20px;")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.items_layout.addWidget(empty_lbl)
            return

        for r in records:
            app = r.get("app_name", "Unknown")
            dl = self._format_bytes(r.get("rx_bytes", 0))
            ul = self._format_bytes(r.get("tx_bytes", 0))
            ts = r.get("timestamp", "")
            icon = self._get_icon_symbol(app)
            item = HistoryLogItem(ts, app, icon, f"+{dl} (DL)", f"{ul} (UL)")
            self.items_layout.addWidget(item)

    @staticmethod
    def _get_icon_symbol(name: str) -> str:
        nl = name.lower()
        if "firefox" in nl:
            return "🦊"
        elif "chrome" in nl:
            return "🌐"
        elif "docker" in nl:
            return "🐳"
        elif "update" in nl or "linux" in nl:
            return "🐧"
        elif "telegram" in nl:
            return "✈"
        elif "spotify" in nl:
            return "🎵"
        return "⚙"

    @staticmethod
    def _format_bytes(b: int) -> str:
        if b >= 1024 * 1024 * 1024:
            return f"{b / (1024 * 1024 * 1024):.1f} GB"
        elif b >= 1024 * 1024:
            return f"{b / (1024 * 1024):.1f} MB"
        elif b >= 1024:
            return f"{b / 1024:.1f} KB"
        return f"{b} B"
