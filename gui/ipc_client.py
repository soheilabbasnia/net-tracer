"""
NetTracer - Unix Socket IPC Client
Handles unprivileged communication between the desktop GUI and root monitoring daemon.
"""

import os
import json
import time
import socket
import select
import random
from typing import Dict, Any, Optional

from PyQt6.QtCore import QThread, pyqtSignal

SOCKET_PATHS = [
    "/run/nettracer/nettracer.sock",
    "/tmp/nettracer.sock"
]


class IPCClientThread(QThread):
    """Background worker thread maintaining connection to the monitoring daemon."""

    telemetry_received = pyqtSignal(dict)
    history_received = pyqtSignal(list)
    connection_changed = pyqtSignal(bool)  # True = Live Daemon, False = Demo/Offline Mode

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True
        self._sock: Optional[socket.socket] = None
        self._connected = False
        self._pending_commands: list = []

    def run(self):
        while self._running:
            if not self._connected:
                self._attempt_connect()

            if self._connected and self._sock:
                self._read_socket_stream()
            else:
                # Simulation / Demo fallback loop when daemon is offline
                self._run_simulation_step()
                time.sleep(1.0)

    def _attempt_connect(self):
        for path in SOCKET_PATHS:
            if os.path.exists(path):
                try:
                    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    s.connect(path)
                    s.setblocking(False)
                    self._sock = s
                    self._connected = True
                    self.connection_changed.emit(True)
                    return
                except (ConnectionRefusedError, PermissionError, OSError):
                    pass
        if self._connected:
            self._connected = False
            self.connection_changed.emit(False)

    def _read_socket_stream(self):
        buffer = ""
        while self._running and self._connected and self._sock:
            # Check for pending commands to write
            while self._pending_commands:
                cmd = self._pending_commands.pop(0)
                try:
                    self._sock.sendall((json.dumps(cmd) + "\n").encode("utf-8"))
                except OSError:
                    self._disconnect()
                    return

            try:
                r, _, _ = select.select([self._sock], [], [], 0.5)
                if not r:
                    continue

                chunk = self._sock.recv(4096)
                if not chunk:
                    self._disconnect()
                    return

                buffer += chunk.decode("utf-8", errors="ignore")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                        msg_type = msg.get("type")
                        if msg_type == "telemetry":
                            self.telemetry_received.emit(msg.get("data", {}))
                        elif msg_type == "history_response":
                            self.history_received.emit(msg.get("data", []))
                    except json.JSONDecodeError:
                        pass
            except OSError:
                self._disconnect()
                return

    def _disconnect(self):
        self._connected = False
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        self.connection_changed.emit(False)

    def send_command(self, cmd: Dict[str, Any]):
        """Queue a command to be sent to daemon."""
        if self._connected and self._sock:
            self._pending_commands.append(cmd)

    def _run_simulation_step(self):
        """Produces realistic data matching the prototype when daemon is offline."""
        base_dl = 2.4
        base_ul = 0.8
        fluc_dl = random.uniform(-0.4, 0.5)
        fluc_ul = random.uniform(-0.1, 0.2)

        live_dl = max(0.1, round(base_dl + fluc_dl, 1))
        live_ul = max(0.05, round(base_ul + fluc_ul, 1))

        telemetry = {
            "timestamp": time.time(),
            "interface": "wlan0",
            "local_ip": "192.168.1.104",
            "live_dl_mb_s": live_dl,
            "live_ul_mb_s": live_ul,
            "total_today_bytes": 4200 * 1024 * 1024,
            "total_today_formatted": "4.2 GB",
            "tracked_count": 42,
            "top_consumers": [
                {"name": "Chrome", "percentage": 68},
                {"name": "Telegram", "percentage": 22},
                {"name": "Spotify", "percentage": 8},
                {"name": "Pacman", "percentage": 2},
            ],
            "processes": [
                {"pid": 8432, "name": "Google Chrome", "rx_bytes": 2100 * 1024 * 1024, "tx_bytes": 340 * 1024 * 1024},
                {"pid": 1205, "name": "Telegram Desktop", "rx_bytes": 450 * 1024 * 1024, "tx_bytes": 80 * 1024 * 1024},
                {"pid": 3491, "name": "Spotify", "rx_bytes": 120 * 1024 * 1024, "tx_bytes": 5 * 1024 * 1024},
                {"pid": 9912, "name": "Pacman", "rx_bytes": 45 * 1024 * 1024, "tx_bytes": int(1.2 * 1024 * 1024)},
            ]
        }
        self.telemetry_received.emit(telemetry)

    def stop(self):
        self._running = False
        self._disconnect()
        self.wait(1000)
