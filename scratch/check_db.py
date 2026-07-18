import sqlite3
import pandas as pd

def check_db(db_path):
    print(f"Checking {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
        for t in tables['name']:
            try:
                df = pd.read_sql(f"SELECT * FROM {t}", conn)
                # find columns that might be symbol
                sym_cols = [c for c in df.columns if 'sym' in c.lower() or 'asset' in c.lower() or 'ticker' in c.lower()]
                for c in sym_cols:
                    matches = df[df[c].astype(str).str.contains("DIVISLAB|EXIDEIND|FEDERALBNK|NTPC", na=False)]
                    if not matches.empty:
                        print(f"Found in {t}:")
                        print(matches.to_string())
            except Exception as e:
                pass
        conn.close()
    except Exception as e:
        print("Error reading db:", e)

check_db("data/trade_journal.db")
check_db("data/paper_trading.db")
check_db("data/radar.db")
