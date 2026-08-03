import re

candidates_raw = [
    ('DIVISLAB.NS', 92.55),
    ('LAURUSLABS.NS', 91.32),
    ('SUNPHARMA.NS', 90.16),
    ('BAJAJ-AUTO.NS', 90.04),
    ('M&MFIN.NS', 88.26),
    ('TECHM.NS', 87.92),
    ('KALYANKJIL.NS', 87.27),
    ('TITAN.NS', 86.58),
    ('BAJFINANCE.NS', 86.06),
    ('HEROMOTOCO.NS', 85.68),
    ('BAJAJFINSV.NS', 85.66),
    ('MARICO.NS', 85.14),
    ('FEDERALBNK.NS', 80.85),
    ('IDFCFIRSTB.NS', 79.26),
    ('BHARATFORG.NS', 77.63),
    ('DIXON.NS', 77.00),
    ('HCLTECH.NS', 75.79),
    ('BHARTIARTL.NS', 74.80),
    ('ATUL.NS', 72.00),
    ('OIL.NS', 57.00),
]

print("Top 20 BUY Candidates count:", len(candidates_raw))

# For candidates with 85 <= TQI < 90:
# M&MFIN.NS (88.26)
# TECHM.NS (87.92)
# KALYANKJIL.NS (87.27)
# TITAN.NS (86.58)
# BAJFINANCE.NS (86.06)
# HEROMOTOCO.NS (85.68)
# BAJAJFINSV.NS (85.66)
# MARICO.NS (85.14)

