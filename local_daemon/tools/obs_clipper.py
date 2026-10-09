import os
import sys
import time
import socket

try:
    import obsws_python as obs
    OBSWS_AVAILABLE = True
except ImportError:
    OBSWS_AVAILABLE = False


class OBSAutoClipper:
    def __init__(self, host="localhost", port=4455, password=""):
        self.host = host
        self.port = port
        self.password = password
        self.client = None
        self.connected = False
        self._init_connection()

    def _is_port_listening(self, timeout=0.2):
        """Quick socket check to avoid noisy obsws-python tracebacks when OBS is closed."""
        try:
            with socket.create_connection((self.host, self.port), timeout=timeout):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def _init_connection(self):
        if not OBSWS_AVAILABLE or not self._is_port_listening():
            self.connected = False
            return

        try:
            self.client = obs.ReqClient(
                host=self.host,
                port=self.port,
                password=self.password,
                timeout=2
            )
            self.connected = True
        except Exception:
            self.connected = False

    def save_replay_buffer(self, trigger_reason="Manual Trigger"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        if not self.connected:
            return {
                "status": "simulated",
                "message": f"OBS not connected. Simulated clip trigger logged: [{trigger_reason}]",
                "timestamp": timestamp
            }

        try:
            self.client.save_replay_buffer()
            return {
                "status": "success",
                "message": f"OBS Replay Buffer saved successfully: [{trigger_reason}]",
                "timestamp": timestamp
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to save replay buffer: {str(e)}",
                "timestamp": timestamp
            }


if __name__ == "__main__":
    reason = sys.argv[1] if len(sys.argv) > 1 else "Hardware Anomaly Detected"
    clipper = OBSAutoClipper()
    result = clipper.save_replay_buffer(trigger_reason=reason)
    print(result)