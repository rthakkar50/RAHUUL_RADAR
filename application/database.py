import sqlite3
import os
from datetime import datetime
import random
from config.settings import BASE_DIR
from utils.logger import get_logger

class DatabaseManager:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.db_path = os.path.join(str(BASE_DIR), 'radar.db')
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._enable_wal_and_timeouts()
        self._create_table()

    def _enable_wal_and_timeouts(self):
        """Enable Write-Ahead Logging (WAL) and set safe production busy timeout pragma."""
        cursor = self._conn.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.execute("PRAGMA busy_timeout=5000;")
            self._conn.commit()
        except Exception as e:
            try:
                self._conn.rollback()
            except Exception:
                pass
            self.logger.error(f"Failed to configure database PRAGMAs: {e}. Rollback executed.")
            raise e
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    def _create_table(self):
        cursor = self._conn.cursor()
        try:
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
                
            self._conn.commit()
        except Exception as e:
            try:
                self._conn.rollback()
            except Exception:
                pass
            self.logger.error(f"Table creation transaction failed: {e}. Rollback executed.")
            raise e
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    def insert_trade(self, symbol, signal, entry, sl, target, result="PENDING", return_pct="--", score=0, grade="N/A", category="SWING"):
        cursor = self._conn.cursor()
        try:
            date_str = datetime.now().strftime("%d-%b")
            cursor.execute('''
                INSERT INTO trades (date, symbol, signal, entry, sl, target, result, return_pct, score, grade, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (date_str, symbol, signal, entry, sl, target, result, return_pct, score, grade, category))
            self._conn.commit()
        except Exception as e:
            try:
                self._conn.rollback()
            except Exception:
                pass
            self.logger.error(f"Transaction failed in insert_trade for {symbol}: {e}. Rollback executed.")
            raise e
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    def update_trade_result(self, trade_id, result, return_pct):
        cursor = self._conn.cursor()
        try:
            cursor.execute('''
                UPDATE trades SET result = ?, return_pct = ? WHERE id = ?
            ''', (result, return_pct, trade_id))
            self._conn.commit()
        except Exception as e:
            try:
                self._conn.rollback()
            except Exception:
                pass
            self.logger.error(f"Transaction failed in update_trade_result for ID {trade_id}: {e}. Rollback executed.")
            raise e
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    def get_all_trades(self):
        cursor = self._conn.cursor()
        try:
            cursor.execute('SELECT id, date, symbol, signal, entry, sl, target, result, return_pct, score, grade, category FROM trades ORDER BY id DESC')
            return cursor.fetchall()
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        
    def get_performance_stats(self):
        """Aggregates win rate by Score Bracket and Quality Grade."""
        cursor = self._conn.cursor()
        try:
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
            
            return {"by_grade": grade_stats, "by_score": score_stats}
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    # --- SPRINT-72 Master AI Engine Methods ---
    
    def log_ai_decision(self, symbol, signal, reasons, score, status, result="PENDING"):
        cursor = self._conn.cursor()
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO master_ai_decisions (timestamp, symbol, signal, reasons, score, status, result)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, symbol, signal, reasons, score, status, result))
            self._conn.commit()
        except Exception as e:
            try:
                self._conn.rollback()
            except Exception:
                pass
            self.logger.error(f"Transaction failed in log_ai_decision for {symbol}: {e}. Rollback executed.")
            raise e
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        
    def insert_ai_decision(self, symbol, signal, reasons, score, status, result="PENDING"):
        """Alias for log_ai_decision to ensure backward compatibility and consistency."""
        return self.log_ai_decision(symbol, signal, reasons, score, status, result)
        
    def update_ai_decision_result(self, decision_id, result):
        cursor = self._conn.cursor()
        try:
            cursor.execute('UPDATE master_ai_decisions SET result = ? WHERE id = ?', (result, decision_id))
            self._conn.commit()
        except Exception as e:
            try:
                self._conn.rollback()
            except Exception:
                pass
            self.logger.error(f"Transaction failed in update_ai_decision_result for ID {decision_id}: {e}. Rollback executed.")
            raise e
        finally:
            try:
                cursor.close()
            except Exception:
                pass
        
    def get_ai_performance_stats(self):
        cursor = self._conn.cursor()
        try:
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
            
            acc_win_rate = (acc_stats[1] / acc_stats[0] * 100) if acc_stats and acc_stats[0] > 0 else 0
            rej_win_rate = (rej_stats[1] / rej_stats[0] * 100) if rej_stats and rej_stats[0] > 0 else 0
            
            return {
                "accepted_win_rate": round(acc_win_rate, 2),
                "rejected_win_rate": round(rej_win_rate, 2),
                "average_score": round(avg_score, 2) if avg_score else 0.0,
                "total_accepted": acc_stats[0] if acc_stats else 0,
                "total_rejected": rej_stats[0] if rej_stats else 0
            }
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    def close(self):
        """Close the persistent SQLite database connection when cleanly shutting down."""
        if hasattr(self, '_conn') and self._conn:
            try:
                self._conn.close()
            except Exception:
                pass

