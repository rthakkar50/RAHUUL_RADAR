import sys
import psutil
import os
import time
import logging

from application.swing_scanner_service import SwingScannerService
from utils.logger import get_logger

logger = get_logger("StressTest")
logger.setLevel(logging.CRITICAL)

def test_memory():
    process = psutil.Process(os.getpid())
    mem_start = process.memory_info().rss / 1024 / 1024
    print(f"Start Mem: {mem_start:.2f} MB")
    
    for i in range(1, 101):
        service = SwingScannerService()
        res = service.execute_swing_scan()
        if i % 25 == 0:
            mem = process.memory_info().rss / 1024 / 1024
            print(f"Iteration {i}: Mem = {mem:.2f} MB")
            
    mem_end = process.memory_info().rss / 1024 / 1024
    print(f"End Mem: {mem_end:.2f} MB. Diff: {mem_end - mem_start:.2f} MB")
    
    if (mem_end - mem_start) < 50:
        print("STRESS TEST: PASS")
    else:
        print("STRESS TEST: FAIL (Potential Leak)")

if __name__ == "__main__":
    test_memory()
