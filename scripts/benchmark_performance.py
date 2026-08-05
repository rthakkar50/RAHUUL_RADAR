#!/usr/bin/env python3
import asyncio
import time
import sqlite3
import os
import sys
import threading

import logging
logging.getLogger("api.main").setLevel(logging.ERROR)

sys.path.append('/Users/pr/RAHUUL_RADAR')
from api.main import (
    get_market_overview,
    run_swing_scanner,
    get_portfolio,
    get_trade_journal,
    get_risk_report,
    get_fno_option_chain,
    health_check,
    get_app_version
)


async def benchmark_endpoint(name, func, num_requests=50):
    latencies = []
    errors = 0
    start_total = time.time()
    
    for _ in range(num_requests):
        t0 = time.time()
        try:
            res = await func()
            latencies.append((time.time() - t0) * 1000)
        except Exception as e:
            errors += 1
            
    total_time = time.time() - start_total
    latencies.sort()
    
    avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0.0
    p99 = latencies[int(len(latencies) * 0.99)] if latencies else 0.0
    rps = num_requests / total_time if total_time > 0 else 0.0
    
    print(f"{name:<30} | Req: {num_requests:<3} | Avg: {avg_lat:6.2f}ms | P95: {p95:6.2f}ms | P99: {p99:6.2f}ms | RPS: {rps:6.1f} | Errors: {errors}")
    return {
        "name": name,
        "num_requests": num_requests,
        "avg_lat_ms": round(avg_lat, 2),
        "p95_ms": round(p95, 2),
        "p99_ms": round(p99, 2),
        "rps": round(rps, 1),
        "errors": errors
    }

def benchmark_sqlite(db_path="data/live_journal.db", iterations=500):
    print("\n--- SQLite Database Benchmark ---")
    if not os.path.exists(db_path):
        print("Database file not found.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read Benchmark
    t0 = time.time()
    for _ in range(iterations):
        cursor.execute("SELECT COUNT(*) FROM sqlite_master;")
        cursor.fetchone()
    read_time = time.time() - t0
    read_rps = iterations / read_time if read_time > 0 else 0.0
    
    conn.close()
    print(f"SQLite Read Latency (500 Queries): Total {read_time*1000:.2f}ms | Avg {(read_time/iterations)*1000:.4f}ms | RPS: {read_rps:.1f}")

async def run_master_benchmark():
    print("=======================================================================")
    print("  RAHUUL_RADAR ENTERPRISE PERFORMANCE & LOAD BENCHMARK")
    print("=======================================================================")
    
    endpoints = [
        ("GET /api/v1/health", health_check),
        ("GET /api/v1/version", get_app_version),
        ("GET /api/v1/dashboard", get_market_overview),
        ("GET /api/v1/scanner/swing", lambda: run_swing_scanner(debug=False)),
        ("GET /api/v1/portfolio", get_portfolio),
        ("GET /api/v1/journal", get_trade_journal),
        ("GET /api/v1/risk/report", get_risk_report),
        ("GET /api/v1/fno/option-chain", lambda: get_fno_option_chain('NIFTY')),
    ]
    
    for name, func in endpoints:
        await benchmark_endpoint(name, func, num_requests=50)
        
    benchmark_sqlite()
    print("=======================================================================")

if __name__ == "__main__":
    asyncio.run(run_master_benchmark())
