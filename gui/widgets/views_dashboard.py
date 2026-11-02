"""
NetTracer - Dashboard View
Main view showcasing real-time bandwidth speeds, live status, and active per-process cards.
"""

from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QFrame, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

from gui.styles import (
    COLOR_CARD_DARK, COLOR_CARD_DARKER, COLOR_ACCENT,
    COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, COLOR_BG_DARK
)
from gui.widgets.icons import VectorIcons


class ProcessCardItem(QFrame):
    """Card widget representing an active monitored process."""

    def __init__(self, pid: int, name: str, icon_key: str, rx_str: str, tx_str: str, parent=None):
        super().__init__(parent)
        self._setup_ui(pid, name, icon_key, rx_str, tx_str)

    def _setup_ui(self, pid: int, name: str, icon_key: str, rx_str: str, tx_str: str):
        self.setStyleSheet(f"""
            QFrame#ProcessCardItem {{
                background-color: {COLOR_CARD_DARKER};
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
            QFrame#ProcessCardItem:hover {{
                border: 1px solid rgba(255, 255, 255, 0.12);
            }}
        """)
        self.setObjectName("ProcessCardItem")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        # Top Row: App Icon, Name, and PID
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        # Vector Icon box
        self.icon_box = QLabel()
        self.icon_box.setFixedSize(38, 38)
        self.icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_box.setStyleSheet(f"""
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
        """)
        pix = VectorIcons.render_pixmap(icon_key, size=20, color=COLOR_TEXT_MAIN)
        self.icon_box.setPixmap(pix)

        # Name and PID
        meta_layout = QVBoxLayout()
        meta_layout.setSpacing(2)

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 13px; font-weight: 600;")

        pid_lbl = QLabel(f"PID: {pid}")
        pid_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px;")

        meta_layout.addWidget(name_lbl)
        meta_layout.addWidget(pid_lbl)

        top_row.addWidget(self.icon_box)
        top_row.addLayout(meta_layout)
        top_row.addStretch()

        layout.addLayout(top_row)

        # Bottom Row: RX and TX metrics boxes
        stats_row = QHBoxLayout()
        stats_row.setSpacing(8)

        # RX box
        rx_box = QFrame()
        rx_box.setStyleSheet(f"background-color: {COLOR_BG_DARK}; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.04);")
        rx_lay = QVBoxLayout(rx_box)
        rx_lay.setContentsMargins(6, 6, 6, 6)
        rx_lay.setSpacing(2)
        rx_title = QLabel("RX")
        rx_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rx_title.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 9px;")
        self.rx_val = QLabel(rx_str)
        self.rx_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rx_val.setStyleSheet(f"color: {COLOR_ACCENT}; font-size: 12px; font-weight: 600;")
        rx_lay.addWidget(rx_title)
        rx_lay.addWidget(self.rx_val)

        # TX box
        tx_box = QFrame()
        tx_box.setStyleSheet(f"background-color: {COLOR_BG_DARK}; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.04);")
        tx_lay = QVBoxLayout(tx_box)
        tx_lay.setContentsMargins(6, 6, 6, 6)
        tx_lay.setSpacing(2)
        tx_title = QLabel("TX")
        tx_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tx_title.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 9px;")
        self.tx_val = QLabel(tx_str)
        self.tx_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tx_val.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 12px; font-weight: 600;")
        tx_lay.addWidget(tx_title)
        tx_lay.addWidget(self.tx_val)

        stats_row.addWidget(rx_box)
        stats_row.addWidget(tx_box)

        layout.addLayout(stats_row)

    def update_values(self, rx_str: str, tx_str: str):
        self.rx_val.setText(rx_str)
        self.tx_val.setText(tx_str)


class DashboardView(QWidget):
    """Main Dashboard View matching the HTML structure."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.process_widgets: Dict[int, ProcessCardItem] = {}
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(24)

        # Left Column: Hero Title & Speed Cards
        left_col = QVBoxLayout()
        left_col.setContentsMargins(10, 10, 10, 10)
        left_col.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        left_col.setSpacing(14)

        # Live Traffic pill badge (Properly padded without fixed-width cutoff!)
        pill_badge = QFrame()
        pill_badge.setStyleSheet(f"""
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        """)
        pill_lay = QHBoxLayout(pill_badge)
        pill_lay.setContentsMargins(12, 6, 16, 6)
        pill_lay.setSpacing(8)

        icon_live = QLabel()
        icon_live.setPixmap(VectorIcons.render_pixmap("live", size=14, color=COLOR_ACCENT))
        icon_live.setStyleSheet("border: none; background: transparent;")

        lbl_live_text = QLabel("Live Traffic")
        lbl_live_text.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px; font-weight: 500; border: none; background: transparent;")

        pill_lay.addWidget(icon_live)
        pill_lay.addWidget(lbl_live_text)

        badge_container = QHBoxLayout()
        badge_container.addWidget(pill_badge)
        badge_container.addStretch()
        left_col.addLayout(badge_container)

        # Headline
        headline = QLabel()
        headline.setTextFormat(Qt.TextFormat.RichText)
        headline.setText(
            f'<div style="font-size: 46px; font-weight: 800; line-height: 1.1; color: {COLOR_TEXT_MAIN};">'
            f'Monitor your<br>'
            f'<span style="color: {COLOR_ACCENT};">Network Activity</span>'
            f'</div>'
        )
        left_col.addWidget(headline)

        # Subtitle paragraph
        self.desc_lbl = QLabel(
            "eBPF socket monitoring is active. Currently tracking 42 processes in real-time. "
            "Unrecognized UDP packets are dropped from stats."
        )
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setMaximumWidth(460)
        self.desc_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px; line-height: 1.5;")
        left_col.addWidget(self.desc_lbl)

        # Checklist badges
        checks_row = QHBoxLayout()
        checks_row.setSpacing(20)

        chk1 = QLabel(f'<span style="color:{COLOR_ACCENT}; font-weight:bold;">✓</span> Real-time')
        chk1.setTextFormat(Qt.TextFormat.RichText)
        chk1.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")

        chk2 = QLabel(f'<span style="color:{COLOR_ACCENT}; font-weight:bold;">✓</span> Zero-overhead')
        chk2.setTextFormat(Qt.TextFormat.RichText)
        chk2.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px;")

        checks_row.addWidget(chk1)
        checks_row.addWidget(chk2)
        checks_row.addStretch()
        left_col.addLayout(checks_row)
        left_col.addSpacing(16)

        # Big Speeds Box (Refined with vector arrows)
        speeds_frame = QFrame()
        speeds_frame.setStyleSheet(f"""
            background-color: rgba(37, 38, 42, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 28px;
        """)
        speeds_frame.setFixedSize(380, 114)

        speeds_layout = QHBoxLayout(speeds_frame)
        speeds_layout.setContentsMargins(24, 16, 24, 16)
        speeds_layout.setSpacing(20)

        # Download column
        dl_col = QVBoxLayout()
        dl_col.setSpacing(4)
        
        dl_head = QHBoxLayout()
        dl_icon = QLabel()
        dl_icon.setPixmap(VectorIcons.render_pixmap("download", size=13, color=COLOR_ACCENT))
        dl_icon.setStyleSheet("border: none; background: transparent;")
        lbl_dl_tag = QLabel("DOWNLOAD")
        lbl_dl_tag.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px; font-weight: 700; letter-spacing: 1px; border: none;")
        dl_head.addWidget(dl_icon)
        dl_head.addWidget(lbl_dl_tag)
        dl_head.addStretch()

        dl_val_row = QHBoxLayout()
        self.lbl_live_dl = QLabel("2.4")
        self.lbl_live_dl.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 32px; font-weight: 800; border: none;")
        dl_unit = QLabel("MB/s")
        dl_unit.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px; font-weight: 400; padding-bottom: 4px; border: none;")
        dl_unit.setAlignment(Qt.AlignmentFlag.AlignBottom)
        dl_val_row.addWidget(self.lbl_live_dl)
        dl_val_row.addWidget(dl_unit)
        dl_val_row.addStretch()

        dl_col.addLayout(dl_head)
        dl_col.addLayout(dl_val_row)

        # Divider
        divider = QWidget()
        divider.setFixedWidth(1)
        divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);")

        # Upload column
        ul_col = QVBoxLayout()
        ul_col.setSpacing(4)

        ul_head = QHBoxLayout()
        ul_icon = QLabel()
        ul_icon.setPixmap(VectorIcons.render_pixmap("upload", size=13, color=COLOR_ACCENT))
        ul_icon.setStyleSheet("border: none; background: transparent;")
        lbl_ul_tag = QLabel("UPLOAD")
        lbl_ul_tag.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px; font-weight: 700; letter-spacing: 1px; border: none;")
        ul_head.addWidget(ul_icon)
        ul_head.addWidget(lbl_ul_tag)
        ul_head.addStretch()

        ul_val_row = QHBoxLayout()
        self.lbl_live_ul = QLabel("0.8")
        self.lbl_live_ul.setStyleSheet(f"color: {COLOR_TEXT_MAIN}; font-size: 32px; font-weight: 800; border: none;")
        ul_unit = QLabel("MB/s")
        ul_unit.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px; font-weight: 400; padding-bottom: 4px; border: none;")
        ul_unit.setAlignment(Qt.AlignmentFlag.AlignBottom)
        ul_val_row.addWidget(self.lbl_live_ul)
        ul_val_row.addWidget(ul_unit)
        ul_val_row.addStretch()

        ul_col.addLayout(ul_head)
        ul_col.addLayout(ul_val_row)

        speeds_layout.addLayout(dl_col)
        speeds_layout.addWidget(divider)
        speeds_layout.addLayout(ul_col)

        left_col.addWidget(speeds_frame)
        main_layout.addLayout(left_col, stretch=1)

        # Right Column: Process List Card
        proc_card = QFrame()
        proc_card.setFixedWidth(380)
        proc_card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        proc_card.setStyleSheet(f"""
            QFrame#ProcCard {{
                background-color: rgba(37, 38, 42, 0.85);
                border-radius: 36px;
                border: 1px solid rgba(255, 255, 255, 0.06);
            }}
        """)
        proc_card.setObjectName("ProcCard")

        proc_layout = QVBoxLayout(proc_card)
        proc_layout.setContentsMargins(20, 24, 20, 20)
        proc_layout.setSpacing(14)

        # Card Header
        header_row = QHBoxLayout()
        icon_cpu = QLabel()
        icon_cpu.setPixmap(VectorIcons.render_pixmap("settings", size=14, color=COLOR_ACCENT))
        icon_cpu.setStyleSheet("border: none; background: transparent;")
        header_title = QLabel("PROCESS LIST")
        header_title.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-weight: 700; letter-spacing: 1.2px; border: none;")

        sort_btn = QPushButton("Sort by Usage ▼")
        sort_btn.setProperty("class", "subtle-btn")
        sort_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        header_row.addWidget(icon_cpu)
        header_row.addWidget(header_title)
        header_row.addStretch()
        header_row.addWidget(sort_btn)
        proc_layout.addLayout(header_row)

        # Scroll Area for Process Cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.items_layout = QVBoxLayout(self.scroll_content)
        self.items_layout.setContentsMargins(0, 4, 8, 4)
        self.items_layout.setSpacing(12)
        self.items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        proc_layout.addWidget(self.scroll_area)

        # Pre-populate with initial mockup items using vector icons
        self._populate_initial_mockup()

        main_layout.addWidget(proc_card)

    def _populate_initial_mockup(self):
        samples = [
            (8432, "Google Chrome", "chrome", "2.1 GB", "340 MB"),
            (1205, "Telegram Desktop", "telegram", "450 MB", "80 MB"),
            (3491, "Spotify", "spotify", "120 MB", "5 MB"),
            (9912, "Pacman", "pacman", "45 MB", "1.2 MB"),
        ]
        for pid, name, icon_key, rx, tx in samples:
            card = ProcessCardItem(pid, name, icon_key, rx, tx)
            self.process_widgets[pid] = card
            self.items_layout.addWidget(card)

    def update_telemetry(self, data: Dict[str, Any]):
        dl = data.get("live_dl_mb_s", 2.4)
        ul = data.get("live_ul_mb_s", 0.8)
        self.lbl_live_dl.setText(f"{dl:.1f}")
        self.lbl_live_ul.setText(f"{ul:.1f}")

        tracked_cnt = data.get("tracked_count", 42)
        self.desc_lbl.setText(
            f"eBPF socket monitoring is active. Currently tracking {tracked_cnt} processes in real-time. "
            f"Unrecognized UDP packets are dropped from stats."
        )

        processes = data.get("processes", [])
        if processes:
            current_pids = set()
            for p in processes[:15]:
                pid = p["pid"]
                current_pids.add(pid)
                rx_str = self._format_bytes(p.get("rx_bytes", 0))
                tx_str = self._format_bytes(p.get("tx_bytes", 0))
                name = p.get("name", "Unknown")
                icon_key = self._get_icon_key(name)

                if pid in self.process_widgets:
                    self.process_widgets[pid].update_values(rx_str, tx_str)
                else:
                    card = ProcessCardItem(pid, name, icon_key, rx_str, tx_str)
                    self.process_widgets[pid] = card
                    self.items_layout.addWidget(card)

    @staticmethod
    def _get_icon_key(name: str) -> str:
        nl = name.lower()
        if "chrome" in nl:
            return "chrome"
        elif "telegram" in nl:
            return "telegram"
        elif "spotify" in nl:
            return "spotify"
        elif "pacman" in nl or "yay" in nl:
            return "pacman"
        elif "firefox" in nl:
            return "firefox"
        elif "docker" in nl:
            return "docker"
        return "settings"

    @staticmethod
    def _format_bytes(b: int) -> str:
        if b >= 1024 * 1024 * 1024:
            return f"{b / (1024 * 1024 * 1024):.1f} GB"
        elif b >= 1024 * 1024:
            return f"{b / (1024 * 1024):.1f} MB"
        elif b >= 1024:
            return f"{b / 1024:.1f} KB"
        return f"{b} B"
