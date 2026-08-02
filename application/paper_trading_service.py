import sqlite3
import logging
from datetime import datetime
import pandas as pd
from PySide6.QtCore import QObject, Signal

from core.paper_portfolio_engine import PaperPortfolioEngine
from core.models.paper_portfolio_models import PaperPosition

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
        self.db_path = "data/paper_trading.db"
        
        # We assume config is already loaded globally or we load a fresh instance
        from config.config import AppConfig
        conf = AppConfig()
        conf.load()
        
        # Instantiate the Core Engine
        self.engine = PaperPortfolioEngine(
            starting_capital=conf.paper_trading_starting_capital,
            max_open_positions=conf.paper_trading_max_open_positions,
            max_risk_per_trade_pct=conf.paper_trading_max_risk_per_trade_pct,
            max_exposure_pct=conf.paper_trading_max_exposure_pct
        )
        
        self._init_db()
        self._load_state()

    def _init_db(self):
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
            target_1 REAL,
            target_2 REAL,
            target_3 REAL,
            sl REAL,
            trailing_stop REAL,
            time_exit_dt TEXT,
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
        
        # Load capital
        c.execute("SELECT capital FROM portfolio ORDER BY id DESC LIMIT 1")
        res = c.fetchone()
        if res:
            self.engine.virtual_capital = res[0]
            self.engine.realized_pnl = res[0] - self.engine.starting_capital
            self.engine.available_cash = res[0]
            
        # Load open positions
        c.execute("SELECT * FROM positions WHERE status='OPEN'")
        rows = c.fetchall()
        cols = [description[0] for description in c.description]
        
        for r in rows:
            pos_dict = dict(zip(cols, r))
            pos = PaperPosition(
                position_id=pos_dict['id'],
                symbol=pos_dict['symbol'],
                direction=pos_dict['direction'],
                qty=pos_dict['qty'],
                entry_price=pos_dict['entry_price'],
                current_price=pos_dict['cmp'],
                sl=pos_dict['sl'],
                target=pos_dict['target'],
                target_1=pos_dict.get('target_1', 0.0) or 0.0,
                target_2=pos_dict.get('target_2', 0.0) or 0.0,
                target_3=pos_dict.get('target_3', 0.0) or 0.0,
                trailing_stop=pos_dict.get('trailing_stop', 0.0) or 0.0,
                time_exit_dt=pos_dict.get('time_exit_dt', None),
                status='OPEN',
                used_margin=pos_dict['qty'] * pos_dict['entry_price'],
                charges=pos_dict['charges']
            )
            self.engine.open_positions[pos.position_id] = pos
            
        conn.close()
        
        # Sync engine state
        self.engine.used_margin = sum(p.used_margin for p in self.engine.open_positions.values())
        self.engine.available_cash = max(0.0, self.engine.virtual_capital - self.engine.used_margin)
        self._emit_portfolio_update()

    def _emit_portfolio_update(self):
        state = self.engine.get_portfolio_state()
        
        # Map to old dict format for UI compatibility
        summary = {
            "capital": state.virtual_capital,
            "margin": state.used_margin,
            "open_pnl": state.unrealized_pnl,
            "closed_pnl": state.realized_pnl,
            "today_pnl": state.unrealized_pnl + state.realized_pnl,
            "total_return": state.total_equity - self.engine.starting_capital
        }
        self.signals.portfolio_updated.emit(summary)

    def execute_trade(self, symbol, direction, price, sl, target, order_type=OrderType.MARKET, sizing=PositionSizing.AUTO_RISK):
        success, pos_id, msg = self.engine.execute_trade(symbol, direction, price, sl, target)
        
        if not success:
            self.signals.notification.emit("Risk Rejected", msg)
            return None
            
        self.signals.notification.emit("Order Executed", msg)
        pos = self.engine.open_positions[pos_id]
        
        # DB Persistence
        self._save_position(pos)
        self._save_portfolio()
        
        # Map for UI
        pos_dict = {
            'id': pos.position_id,
            'symbol': pos.symbol,
            'direction': pos.direction,
            'qty': pos.qty,
            'cmp': pos.current_price,
            'pnl': pos.unrealized_pnl,
            'net_pnl': pos.unrealized_pnl - pos.charges
        }
        
        self.signals.order_executed.emit(pos_dict)
        self._emit_portfolio_update()
        return pos_id

    def update_market_price(self, symbol, cmp):
        state, exits = self.engine.update_market_prices({symbol: cmp})
        
        # Check what was closed during the update
        open_ids_now = set(self.engine.open_positions.keys())
        
        # We need to sync the UI for updated positions
        for pid, pos in self.engine.open_positions.items():
            if pos.symbol == symbol:
                pos_dict = {
                    'id': pos.position_id,
                    'symbol': pos.symbol,
                    'direction': pos.direction,
                    'qty': pos.qty,
                    'cmp': pos.current_price,
                    'pnl': pos.unrealized_pnl,
                    'net_pnl': pos.unrealized_pnl - pos.charges
                }
                self.signals.position_updated.emit(pos_dict)
                self._save_position(pos) # Save partial updates or trailing stop changes
                
        # Emit notifications for the exits
        for pid, exit_price, reason, close_qty in exits:
            is_partial = False
            if pid in open_ids_now:
                is_partial = True
                
            if is_partial:
                self._save_portfolio()
                self.signals.notification.emit("Partial Exit", f"{symbol} partially closed ({close_qty} qty): {reason}")
            
        # Let's save all recently closed positions
        for pos in self.engine.closed_positions:
            if pos.symbol == symbol and pos.exit_price == cmp: # Just closed in this tick
                self._save_position(pos)
                self._save_portfolio()
                self.signals.notification.emit("Position Closed", f"{pos.symbol} closed. PNL: {pos.realized_pnl:.2f}")

        self._emit_portfolio_update()

    def close_position(self, pos_id, exit_price, reason="Manual"):
        if pos_id in self.engine.open_positions:
            self.engine.close_position(pos_id, exit_price, reason)
            
            # The last closed position
            pos = self.engine.closed_positions[-1]
            self._save_position(pos)
            self._save_portfolio()
            
            self._emit_portfolio_update()
            self.signals.notification.emit("Position Closed", f"{pos.symbol} closed: {reason} PNL: {pos.realized_pnl:.2f}")

    def has_open_position(self, symbol: str) -> bool:
        """
        Returns True if an OPEN position already exists for the given symbol.
        Prevents duplicate paper trades.
        """
        symbol = symbol.upper().strip()

        for pos in self.engine.open_positions.values():
            if (
                pos.symbol.upper().strip() == symbol
                and getattr(pos, "status", "OPEN") == "OPEN"
            ):
                return True

        return False

    def _save_position(self, p: PaperPosition):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO positions 
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            p.position_id, p.symbol, OrderType.MARKET, p.direction, p.qty,
            p.entry_price, p.current_price, p.target, p.target_1, p.target_2, p.target_3,
            p.sl, p.trailing_stop, p.time_exit_dt, p.status,
            p.entry_time, p.exit_price, p.exit_time, p.unrealized_pnl + p.realized_pnl, p.charges, p.realized_pnl if p.status == 'CLOSED' else p.unrealized_pnl - p.charges
        ))
        conn.commit()
        conn.close()
        
    def _save_portfolio(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO portfolio (capital, date) VALUES (?, ?)", 
                 (self.engine.virtual_capital, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

    def get_statistics(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM positions WHERE status='CLOSED'")
        closed_rows = [dict(r) for r in c.fetchall()]
        c.execute("SELECT * FROM positions WHERE status='OPEN'")
        open_rows = [dict(r) for r in c.fetchall()]
        conn.close()

        total_trades = len(closed_rows) + len(open_rows)
        closed_trades = len(closed_rows)
        open_trades = len(open_rows)

        if closed_trades == 0:
            return {
                "total_trades": total_trades,
                "closed_trades": 0,
                "open_trades": open_trades,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "loss_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
                "expectancy": 0.0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0,
                "sortino_ratio": 0.0,
                "largest_winner": 0.0,
                "largest_loser": 0.0
            }

        wins = [float(r.get("net_pnl") or r.get("pnl") or 0.0) for r in closed_rows if float(r.get("net_pnl") or r.get("pnl") or 0.0) > 0]
        losses = [abs(float(r.get("net_pnl") or r.get("pnl") or 0.0)) for r in closed_rows if float(r.get("net_pnl") or r.get("pnl") or 0.0) < 0]

        winning_trades = len(wins)
        losing_trades = len(losses)

        win_rate = (winning_trades / closed_trades * 100.0) if closed_trades > 0 else 0.0
        loss_rate = (losing_trades / closed_trades * 100.0) if closed_trades > 0 else 0.0

        avg_win = (sum(wins) / winning_trades) if winning_trades > 0 else 0.0
        avg_loss = (sum(losses) / losing_trades) if losing_trades > 0 else 0.0

        # Mathematical Guardrails (Task 4)
        if winning_trades == 0:
            profit_factor = 0.0
        elif losing_trades == 0:
            profit_factor = round(sum(wins), 2)
        else:
            profit_factor = round(sum(wins) / sum(losses), 2)

        win_prob = win_rate / 100.0
        loss_prob = loss_rate / 100.0
        expectancy = (win_prob * avg_win) - (loss_prob * avg_loss)

        std_dev = (sum((w - avg_win) ** 2 for w in wins) / max(1, len(wins))) ** 0.5 if wins else 1.0
        sharpe = round((expectancy / (std_dev + 1.0)) * 1.5, 2)
        sortino = round((expectancy / (avg_loss + 1.0)) * 1.8, 2)

        largest_winner = max(wins, default=0.0)
        largest_loser = max(losses, default=0.0)

        history_df = self.get_portfolio_history()
        max_dd = 0.0
        if not history_df.empty and 'capital' in history_df.columns:
            equity = history_df['capital']
            peak = equity.cummax()
            drawdown = (equity - peak) / peak * 100
            max_dd = drawdown.min()
            if str(max_dd) == 'nan': max_dd = 0.0

        return {
            "total_trades": total_trades,
            "closed_trades": closed_trades,
            "open_trades": open_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round(win_rate, 2),
            "loss_rate": round(loss_rate, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": profit_factor,
            "expectancy": round(expectancy, 2),
            "max_drawdown": round(max_dd, 2),
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "largest_winner": round(largest_winner, 2),
            "largest_loser": round(largest_loser, 2)
        }

    def get_portfolio_history(self):
        """
        Returns a DataFrame of the portfolio capital over time for the equity curve.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql("SELECT capital, date FROM portfolio ORDER BY date ASC", conn)
        except sqlite3.OperationalError:
            df = pd.DataFrame(columns=['capital', 'date'])
        conn.close()
        return df
