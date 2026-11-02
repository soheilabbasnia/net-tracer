"""
NetTracer - Unix Domain Socket IPC Server
Enables secure privilege separation between root daemon and user-space GUI.
"""

import os
import json
import socket
import select
import logging
import threading
from typing import Dict, Any, List, Callable, Optional

logger = logging.getLogger("nettracer.ipc")

DEFAULT_SOCKET_DIR = "/run/nettracer"
DEFAULT_SOCKET_PATH = "/run/nettracer/nettracer.sock"
FALLBACK_SOCKET_PATH = "/tmp/nettracer.sock"


class IPCServer:
    """Unix Domain Socket IPC server with broadcast and RPC support."""

    def __init__(self, request_handler: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None):
        self.request_handler = request_handler
        self.socket_path = self._resolve_socket_path()
        self._server_sock: Optional[socket.socket] = None
        self._clients: List[socket.socket] = []
        self._clients_lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def _resolve_socket_path(self) -> str:
        # Check if root and can create /run/nettracer
        if os.geteuid() == 0:
            try:
                os.makedirs(DEFAULT_SOCKET_DIR, mode=0o755, exist_ok=True)
                return DEFAULT_SOCKET_PATH
            except OSError:
                pass
        return FALLBACK_SOCKET_PATH

    def start(self):
        """Bind socket and start background listening thread."""
        if os.path.exists(self.socket_path):
            try:
                os.unlink(self.socket_path)
            except OSError:
                pass

        self._server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server_sock.bind(self.socket_path)

        # Allow user-space desktop apps to read/write to the socket
        try:
            os.chmod(self.socket_path, 0o666)
        except OSError as e:
            logger.warning(f"Could not chmod socket {self.socket_path}: {e}")

        self._server_sock.listen(10)
        self._server_sock.setblocking(False)
        self._running = True

        logger.info(f"IPC Unix Domain Socket active at: {self.socket_path}")

        self._thread = threading.Thread(target=self._run_server, name="IPCServerThread", daemon=True)
        self._thread.start()

    def _run_server(self):
        while self._running:
            try:
                with self._clients_lock:
                    readable, _, _ = select.select([self._server_sock] + self._clients, [], [], 0.5)

                for s in readable:
                    if s is self._server_sock:
                        client_sock, _ = self._server_sock.accept()
                        client_sock.setblocking(False)
                        with self._clients_lock:
                            self._clients.append(client_sock)
                        logger.info("GUI client connected via Unix Socket.")
                    else:
                        # Data incoming from client
                        try:
                            data = s.recv(4096)
                            if data:
                                self._handle_client_data(s, data)
                            else:
                                self._disconnect_client(s)
                        except (ConnectionResetError, BrokenPipeError):
                            self._disconnect_client(s)
            except Exception as e:
                if self._running:
                    logger.debug(f"IPC loop iteration note: {e}")

    def _handle_client_data(self, client_sock: socket.socket, raw_bytes: bytes):
        lines = raw_bytes.decode("utf-8", errors="ignore").strip().split("\n")
        for line in lines:
            if not line:
                continue
            try:
                msg = json.loads(line)
                if self.request_handler:
                    response = self.request_handler(msg)
                    if response:
                        resp_bytes = (json.dumps(response) + "\n").encode("utf-8")
                        client_sock.sendall(resp_bytes)
            except Exception as e:
                logger.error(f"Error handling IPC message: {e}")

    def _disconnect_client(self, client_sock: socket.socket):
        with self._clients_lock:
            if client_sock in self._clients:
                self._clients.remove(client_sock)
        try:
            client_sock.close()
        except OSError:
            pass
        logger.info("GUI client disconnected.")

    def broadcast_telemetry(self, telemetry: Dict[str, Any]):
        """Broadcasts live network telemetry payload to all connected GUI clients."""
        payload = json.dumps({"type": "telemetry", "data": telemetry}) + "\n"
        payload_bytes = payload.encode("utf-8")

        with self._clients_lock:
            disconnected = []
            for client in self._clients:
                try:
                    client.sendall(payload_bytes)
                except (BrokenPipeError, ConnectionResetError, OSError):
                    disconnected.append(client)

            for dead in disconnected:
                self._clients.remove(dead)
                try:
                    dead.close()
                except OSError:
                    pass

    def stop(self):
        """Closes socket and terminates server thread."""
        self._running = False
        with self._clients_lock:
            for client in self._clients:
                try:
                    client.close()
                except OSError:
                    pass
            self._clients.clear()

        if self._server_sock:
            try:
                self._server_sock.close()
            except OSError:
                pass

        if os.path.exists(self.socket_path):
            try:
                os.unlink(self.socket_path)
            except OSError:
                pass
        logger.info("IPC Server stopped.")
