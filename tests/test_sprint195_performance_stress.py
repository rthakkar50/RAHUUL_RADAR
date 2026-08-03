import unittest
import time
import asyncio
import os
import psutil
from api.main import health_check, run_swing_scanner, run_intraday_scanner
from core.telegram_intelligence import TelegramIntelligence
from core.backend_url_resolver import BackendUrlResolver

class TestSprint195PerformanceStress(unittest.TestCase):
    def test_task1_health_endpoint_latency(self):
        """Task 11 & Task 14: Verify /health latency is < 50ms across 100 calls."""
        latencies = []
        async def run_100_health():
            for _ in range(100):
                t0 = time.time()
                res = await health_check()
                t1 = time.time()
                latencies.append((t1 - t0) * 1000)
                self.assertEqual(res.get("status"), "online")
        
        asyncio.run(run_100_health())
        avg_lat = sum(latencies) / len(latencies)
        max_lat = max(latencies)
        print(f"\n[PERF-BENCHMARK] /health Avg Latency: {avg_lat:.2f}ms | Max Latency: {max_lat:.2f}ms")
        self.assertLess(avg_lat, 50.0, f"Average health latency {avg_lat:.2f}ms exceeded 50ms threshold")

    def test_task2_cached_scanner_latency(self):
        """Task 11 & Task 14: Verify cached scanner response latency is < 100ms across 100 calls."""
        latencies = []
        async def run_100_scanner():
            for _ in range(100):
                t0 = time.time()
                res = await run_swing_scanner()
                t1 = time.time()
                latencies.append((t1 - t0) * 1000)
                self.assertIn("qualified_results", res)
        
        asyncio.run(run_100_scanner())
        avg_lat = sum(latencies) / len(latencies)
        max_lat = max(latencies)
        print(f"[PERF-BENCHMARK] Cached Scanner Avg Latency: {avg_lat:.2f}ms | Max Latency: {max_lat:.2f}ms")
        self.assertLess(avg_lat, 100.0, f"Average cached scanner latency {avg_lat:.2f}ms exceeded 100ms threshold")

    def test_task3_telegram_commands(self):
        """Task 14: Verify 50 Telegram command calls execute without failure."""
        intel = TelegramIntelligence.get_instance()
        for i in range(50):
            res = intel.get_system_health()
            self.assertIn("SYSTEM HEALTH", res)

    def test_task4_memory_cpu_stress(self):
        """Task 9 & 14: Measure RAM and CPU footprint under stress."""
        proc = psutil.Process(os.getpid())
        mem_mb = proc.memory_info().rss / (1024 * 1024)
        cpu_pct = psutil.cpu_percent(interval=0.1)
        print(f"[PERF-BENCHMARK] RAM Memory: {mem_mb:.2f} MB | CPU: {cpu_pct:.1f}%")
        self.assertLess(mem_mb, 500.0, f"RAM memory {mem_mb:.1f}MB exceeded Render 512MB limit")

if __name__ == "__main__":
    unittest.main()
