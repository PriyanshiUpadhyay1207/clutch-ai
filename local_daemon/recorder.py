import os
import sys
import time
import json
import signal
from monitor import TelemetryCollector

class MatchRecorder:
    def __init__(self, game_name="Active Session", sample_interval_sec=2.0, output_dir="sessions"):
        self.game_name = game_name
        self.sample_interval = sample_interval_sec
        self.output_dir = output_dir
        self.collector = TelemetryCollector()
        self.running = False
        self.session_data = {
            "session_id": f"session_{int(time.time())}",
            "game": self.game_name,
            "start_time": time.time(),
            "end_time": None,
            "duration_seconds": 0,
            "samples": []
        }

        os.makedirs(self.output_dir, exist_ok=True)

    def _detect_anomalies(self, snapshot):
        anomalies = []
        cpu = snapshot["system"]
        gpu = snapshot["gpu"]

        # CPU Thresholds
        if cpu["cpu_percent"] >= 92.0:
            anomalies.append("CPU_HIGH_UTILIZATION")
        if cpu["ram_percent"] >= 90.0:
            anomalies.append("MEMORY_PRESSURE_CRITICAL")

        # GPU / Thermal Thresholds
        if gpu.get("gpu_detected"):
            if gpu.get("gpu_temp_c", 0) >= 84.0:
                anomalies.append("GPU_THERMAL_THROTTLE_RISK")
            if gpu.get("gpu_util_percent", 0) >= 98.0:
                anomalies.append("GPU_SATURATION")

        return anomalies

    def start(self):
        self.running = True
        print(f"[Clutch.ai] Recording telemetry for '{self.game_name}' every {self.sample_interval}s...")
        print("[Clutch.ai] Press Ctrl+C at any time to end the match session.")

        try:
            while self.running:
                snapshot = self.collector.snapshot()
                anomalies = self._detect_anomalies(snapshot)

                sample_entry = {
                    "offset_sec": round(time.time() - self.session_data["start_time"], 2),
                    "telemetry": snapshot,
                    "anomalies": anomalies
                }
                self.session_data["samples"].append(sample_entry)

                if anomalies:
                    print(f"[!] Anomaly detected at {sample_entry['offset_sec']}s: {', '.join(anomalies)}")

                time.sleep(self.sample_interval)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        self.session_data["end_time"] = time.time()
        self.session_data["duration_seconds"] = round(
            self.session_data["end_time"] - self.session_data["start_time"], 2
        )

        filename = os.path.join(self.output_dir, f"{self.session_data['session_id']}.json")
        latest_symlink = os.path.join(self.output_dir, "latest.json")

        with open(filename, "w") as f:
            json.dump(self.session_data, f, indent=2)

        with open(latest_symlink, "w") as f:
            json.dump(self.session_data, f, indent=2)

        print(f"\n[Clutch.ai] Session saved -> {filename}")
        print(f"[Clutch.ai] Linked latest trace -> {latest_symlink}")


if __name__ == "__main__":
    game_title = sys.argv[1] if len(sys.argv) > 1 else "Standard Match"
    recorder = MatchRecorder(game_name=game_title)
    recorder.start()