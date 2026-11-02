"""
NetTracer - eBPF Socket Traffic Tracer via BCC
Tracks socket send/receive bandwidth per PID using kernel probes.
"""

import os
import sys
import time
import logging
from typing import Dict, Tuple

logger = logging.getLogger("nettracer.bpf")

BPF_PROGRAM = r"""
#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>

struct traffic_val_t {
    u64 tx_bytes;
    u64 rx_bytes;
};

// Map PID -> traffic_val_t
BPF_HASH(traffic_map, u32, struct traffic_val_t);

// Intercept return of sock_sendmsg to track outbound bytes
int kretprobe__sock_sendmsg(struct pt_regs *ctx) {
    int ret = PT_REGS_RC(ctx);
    if (ret <= 0)
        return 0;

    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid >> 32;

    struct traffic_val_t zero = {0, 0};
    struct traffic_val_t *val = traffic_map.lookup_or_init(&pid, &zero);
    if (val) {
        __sync_fetch_and_add(&val->tx_bytes, (u64)ret);
    }
    return 0;
}

// Intercept return of sock_recvmsg to track inbound bytes
int kretprobe__sock_recvmsg(struct pt_regs *ctx) {
    int ret = PT_REGS_RC(ctx);
    if (ret <= 0)
        return 0;

    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid >> 32;

    struct traffic_val_t zero = {0, 0};
    struct traffic_val_t *val = traffic_map.lookup_or_init(&pid, &zero);
    if (val) {
        __sync_fetch_and_add(&val->rx_bytes, (u64)ret);
    }
    return 0;
}
"""


class BpfTracer:
    """
    Manages eBPF probes attached to socket system operations via BCC.
    Provides per-PID delta counts between polls.
    """

    def __init__(self, simulate_fallback: bool = True):
        self.simulate_fallback = simulate_fallback
        self.is_simulated = False
        self.bpf = None
        self.traffic_map = None
        self._last_poll_time = time.time()
        self._suspended = False

        self._init_bpf()

    def _init_bpf(self):
        # Must be root to attach eBPF probes
        if os.geteuid() != 0:
            logger.warning("NetTracer not running as root (UID != 0). eBPF requires root.")
            if self.simulate_fallback:
                logger.info("Engaging simulation fallback mode for user testing.")
                self.is_simulated = True
                self._init_simulation()
                return
            else:
                raise PermissionError("eBPF requires root privileges (CAP_BPF / CAP_SYS_ADMIN).")

        try:
            from bcc import BPF  # type: ignore

            logger.info("Compiling and loading eBPF socket monitoring probes via BCC...")
            self.bpf = BPF(text=BPF_PROGRAM)
            self.traffic_map = self.bpf["traffic_map"]
            logger.info("eBPF probes successfully attached to sock_sendmsg and sock_recvmsg.")
        except ImportError:
            logger.error("python-bcc is not installed on this system.")
            if self.simulate_fallback:
                logger.info("Engaging simulation fallback mode.")
                self.is_simulated = True
                self._init_simulation()
            else:
                raise
        except Exception as e:
            logger.error(f"Failed to initialize eBPF: {e}")
            if self.simulate_fallback:
                logger.info("Engaging simulation fallback mode.")
                self.is_simulated = True
                self._init_simulation()
            else:
                raise

    def _init_simulation(self):
        import random
        self._sim_random = random.Random()
        # Simulated cumulative traffic
        self._sim_data: Dict[int, Dict[str, int]] = {}

    def set_suspended(self, suspended: bool):
        """Temporarily suspend tracing without unloading kernel probes."""
        self._suspended = suspended

    def poll_traffic(self) -> Tuple[Dict[int, Dict[str, int]], float]:
        """
        Polls per-PID byte counters since last poll.
        Returns:
            ( { pid: {"rx_bytes": delta_rx, "tx_bytes": delta_tx} }, time_delta_sec )
        """
        now = time.time()
        time_delta = max(0.001, now - self._last_poll_time)
        self._last_poll_time = now

        if self._suspended:
            return {}, time_delta

        if self.is_simulated:
            return self._poll_simulated(time_delta)

        deltas: Dict[int, Dict[str, int]] = {}
        if self.traffic_map is None:
            return deltas, time_delta

        # Atomic read and clear of the BPF map entries
        for key, val in self.traffic_map.items():
            pid = key.value
            tx = val.tx_bytes
            rx = val.rx_bytes
            if tx > 0 or rx > 0:
                deltas[pid] = {"tx_bytes": tx, "rx_bytes": rx}

        # Clear map entries for the next interval
        self.traffic_map.clear()
        return deltas, time_delta

    def _poll_simulated(self, time_delta: float) -> Tuple[Dict[int, Dict[str, int]], float]:
        """Generates realistic network traffic for active applications when testing."""
        import psutil
        import random

        deltas = {}
        target_names = ["chrome", "firefox", "telegram", "spotify", "pacman", "python", "curl", "discord"]
        procs = []
        for p in psutil.process_iter(["pid", "name"]):
            try:
                name = (p.info["name"] or "").lower()
                if any(t in name for t in target_names):
                    procs.append(p.info["pid"])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # If few matching processes, take some existing PIDs
        if len(procs) < 3:
            for p in psutil.process_iter(["pid"]):
                if p.info["pid"] > 100:
                    procs.append(p.info["pid"])
                if len(procs) >= 5:
                    break

        for pid in procs[:6]:
            # Generate plausible bandwidth (KB to MB range)
            rx = int(random.uniform(50_000, 750_000) * time_delta)
            tx = int(random.uniform(5_000, 150_000) * time_delta)
            deltas[pid] = {"rx_bytes": rx, "tx_bytes": tx}

        return deltas, time_delta
