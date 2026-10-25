"""USB/serial inventory and bounded optional read-only port capture."""
from __future__ import annotations
import platform
import time

class ExpansionPack:
    def __init__(self):
        self.name = "Universal USB & Serial Port Monitor"

    def _ports(self):
        try:
            from serial.tools import list_ports
            return [{"port": p.device, "description": p.description, "hwid": p.hwid}
                    for p in list_ports.comports()]
        except ImportError:
            return None
        except Exception:
            return []

    def run_diagnostics(self, payload):
        ports = self._ports()
        if ports is None:
            return {
                "status": "dependency_missing",
                "sector": "usb_serial_monitor",
                "host_os": platform.system(),
                "message": "pyserial is not installed. Run run_jbot.bat to install the declared dependencies.",
                "ports": [],
                "bytes_written": 0,
            }
        requested_port = str(payload.get("port", "")).strip()
        if not requested_port:
            return {
                "status": "inventory_complete",
                "sector": "usb_serial_monitor",
                "host_os": platform.system(),
                "ports": ports,
                "monitoring": "not_started",
                "bytes_written": 0,
                "note": "Enumeration only. To request a short read-only capture, set port, read_only_capture=true, and confirm_open_port=true.",
            }
        if not (payload.get("read_only_capture") is True and payload.get("confirm_open_port") is True):
            return {
                "status": "confirmation_required",
                "sector": "usb_serial_monitor",
                "ports": ports,
                "message": "Opening serial ports may toggle hardware control lines. Explicitly confirm a short read-only capture.",
                "bytes_written": 0,
            }
        if requested_port not in {p["port"] for p in ports}:
            return {"status": "port_not_found", "sector": "usb_serial_monitor", "ports": ports, "bytes_written": 0}
        try:
            import serial
        except ImportError:
            return {"status": "dependency_missing", "message": "Install project requirements to enable serial capture."}
        try:
            baudrate = int(payload.get("baudrate", 115200))
            duration = float(payload.get("duration_seconds", 2))
        except (ValueError, TypeError):
            return {"status": "invalid_parameters", "message": "baudrate and duration_seconds must be numeric."}
        if baudrate not in {9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600}:
            return {"status": "invalid_parameters", "message": "Baud rate not in the supported allowlist."}
        duration = max(0.25, min(duration, 3.0))
        captured = bytearray()
        try:
            # Read only. Never call write() or send commands to a connected controller.
            with serial.Serial(port=None, baudrate=baudrate, timeout=0.1, write_timeout=0.1) as connection:
                connection.port = requested_port
                connection.dtr = False
                connection.rts = False
                connection.open()
                deadline = time.monotonic() + duration
                while time.monotonic() < deadline and len(captured) < 2048:
                    part = connection.read(min(128, 2048 - len(captured)))
                    if part:
                        captured.extend(part)
        except Exception as exc:
            return {
                "status": "capture_failed",
                "sector": "usb_serial_monitor",
                "port": requested_port,
                "message": "Read failed: " + type(exc).__name__ + ". Confirm authorization and that another application is not using the port.",
                "bytes_written": 0,
            }
        return {
            "status": "capture_complete",
            "sector": "usb_serial_monitor",
            "port": requested_port,
            "baudrate": baudrate,
            "duration_seconds": duration,
            "bytes_read": len(captured),
            "hex_sample": bytes(captured[:512]).hex(" "),
            "text_sample": bytes(captured[:512]).decode("utf-8", errors="replace"),
            "bytes_written": 0,
            "note": "Only received bytes were sampled. Serial data may include sensitive information; handle it accordingly.",
        }
