"""
NetTracer - Main Desktop GUI Application
Assembles native PyQt6 components, custom styling, IPC communication, and page views.
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QIcon, QPainterPath

from gui.styles import APPLICATION_QSS, COLOR_BG_DARK, COLOR_ACCENT
from gui.widgets.sidebar import SidebarWidget
from gui.widgets.dock import NavigationDock
from gui.widgets.views_dashboard import DashboardView
from gui.widgets.views_charts import ChartsView
from gui.widgets.views_history import HistoryView
from gui.widgets.views_security import SecurityView
from gui.widgets.views_settings import SettingsView
from gui.ipc_client import IPCClientThread


class BackgroundDecoratedWindow(QMainWindow):
    """Main window with subtle geometric diamond accents matching prototype."""

    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Subtle decorative mint diamonds from prototype
        w = self.width()
        h = self.height()

        diamonds = [
            (int(w * 0.25), int(h * 0.15), 6, 178),  # 70% opacity
            (int(w * 0.75), int(h * 0.85), 6, 178),
            (int(w * 0.75), int(h * 0.05), 5, 76),   # 30% opacity
        ]

        for cx, cy, sz, alpha in diamonds:
            painter.setBrush(QColor(0, 210, 138, alpha))
            painter.setPen(Qt.PenStyle.NoPen)
            path = QPainterPath()
            path.moveTo(cx, cy - sz)
            path.lineTo(cx + sz, cy)
            path.lineTo(cx, cy + sz)
            path.lineTo(cx - sz, cy)
            path.closeSubpath()
            painter.drawPath(path)


class NetTracerApp(BackgroundDecoratedWindow):
    """Primary application controller window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetTracer - Bandwidth Monitor")
        self.resize(1340, 780)
        self.setMinimumSize(1100, 680)

        self._setup_ui()
        self._init_ipc()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(28, 28, 28, 28)
        main_layout.setSpacing(24)

        # 1. Left Sidebar
        self.sidebar = SidebarWidget(self)
        main_layout.addWidget(self.sidebar)

        # 2. Central Content Area: Stacked Views
        self.stack = QStackedWidget(self)
        self.view_dashboard = DashboardView(self)
        self.view_charts = ChartsView(self)
        self.view_history = HistoryView(self)
        self.view_security = SecurityView(self)
        self.view_settings = SettingsView(self)

        self.stack.addWidget(self.view_dashboard)  # Index 0
        self.stack.addWidget(self.view_charts)     # Index 1
        self.stack.addWidget(self.view_history)    # Index 2
        self.stack.addWidget(self.view_security)   # Index 3
        self.stack.addWidget(self.view_settings)   # Index 4

        main_layout.addWidget(self.stack, stretch=1)

        # 3. Right Floating Dock
        self.dock = NavigationDock(self)
        main_layout.addWidget(self.dock, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Connect Dock navigation signals
        self.dock.tab_changed.connect(self._on_tab_changed)

        # Connect user actions
        self.sidebar.suspend_clicked.connect(self._on_suspend_clicked)
        self.sidebar.export_clicked.connect(self._on_export_clicked)
        self.view_security.quota_changed.connect(self._on_quota_changed)
        self.view_history.clear_requested.connect(self._on_clear_history)
        self.view_settings.setting_changed.connect(self._on_setting_changed)

    def _init_ipc(self):
        self.ipc_thread = IPCClientThread(self)
        self.ipc_thread.telemetry_received.connect(self._on_telemetry_received)
        self.ipc_thread.history_received.connect(self.view_history.set_history_records)
        self.ipc_thread.connection_changed.connect(self._on_connection_changed)
        self.ipc_thread.start()

    def _on_tab_changed(self, index: int):
        self.stack.setCurrentIndex(index)
        if index == 2:  # History tab opened, request fresh log from daemon
            self.ipc_thread.send_command({"action": "get_history", "limit": 50})

    def _on_telemetry_received(self, data: dict):
        iface = data.get("interface", "wlan0")
        ip = data.get("local_ip", "192.168.1.104")
        total_str = data.get("total_today_formatted", "4.2 GB")
        top_consumers = data.get("top_consumers", [])
        is_live = not data.get("is_simulated", False) and self.ipc_thread._connected

        # Update Sidebar
        self.sidebar.update_metrics(iface, ip, total_str, top_consumers, is_live)

        # Update Dashboard
        self.view_dashboard.update_telemetry(data)

        # Update Charts
        dl = data.get("live_dl_mb_s", 0.0)
        ul = data.get("live_ul_mb_s", 0.0)
        self.view_charts.update_telemetry(dl, ul)

    def _on_connection_changed(self, is_connected: bool):
        pass

    def _on_suspend_clicked(self, suspended: bool):
        self.ipc_thread.send_command({"action": "suspend", "state": suspended})

    def _on_export_clicked(self):
        print("Export metrics requested.")

    def _on_quota_changed(self, quota_gb: int):
        self.ipc_thread.send_command({"action": "set_quota", "quota_gb": quota_gb})

    def _on_clear_history(self):
        self.ipc_thread.send_command({"action": "clear_history"})
        self.view_history.set_history_records([])

    def _on_setting_changed(self, key: str, value):
        self.ipc_thread.send_command({"action": "update_setting", "key": key, "value": value})

    def closeEvent(self, event):
        self.ipc_thread.stop()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APPLICATION_QSS)
    window = NetTracerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
