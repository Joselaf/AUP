"""
Shared Tuya UDP listener.

Tuya devices broadcast encrypted status packets on:
  - port 6666  (protocol v3.1 / v3.2)
  - port 6667  (protocol v3.3+, GCM-encrypted)

One listener binds to each port and receives packets from ALL devices on the
LAN. Each packet is decrypted using the originating device's local key, then
the parsed DPS dict is forwarded to the matching device object via
update_from_dps().
"""
from __future__ import annotations

import socket
import threading
import logging

logger = logging.getLogger(__name__)

_PORTS  = (6666, 6667)
_BUFFER = 4096


class UDPListener:
    def __init__(self, device_registry: dict, on_update=None):
        """
        device_registry : dict  device_id (str) → device object
        on_update       : callable(device_id, device_obj) — called on the
                          listener thread after a successful DPS update.
                          Use call_from_thread() in the callback to push
                          UI changes safely.
        """
        self._registry   = device_registry
        self._on_update  = on_update
        self._stop_event = threading.Event()
        self._threads: list[threading.Thread] = []

        # Per-device lock so UDP and poll loop never write dps/stats at the
        # same time.  Keyed by device_id.
        self._dev_locks: dict[str, threading.Lock] = {
            dev_id: threading.Lock()
            for dev_id in device_registry
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        for port in _PORTS:
            t = threading.Thread(
                target=self._listen,
                args=(port,),
                name=f"udp-listener-{port}",
                daemon=True,
            )
            t.start()
            self._threads.append(t)
        logger.info("UDPListener started on ports %s", _PORTS)

    def stop(self) -> None:
        self._stop_event.set()

    def get_lock(self, device_id: str) -> threading.Lock:
        """Return the per-device lock. Poll loop acquires this before refresh()."""
        return self._dev_locks.get(device_id, threading.Lock())

    def update_registry(self, registry: dict) -> None:
        self._registry = registry
        for dev_id in registry:
            if dev_id not in self._dev_locks:
                self._dev_locks[dev_id] = threading.Lock()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _listen(self, port: int) -> None:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(1.0)
            sock.bind(("", port))
        except OSError as e:
            logger.warning("UDPListener: cannot bind port %d: %s", port, e)
            return

        logger.debug("UDPListener: listening on port %d", port)
        while not self._stop_event.is_set():
            try:
                data, addr = sock.recvfrom(_BUFFER)
            except socket.timeout:
                continue
            except OSError:
                break
            self._handle_packet(data, addr)
        sock.close()

    def _handle_packet(self, data: bytes, addr: tuple) -> None:
        sender_ip = addr[0]

        # First try devices whose stored IP matches the sender
        candidates = [
            dev for dev in self._registry.values()
            if getattr(dev, "ip", None) == sender_ip
        ]

        # If no match, the device may have changed IP — try all devices
        if not candidates:
            candidates = list(self._registry.values())

        for dev in candidates:
            try:
                result = dev.device.receive(data)
                if not (result and isinstance(result, dict)):
                    continue
                dps = result.get("dps") or result.get("Data")
                if not dps:
                    continue

                # Update IP if it changed (DHCP reassignment)
                if getattr(dev, "ip", None) != sender_ip:
                    logger.info(
                        "Device %s IP changed: %s → %s",
                        dev.name, dev.ip, sender_ip,
                    )
                    dev.ip = sender_ip
                    dev.device.address = sender_ip

                # Acquire the per-device lock before mutating dps/stats
                lock = self._dev_locks.get(dev.id)
                if lock:
                    with lock:
                        dev.update_from_dps(dps)
                else:
                    dev.update_from_dps(dps)

                if self._on_update:
                    self._on_update(dev.id, dev)
                return

            except Exception:
                continue
