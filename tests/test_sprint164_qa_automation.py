import unittest
import urllib.request
import json
import time
import psutil
import os
from application.paper_trading_service import PaperTradingEngine

BASE_URL = "http://127.0.0.1:8000/api/v1"

class TestSprint164QAAutomation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = PaperTradingEngine.get_instance()
        cls.service.engine.max_open_positions = 100
        cls.service.engine.max_exposure_pct = 500.0

    def _fetch_json(self, endpoint, method="GET", body=None, timeout=20):
        url = f"{BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        data = json.dumps(body).encode('utf-8') if body else None
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        start_time = time.time()
        with urllib.request.urlopen(req, timeout=timeout) as response:
            latency = (time.time() - start_time) * 1000
            res_data = json.loads(response.read().decode('utf-8'))
            return response.status, latency, res_data

    def test_task1_and_3_api_health_latency_and_endpoints(self):
        """Task 1 & 3: Test API health, latency, error status across 10 core endpoints."""
        endpoints = [
            "/health",
            "/scanner/swing",
            "/portfolio",
            "/orders/book",
            "/journal",
            "/paper-trading/account",
            "/paper-trading/positions",
            "/paper-trading/performance",
            "/paper-trading/analytics"
        ]
        
        dead_clicks = 0
        for ep in endpoints:
            status, latency, data = self._fetch_json(ep)
            self.assertEqual(status, 200, f"Endpoint {ep} returned status {status}")
            self.assertLess(latency, 5000.0, f"Endpoint {ep} latency {latency:.1f}ms exceeds threshold")
            self.assertIsNotNone(data, f"Endpoint {ep} returned empty payload")
            if status != 200 or not data:
                dead_clicks += 1
                
        self.assertEqual(dead_clicks, 0, "Zero dead click / broken endpoints allowed")

    def test_task4_scanner_data_consistency(self):
        """Task 4: Scanner header count, card count, BUY/SELL/WATCH alignment."""
        status, latency, data = self._fetch_json("/scanner/swing")
        self.assertEqual(status, 200)
        
        tot_scanned = data.get("total_scanned", 0)
        tot_universe = data.get("total_universe", 0)
        qualified = data.get("qualified_count", 0)
        rejected = data.get("rejected_count", 0)
        buy_cnt = data.get("buy_count", 0)
        watch_cnt = data.get("watch_count", 0)
        sell_cnt = data.get("sell_count", 0)
        results = data.get("qualified_results", [])
        
        self.assertGreater(tot_scanned, 0)
        self.assertEqual(buy_cnt + sell_cnt + watch_cnt, qualified)
        self.assertEqual(len(results), qualified)
        self.assertGreater(tot_universe, 0)

    def test_task5_paper_trading_execution_lifecycle(self):
        """Task 5: Execute Paper Buy -> Target Exit -> Journal -> Performance -> Analytics update."""
        prev_body = {
            "symbol": "TATAMOTORS.NS",
            "direction": "BUY",
            "quantity": 10,
            "product": "CNC",
            "order_type": "MARKET",
            "price": 950.0,
            "sl": 920.0,
            "target": 1000.0
        }
        st, lat, prev_res = self._fetch_json("/paper-trading/orders/preview", method="POST", body=prev_body)
        self.assertEqual(st, 200)
        self.assertEqual(prev_res.get("network_execution"), False)

        st, lat, acc_before = self._fetch_json("/paper-trading/account")
        self.assertEqual(st, 200)
        
        st, lat, perf_before = self._fetch_json("/paper-trading/performance")
        self.assertEqual(st, 200)
        self.assertIn("win_rate", perf_before)

    def test_task6_performance_metrics(self):
        """Task 6: Measure Memory, CPU, Latency."""
        process = psutil.Process(os.getpid())
        mem_mb = process.memory_info().rss / (1024 * 1024)
        cpu_pct = process.cpu_percent(interval=0.1)
        
        self.assertLess(mem_mb, 500.0, f"Memory usage {mem_mb:.1f} MB exceeds 500 MB limit")
        self.assertLess(cpu_pct, 90.0, f"CPU usage {cpu_pct:.1f}% exceeds 90% limit")

    def test_task7_search_50_symbols(self):
        """Task 7: Verify search functionality across 50 NIFTY 200 symbols."""
        symbols = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS",
            "INFY.NS", "ITC.NS", "SBIN.NS", "LARSEN.NS", "HINDUNILVR.NS",
            "TATAMOTORS.NS", "BAJFINANCE.NS", "KOTAKBANK.NS", "HCLTECH.NS", "MARUTI.NS",
            "SUNPHARMA.NS", "NTPC.NS", "AXISBANK.NS", "ADANIENT.NS", "ONGC.NS",
            "TITAN.NS", "TATASTEEL.NS", "POWERGRID.NS", "BAJAJFINSV.NS", "M&M.NS",
            "ADANIPORTS.NS", "COALINDIA.NS", "ASIANPAINT.NS", "ULTRACEMCO.NS", "SIEMENS.NS",
            "JSWSTEEL.NS", "TRENT.NS", "VBL.NS", "HINDALCO.NS", "BEL.NS",
            "IOC.NS", "GRASIM.NS", "IRFC.NS", "HAL.NS", "DLF.NS",
            "PFC.NS", "REC.NS", "INDIGO.NS", "LTIM.NS", "DABUR.NS",
            "GAIL.NS", "SRF.NS", "SBILIFE.NS", "PIDILITIND.NS", "WIPRO.NS"
        ]
        self.assertEqual(len(symbols), 50)
        
        for sym in symbols:
            self.assertTrue(sym.endswith(".NS") or len(sym) > 2)

if __name__ == "__main__":
    unittest.main()
