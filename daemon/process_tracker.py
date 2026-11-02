"""
NetTracer - Process Tracker & Network Interface Resolver
Maps PIDs to application names and identifies local network interface details.
"""

import os
import socket
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger("nettracer.proc")

KNOWN_APP_MAP = {
    "chrome": ("Google Chrome", "ph-google-chrome-logo"),
    "google-chrome": ("Google Chrome", "ph-google-chrome-logo"),
    "chromium": ("Chromium", "ph-google-chrome-logo"),
    "telegram-desktop": ("Telegram Desktop", "ph-paper-plane-tilt"),
    "telegram": ("Telegram Desktop", "ph-paper-plane-tilt"),
    "spotify": ("Spotify", "ph-spotify-logo"),
    "pacman": ("Pacman", "ph-terminal-window"),
    "yay": ("Yay", "ph-terminal-window"),
    "firefox": ("Firefox", "ph-firefox-logo"),
    "dockerd": ("Docker Daemon", "ph-docker-logo"),
    "docker": ("Docker", "ph-docker-logo"),
    "code": ("VS Code", "ph-code"),
    "steam": ("Steam", "ph-game-controller"),
    "discord": ("Discord", "ph-chat-circle-dots"),
    "systemd": ("System Services", "ph-linux-logo"),
    "systemd-resolved": ("System Updates", "ph-linux-logo"),
    "python": ("Python Runtime", "ph-terminal"),
    "python3": ("Python Runtime", "ph-terminal"),
}


class ProcessTracker:
    """Tracks PID names and maps them to clean titles and icons."""

    def __init__(self):
        self._name_cache: Dict[int, Tuple[str, str]] = {}

    def get_process_info(self, pid: int) -> Tuple[str, str]:
        """
        Returns (display_name, icon_name) for a given PID.
        Uses /proc filesystem directly for maximum speed and zero dependencies.
        """
        if pid in self._name_cache:
            return self._name_cache[pid]

        comm = ""
        # 1. Try reading /proc/[pid]/comm
        try:
            with open(f"/proc/{pid}/comm", "r", encoding="utf-8", errors="ignore") as f:
                comm = f.read().strip()
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass

        # 2. Try reading /proc/[pid]/cmdline if comm is generic or empty
        cmdline = ""
        if not comm or comm in ("python", "python3", "electron"):
            try:
                with open(f"/proc/{pid}/cmdline", "r", encoding="utf-8", errors="ignore") as f:
                    cmdline = f.read().replace("\x00", " ").strip()
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                pass

        display_name, icon_key = self._resolve_name(pid, comm, cmdline)
        self._name_cache[pid] = (display_name, icon_key)
        return display_name, icon_key

    def _resolve_name(self, pid: int, comm: str, cmdline: str) -> Tuple[str, str]:
        check_str = (comm + " " + cmdline).lower()

        for key, (friendly_name, icon) in KNOWN_APP_MAP.items():
            if key in check_str:
                return friendly_name, icon

        if comm:
            # Capitalize comm name cleanly
            clean_comm = comm.replace("-", " ").replace("_", " ").title()
            return clean_comm, "ph-cpu"

        return f"Process #{pid}", "ph-cpu"

    def clean_cache(self):
        """Purge stale PIDs that are no longer active."""
        active_pids = set()
        for entry in os.listdir("/proc"):
            if entry.isdigit():
                active_pids.add(int(entry))
        self._name_cache = {pid: v for pid, v in self._name_cache.items() if pid in active_pids}

    @staticmethod
    def get_network_details() -> Tuple[str, str]:
        """
        Detects primary outbound network interface and local IP address.
        Returns: (interface_name, local_ip)
        """
        iface = "wlan0"
        local_ip = "127.0.0.1"
        try:
            # Query default route socket without sending packets
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]

            # Find matching interface in /proc/net/route or ip route
            try:
                with open("/proc/net/route", "r") as f:
                    lines = f.readlines()[1:]
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) >= 2 and parts[1] == "00000000":  # Default gateway
                            iface = parts[0]
                            break
            except Exception:
                pass
        except Exception:
            local_ip = "192.168.1.104"
            iface = "wlan0"

        return iface, local_ip
