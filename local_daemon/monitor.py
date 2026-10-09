import time
import json
import psutil

# Optional import for NVIDIA GPU management
try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False


class TelemetryCollector:
    def __init__(self):
        self.has_nvidia_gpu = False
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.device_count = pynvml.nvmlDeviceGetCount()
                if self.device_count > 0:
                    self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    self.has_nvidia_gpu = True
            except Exception:
                self.has_nvidia_gpu = False

    def get_cpu_telemetry(self):
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_percent": psutil.virtual_memory().percent,
            "ram_used_gb": round(psutil.virtual_memory().used / (1024 ** 3), 2),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2)
        }

    def get_gpu_telemetry(self):
        if not self.has_nvidia_gpu:
            # Fallback mock telemetry for environments without an active NVIDIA GPU (e.g., macOS dev)
            return {
                "gpu_detected": False,
                "gpu_name": "Simulated GPU (Apple/Mock)",
                "gpu_temp_c": 62.0,
                "gpu_util_percent": 45.0,
                "vram_used_mb": 2048,
                "vram_total_mb": 8192
            }

        try:
            temp = pynvml.nvmlDeviceGetTemperature(self.handle, pynvml.NVML_TEMPERATURE_GPU)
            util = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            gpu_name = pynvml.nvmlDeviceGetName(self.handle)
            if isinstance(gpu_name, bytes):
                gpu_name = gpu_name.decode("utf-8")

            return {
                "gpu_detected": True,
                "gpu_name": gpu_name,
                "gpu_temp_c": float(temp),
                "gpu_util_percent": float(util.gpu),
                "vram_used_mb": round(memory_info.used / (1024 ** 2), 2),
                "vram_total_mb": round(memory_info.total / (1024 ** 2), 2)
            }
        except Exception as e:
            return {
                "gpu_detected": False,
                "error": str(e)
            }

    def snapshot(self):
        timestamp = time.time()
        cpu_data = self.get_cpu_telemetry()
        gpu_data = self.get_gpu_telemetry()

        return {
            "timestamp": timestamp,
            "system": cpu_data,
            "gpu": gpu_data
        }


if __name__ == "__main__":
    collector = TelemetryCollector()
    print("Collecting single hardware telemetry snapshot...")
    snapshot = collector.snapshot()
    print(json.dumps(snapshot, indent=2))