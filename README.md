# NetTracer ⚡

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Arch%20Linux-blue?logo=archlinux" alt="Arch Linux" />
  <img src="https://img.shields.io/badge/Kernel-eBPF%20%2F%20BCC-orange?logo=linux" alt="eBPF BCC" />
  <img src="https://img.shields.io/badge/GUI-PyQt6-green?logo=qt" alt="PyQt6" />
  <img src="https://img.shields.io/badge/License-MIT-teal.svg" alt="License MIT" />
  <img src="https://img.shields.io/badge/Security-Privilege%20Separated-emerald" alt="Privilege Separated" />
</p>

<p align="center">
  <b>NetTracer</b> is a modern, high-performance per-process bandwidth monitoring suite for <b>Arch Linux</b>.<br/>
  Powered by in-kernel <b>eBPF (BCC)</b> socket tracing, non-blocking <b>Unix Domain Sockets</b>, <b>SQLite</b> persistence, and a native <b>PyQt6</b> desktop interface styled with exact dark-mode aesthetics.
</p>

---

## 🌟 Key Features

- **Kernel-Level eBPF Tracing**: Intercepts `sock_sendmsg` and `sock_recvmsg` return values via BCC kretprobes for zero-overhead per-PID TX/RX tracking.
- **Strict Privilege Separation**:
  - **Monitoring Daemon (`nettracer-daemon`)**: Root service managed by systemd.
  - **Desktop GUI (`nettracer-gui`)**: Unprivileged user-space PyQt6 application.
- **High-Performance Unix Domain Sockets**: Real-time JSON telemetry stream across `/run/nettracer/nettracer.sock` (`0666`).
- **Periodic SQLite Aggregation**: Batched 1-minute application usage records saved into SQLite with retention management.
- **Native PyQt6 UI (Zero WebEngine)**:
  - Custom dark palette (`#1a1b1e`, `#25262a`, `#1f2024`) with mint green accents (`#00d28a`).
  - Circular progress rings rendered via `QPainter` for top bandwidth consumers.
  - Interactive right navigation dock with 5 views: **Dashboard**, **Charts**, **History**, **Security**, and **Settings**.
  - Interactive daily bandwidth quota controller with editable `QSpinBox`.
- **Fault-Tolerant Simulation Fallback**: GUI runs seamlessly in interactive test mode even if the kernel daemon is offline.

---

## 🏛 System Architecture

```
+-----------------------------------------------------------------+
|                    User Space (Unprivileged)                    |
|                                                                 |
|   +---------------------------------------------------------+   |
|   |                      NetTracer GUI                      |   |
|   |  - Native PyQt6 Desktop Client                          |   |
|   |  - Custom QSS (#1a1b1e, #25262a, #00d28a)               |   |
|   |  - Custom QPainter Rings, Curves & Animated Toggles     |   |
|   |  - Views: Dashboard | Analytics | History | Rules | Prefs|  |
|   |  - Non-blocking QThread Unix Socket IPC Client          |   |
|   +----------------------------▲----------------------------+   |
+--------------------------------|--------------------------------+
                                 |
              Unix Domain Socket | /run/nettracer/nettracer.sock
                (JSON Streaming) | Mode: 0666
                                 |
+--------------------------------▼--------------------------------+
|                     Root Space (Kernel & systemd)               |
|                                                                 |
|   +---------------------------------------------------------+   |
|   |                    NetTracer Daemon                     |   |
|   |  - In-kernel eBPF Probes (sock_sendmsg & sock_recvmsg)  |   |
|   |  - Per-PID Atomic Counters in BPF Hash Map              |   |
|   |  - Process Resolution (/proc/[pid]/comm & cmdline)      |   |
|   |  - 1-Minute SQLite Bucket Aggregation                   |   |
|   |  - Broadcast IPC Unix Server                            |   |
|   +---------------------------------------------------------+   |
+-----------------------------------------------------------------+
```

---

## 📂 Directory Hierarchy

```
net-tracer/
├── bin/
│   ├── nettracer-daemon         # Daemon entrypoint wrapper
│   └── nettracer-gui            # GUI entrypoint wrapper
├── daemon/
│   ├── __init__.py
│   ├── bpf_tracer.py            # BCC eBPF kretprobes on socket I/O
│   ├── db.py                    # SQLite database manager & history log
│   ├── ipc_server.py            # Unix domain socket broadcast server
│   ├── process_tracker.py       # PID-to-process mapper and network info
│   └── service.py               # Main daemon coordinator & systemd loop
├── gui/
│   ├── __init__.py
│   ├── app.py                   # PyQt6 MainWindow & central coordinator
│   ├── ipc_client.py            # Threaded IPC client with fallback simulation
│   ├── styles.py                # Design system constants & QSS stylesheets
│   └── widgets/
│       ├── __init__.py
│       ├── circular_progress.py # Custom QPainter circular progress rings
│       ├── dock.py              # Floating right navigation pill dock
│       ├── sidebar.py           # Left stats and profile card
│       ├── toggle_switch.py     # Custom animated iOS/Tailwind toggle switches
│       ├── views_charts.py      # Charts / Traffic Analytics view
│       ├── views_dashboard.py   # Dashboard view (speeds & process list)
│       ├── views_history.py     # History log view with SQLite query
│       ├── views_security.py    # Network Rules & editable Daily Quota
│       └── views_settings.py    # Preferences view (Startup, Mode, Retention)
├── systemd/
│   └── nettracer.service        # Systemd unit file for root daemon
├── nettracer_ui.html            # Original prototype reference
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT License
└── README.md
```

---

## 🚀 Installation & Setup on Arch Linux

### 1. Install System Dependencies

Install kernel headers matching your kernel, BCC compiler collection, PyQt6, and psutil:

```bash
sudo pacman -S --needed \
    linux-headers \
    bcc \
    python-bcc \
    python-pyqt6 \
    python-psutil \
    sqlite
```

*(If you are running the `linux-zen` or `linux-lts` kernel, install `linux-zen-headers` or `linux-lts-headers` instead).*

### 2. Install & Start the Systemd Monitoring Daemon

```bash
# 1. Clone repository
git clone https://github.com/soheilabbasnia/net-tracer.git
cd net-tracer

# 2. Deploy to /opt/nettracer
sudo mkdir -p /opt/nettracer
sudo cp -r daemon bin requirements.txt /opt/nettracer/

# 3. Enable and start the systemd service
sudo cp systemd/nettracer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now nettracer.service

# 4. Check status
sudo systemctl status nettracer.service
```

### 3. Launch the Desktop GUI

Run the GUI as your standard desktop user:

```bash
./bin/nettracer-gui
```

---

## 🔒 Security Hardening

- The GUI runs completely unprivileged in **User Space** and communicates strictly through the Unix Domain Socket.
- The root daemon runs with systemd capability bounding sets:
  `CAP_BPF`, `CAP_NET_ADMIN`, `CAP_PERFMON`, `CAP_SYS_RESOURCE`, `CAP_SYS_ADMIN`
- Filesystem protections enabled: `ProtectSystem=full`, `ProtectHome=true`, and private runtime directories.

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).  
Copyright (c) 2026 Soheil Abbasnia.
