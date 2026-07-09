import sqlite3
import os
from datetime import datetime
import random
from config.settings import BASE_DIR

class DatabaseManager:
    def __init__(self):
        self.db_path = os.path.join(str(BASE_DIR), 'radar.db')
        self._create_table()

    def _create_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                symbol TEXT,
                signal TEXT,
                entry REAL,
                sl REAL,
                target REAL,
                result TEXT,
                return_pct TEXT,
                score REAL DEFAULT 0,
                grade TEXT DEFAULT 'N/A',
                category TEXT DEFAULT 'SWING'
            )
        ''')
        # Add new columns if they don't exist (SQLite patch for existing DB)
        try:
            cursor.execute("ALTER TABLE trades ADD COLUMN score REAL DEFAULT 0")
            cursor.execute("ALTER TABLE trades ADD COLUMN grade TEXT DEFAULT 'N/A'")
            cursor.execute("ALTER TABLE trades ADD COLUMN category TEXT DEFAULT 'SWING'")
        except sqlite3.OperationalError:
            pass # Columns already exist
            
        # SPRINT-72: Master AI Decisions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS master_ai_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                signal TEXT,
                reasons TEXT,
                score REAL,
                status TEXT,
                result TEXT DEFAULT 'PENDING'
            )
        ''')
            
        conn.commit()
        conn.close()

    def insert_trade(self, symbol, signal, entry, sl, target, result="PENDING", return_pct="--", score=0, grade="N/A", category="SWING"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        date_str = datetime.now().strftime("%d-%b")
        
        cursor.execute('''
            INSERT INTO trades (date, symbol, signal, entry, sl, target, result, return_pct, score, grade, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date_str, symbol, signal, entry, sl, target, result, return_pct, score, grade, category))
        conn.commit()
        conn.close()

    def update_trade_result(self, trade_id, result, return_pct):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE trades SET result = ?, return_pct = ? WHERE id = ?
        ''', (result, return_pct, trade_id))
        conn.commit()
        conn.close()

    def get_all_trades(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, date, symbol, signal, entry, sl, target, result, return_pct, score, grade, category FROM trades ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        return rows
        
    def get_performance_stats(self):
        """Aggregates win rate by Score Bracket and Quality Grade."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Win rate by Grade
        cursor.execute('''
            SELECT grade, 
                   COUNT(*) as total, 
                   SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END) as wins 
            FROM trades 
            WHERE result IN ('WIN', 'LOSS') 
            GROUP BY grade
        ''')
        grade_stats = cursor.fetchall()
        
        # Win rate by Score Range
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN score >= 95 THEN '95-100'
                    WHEN score >= 90 THEN '90-94'
                    WHEN score >= 80 THEN '80-89'
                    ELSE '< 80'
                END as score_bracket,
                COUNT(*) as total,
                SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END) as wins
            FROM trades
            WHERE result IN ('WIN', 'LOSS')
            GROUP BY score_bracket
        ''')
        score_stats = cursor.fetchall()
        
        conn.close()
        return {"by_grade": grade_stats, "by_score": score_stats}

    # --- SPRINT-72 Master AI Engine Methods ---
    
    def log_ai_decision(self, symbol, signal, reasons, score, status, result="PENDING"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO master_ai_decisions (timestamp, symbol, signal, reasons, score, status, result)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, symbol, signal, reasons, score, status, result))
        conn.commit()
        conn.close()
        
    def update_ai_decision_result(self, decision_id, result):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE master_ai_decisions SET result = ? WHERE id = ?', (result, decision_id))
        conn.commit()
        conn.close()
        
    def get_ai_performance_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Accepted Win Rate
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END) as wins
            FROM master_ai_decisions
            WHERE status='ACCEPTED' AND result IN ('WIN', 'LOSS')
        ''')
        acc_stats = cursor.fetchone()
        
        # Rejected Win Rate (To measure opportunity cost / if AI was wrong to reject)
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END) as wins
            FROM master_ai_decisions
            WHERE status='REJECTED' AND result IN ('WIN', 'LOSS')
        ''')
        rej_stats = cursor.fetchone()
        
        # Average AI Score
        cursor.execute('SELECT AVG(score) FROM master_ai_decisions')
        avg_score = cursor.fetchone()[0]
        
        conn.close()
        
        acc_win_rate = (acc_stats[1] / acc_stats[0] * 100) if acc_stats and acc_stats[0] > 0 else 0
        rej_win_rate = (rej_stats[1] / rej_stats[0] * 100) if rej_stats and rej_stats[0] > 0 else 0
        
        return {
            "accepted_win_rate": round(acc_win_rate, 2),
            "rejected_win_rate": round(rej_win_rate, 2),
            "average_score": round(avg_score, 2) if avg_score else 0.0,
            "total_accepted": acc_stats[0] if acc_stats else 0,
            "total_rejected": rej_stats[0] if rej_stats else 0
        }

