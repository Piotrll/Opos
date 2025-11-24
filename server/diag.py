import psutil
import os
import time

"""
    Diagnostic module for server health checks.
    Provides functionality to monitor CPU, RAM, and Disk usage.
    Makes avg OAScore available for health assessment.
"""

class Diag:
    """Diagnostic class for server health checks."""
    def __init__(self, log, abs_path, boot=False):
        self.OAScore = 100  # Placeholder for actual diagnostic score calculation
        self.log = log
        self.abs_path = abs_path
        if boot:
            results = self.run_boot_diag()
            

    def run_boot_diag(self, max_iterations=10, sleep_interval=0.5):
        """Run diagnostics at boot time."""
        samples = []
        count = 0
        memory_info = psutil.virtual_memory()
        drive_info = psutil.disk_usage(self.abs_path)
        cpu_usage = psutil.cpu_percent(interval=0)
        samples.append({
            "CPU-inuse": cpu_usage,
            "RAM-inuse": memory_info.percent,
            "Disk-inuse": drive_info.percent,
            "timestamp": time.time(),
        })
        while True:
            # collect metrics (runs at least once)
            time.sleep(sleep_interval)  # pacing between samples
            cpu_usage = psutil.cpu_percent(interval=0)
            

            samples.append({
                "CPU-inuse": cpu_usage,
                "timestamp": time.time(),
            })

            count += 1

            # post-condition check
            if max_iterations is not None and count >= max_iterations:
                break
            # otherwise loop again 
        self.evaluate_samples(samples)
        
    def evaluate_samples(self, samples):
        # simple evaluation: compute average CPU/RAM/Disk and derive a naive OAScore
        cpu_vals = self.get_cpu_values(samples)
        ram_vals = self.get_ram_values(samples)
        disk_vals = self.get_disk_values(samples)

        if cpu_vals:
            avg_cpu = sum(cpu_vals) / len(cpu_vals)
            avg_ram = sum(ram_vals) / len(ram_vals) if ram_vals else 0
            avg_disk = sum(disk_vals) / len(disk_vals) if disk_vals else 0

            # example: lower score for higher usage (simple heuristic)
            score = 100 - int(avg_cpu)
            score -= int(avg_ram * 0.1)   # small penalty for RAM
            score -= int(avg_disk * 0.1)  # small penalty for Disk
            self.OAScore = max(0, score)
        else:
            # prefer instance logger if available
            if hasattr(self, "log") and hasattr(self.log, "log_alert"):
                self.log.log_alert("No data available for evaluation. System may be unstable.")
            else:
                self.log.log_alert("No data available for evaluation. System may be unstable.")
            self.OAScore = 50  # default score if no data
        return self.OAScore

    def runtime_diag(self, max_iterations=5, sleep_interval=1.0):
        """Run diagnostics during runtime."""
        samples = []
        count = 0
        while True:
            # collect metrics
            time.sleep(sleep_interval)  # pacing between samples
            memory_info = psutil.virtual_memory()
            drive_info = psutil.disk_usage(self.abs_path)
            cpu_usage = psutil.cpu_percent(interval=0)

            samples.append({
                "CPU-inuse": cpu_usage,
                "RAM-inuse": memory_info.percent,
                "Disk-inuse": drive_info.percent,
                "timestamp": time.time(),
            })

            count += 1

            # post-condition check
            if max_iterations is not None and count >= max_iterations:
                break
            # otherwise loop again 
        self.last_samples = samples
        return self.evaluate_samples(samples)

    def get_cpu_values(self, samples=None):
        """Return list of CPU-inuse values from given samples or last_samples."""
        src = samples if samples is not None else self.last_samples
        cpu_list = []
        for s in src:
            if "CPU-inuse" in s:
                cpu_list.append(s["CPU-inuse"])
            elif "cpu_percent" in s:
                cpu_list.append(s["cpu_percent"])
        return cpu_list

    def get_ram_values(self, samples=None):
        """Return list of RAM-inuse (%) values."""
        src = samples if samples is not None else self.last_samples
        ram_list = []
        for s in src:
            if "RAM-inuse" in s:
                ram_list.append(s["RAM-inuse"])
            elif "memory_percent" in s:
                ram_list.append(s["memory_percent"])
        return ram_list

    def get_disk_values(self, samples=None):
        """Return list of Disk-inuse (%) values."""
        src = samples if samples is not None else self.last_samples
        disk_list = []
        for s in src:
            if "Disk-inuse" in s:
                disk_list.append(s["Disk-inuse"])
            elif "disk_percent" in s:
                disk_list.append(s["disk_percent"])
        return disk_list