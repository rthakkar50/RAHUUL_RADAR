import sqlite3
import uuid
import time
import json
import logging
from datetime import datetime
from PySide6.QtCore import QObject, Signal
import pandas as pd
import numpy as np

logger = logging.getLogger("PaperTradingEngine")

class OrderType:
    MARKET = "Market"
    LIMIT = "Limit"
    STOP_MARKET = "Stop Market"
    STOP_LIMIT = "Stop Limit"

class PositionSizing:
    AUTO_RISK = "Auto Risk %"
    FIXED_QTY = "Fixed Quantity"
    FIXED_CAPITAL = "Fixed Capital"

class PaperTradingSignals(QObject):
    portfolio_updated = Signal(dict)
    position_updated = Signal(dict)
    order_executed = Signal(dict)
    notification = Signal(str, str)

class PaperTradingEngine:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if PaperTradingEngine._instance is not None:
            raise Exception("Singleton class!")
            
        self.signals = PaperTradingSignals()
        
        # Portfolio Settings
        self.starting_capital = 1000000.0  # ₹10,00,000
        self.available_capital = self.starting_capital
        self.used_margin = 0.0
        
        # Risk Settings
        self.max_risk_per_trade_pct = 1.0 # 1% of capital
        self.daily_loss_limit = -20000.0
        self.max_open_positions = 5
        self.max_exposure_pct = 80.0
        
        self.active_positions = {}
        self.trade_history = []
        self.equity_curve = []
        
        self._init_db()
        self._load_state()

    def _init_db(self):
        self.db_path = "data/paper_trading.db"
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS positions (
            id TEXT PRIMARY KEY,
            symbol TEXT,
            order_type TEXT,
            direction TEXT,
            qty INTEGER,
            entry_price REAL,
            cmp REAL,
            target REAL,
            sl REAL,
            status TEXT,
            entry_time TEXT,
            exit_price REAL,
            exit_time TEXT,
            pnl REAL,
            charges REAL,
            net_pnl REAL
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY,
            capital REAL,
            date TEXT
        )''')
        conn.commit()
        conn.close()

    def _load_state(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM positions WHERE status='OPEN'")
        rows = c.fetchall()
        cols = [description[0] for description in c.description]
        
        for r in rows:
            pos = dict(zip(cols, r))
            self.active_positions[pos['id']] = pos
            
        # Load capital
        c.execute("SELECT capital FROM portfolio ORDER BY id DESC LIMIT 1")
        res = c.fetchone()
        if res:
            self.available_capital = res[0]
            
        conn.close()
        self._update_margin()

    def calculate_charges(self, qty, price, is_delivery=False):
        # Realistic Indian Equity Charges (Approximate)
        turnover = qty * price
        brokerage = min(20, turnover * 0.0003) if not is_delivery else 0
        stt = turnover * 0.00025 if not is_delivery else turnover * 0.001
        exchange = turnover * 0.0000345
        gst = (brokerage + exchange) * 0.18
        sebi = turnover * 0.000001
        stamp = turnover * 0.00003 if not is_delivery else turnover * 0.00015
        return brokerage + stt + exchange + gst + sebi + stamp

    def _update_margin(self):
        self.used_margin = sum(p['qty'] * p['entry_price'] for p in self.active_positions.values())
        self.signals.portfolio_updated.emit(self.get_portfolio_summary())

    def get_portfolio_summary(self):
        today = datetime.now().strftime("%Y-%m-%d")
        
        open_pnl = sum(
            (p['cmp'] - p['entry_price']) * p['qty'] if p['direction'] == 'BUY' else 
            (p['entry_price'] - p['cmp']) * p['qty']
            for p in self.active_positions.values()
        )
        
        # In a real scenario we'd query today's closed trades from DB
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT SUM(net_pnl) FROM positions WHERE status='CLOSED' AND exit_time LIKE ?", (today + "%",))
        closed_pnl = c.fetchone()[0] or 0.0
        conn.close()
        
        total_ret = self.available_capital + open_pnl - self.starting_capital
        
        return {
            "capital": self.available_capital,
            "margin": self.used_margin,
            "open_pnl": open_pnl,
            "closed_pnl": closed_pnl,
            "today_pnl": open_pnl + closed_pnl,
            "total_return": total_ret
        }

    def execute_trade(self, symbol, direction, price, sl, target, order_type=OrderType.MARKET, sizing=PositionSizing.AUTO_RISK):
        # Risk Check
        if len(self.active_positions) >= self.max_open_positions:
            self.signals.notification.emit("Risk Rejected", "Max open positions reached.")
            return None
            
        # Position Sizing
        risk_amount = self.available_capital * (self.max_risk_per_trade_pct / 100)
        price_risk = abs(price - sl)
        if price_risk <= 0: price_risk = price * 0.01 # Fallback 1% risk
        
        qty = int(risk_amount / price_risk)
        if qty <= 0: qty = 1
        
        trade_val = qty * price
        
        # Exposure Check
        if (self.used_margin + trade_val) > (self.available_capital * (self.max_exposure_pct / 100)):
            self.signals.notification.emit("Risk Rejected", "Max exposure limit exceeded.")
            return None
            
        # Execute
        pos_id = str(uuid.uuid4())[:8]
        charges = self.calculate_charges(qty, price)
        
        pos = {
            'id': pos_id,
            'symbol': symbol,
            'order_type': order_type,
            'direction': direction,
            'qty': qty,
            'entry_price': price,
            'cmp': price,
            'target': target,
            'sl': sl,
            'status': 'OPEN',
            'entry_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'exit_price': 0.0,
            'exit_time': "",
            'pnl': 0.0,
            'charges': charges,
            'net_pnl': -charges
        }
        
        self.available_capital -= charges
        self.active_positions[pos_id] = pos
        
        self._save_position(pos)
        self._update_margin()
        
        self.signals.order_executed.emit(pos)
        self.signals.notification.emit("Order Executed", f"{direction} {qty} {symbol} @ {price}")
        return pos_id

    def update_market_price(self, symbol, cmp):
        for pid, p in list(self.active_positions.items()):
            if p['symbol'] == symbol:
                p['cmp'] = cmp
                
                # Calc PNL
                if p['direction'] == 'BUY':
                    p['pnl'] = (cmp - p['entry_price']) * p['qty']
                else:
                    p['pnl'] = (p['entry_price'] - cmp) * p['qty']
                
                p['net_pnl'] = p['pnl'] - p['charges']
                
                # Auto Exit
                if p['direction'] == 'BUY':
                    if cmp >= p['target'] and p['target'] > 0: self.close_position(pid, cmp, "Target Hit")
                    elif cmp <= p['sl'] and p['sl'] > 0: self.close_position(pid, cmp, "SL Hit")
                else:
                    if cmp <= p['target'] and p['target'] > 0: self.close_position(pid, cmp, "Target Hit")
                    elif cmp >= p['sl'] and p['sl'] > 0: self.close_position(pid, cmp, "SL Hit")
                    
                self.signals.position_updated.emit(p)
                
        self.signals.portfolio_updated.emit(self.get_portfolio_summary())

    def close_position(self, pos_id, exit_price, reason="Manual"):
        if pos_id in self.active_positions:
            p = self.active_positions[pos_id]
            p['exit_price'] = exit_price
            p['exit_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            p['status'] = 'CLOSED'
            
            # Recalculate PnL and exit charges
            if p['direction'] == 'BUY': p['pnl'] = (exit_price - p['entry_price']) * p['qty']
            else: p['pnl'] = (p['entry_price'] - exit_price) * p['qty']
                
            exit_charges = self.calculate_charges(p['qty'], exit_price)
            p['charges'] += exit_charges
            p['net_pnl'] = p['pnl'] - p['charges']
            
            self.available_capital += p['net_pnl']
            
            self._save_position(p)
            self._save_portfolio()
            
            del self.active_positions[pos_id]
            self._update_margin()
            
            self.signals.notification.emit("Position Closed", f"{p['symbol']} closed: {reason} PNL: {p['net_pnl']:.2f}")

    def _save_position(self, p):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO positions 
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            p['id'], p['symbol'], p['order_type'], p['direction'], p['qty'],
            p['entry_price'], p['cmp'], p['target'], p['sl'], p['status'],
            p['entry_time'], p['exit_price'], p['exit_time'], p['pnl'], p['charges'], p['net_pnl']
        ))
        conn.commit()
        conn.close()
        
    def _save_portfolio(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO portfolio (capital, date) VALUES (?, ?)", 
                 (self.available_capital, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

    def get_statistics(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql("SELECT * FROM positions WHERE status='CLOSED'", conn)
        conn.close()
        
        if df.empty:
            return {}
            
        wins = df[df['net_pnl'] > 0]
        losses = df[df['net_pnl'] <= 0]
        
        win_rate = len(wins) / len(df) * 100
        loss_rate = len(losses) / len(df) * 100
        avg_win = wins['net_pnl'].mean() if not wins.empty else 0
        avg_loss = abs(losses['net_pnl'].mean()) if not losses.empty else 0
        profit_factor = (wins['net_pnl'].sum() / abs(losses['net_pnl'].sum())) if not losses.empty and losses['net_pnl'].sum() != 0 else 0
        
        # Max Drawdown simplified
        equity = self.starting_capital + df['net_pnl'].cumsum()
        peak = equity.cummax()
        drawdown = (equity - peak) / peak * 100
        max_dd = drawdown.min()
        
        return {
            "win_rate": round(win_rate, 2),
            "loss_rate": round(loss_rate, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2),
            "max_drawdown": round(max_dd, 2)
        }
