import datetime
from core.market_regime_engine import MarketRegimeEngine
from application.data_manager import DataManager

class MarketEnvironment:
    """
    Evaluates 12 specific market conditions:
    Strong Bull Trend, Bull Trend, Strong Bear Trend, Bear Trend,
    Sideways Range, Low Volatility, High Volatility, Gap Up Trend Day,
    Gap Down Trend Day, Reversal Day, Breakout Day, Expiry Day
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        self.regime_engine = MarketRegimeEngine()
        self.data_manager = DataManager.get_instance()
        self.current_env = "Unknown"
        self.volatility = "Normal"
        self.last_update = None
        self.atr_val = 0.0
        
    def get_environment(self):
        # Refresh every 5 mins
        if self.last_update is None or (datetime.datetime.now() - self.last_update).total_seconds() > 300:
            self._evaluate()
        return {
            "environment": self.current_env,
            "volatility": self.volatility,
            "atr": self.atr_val
        }
        
    def _evaluate(self):
        # Get base regime
        base_regime = self.regime_engine.get_current_regime()
        
        try:
            df = self.data_manager.get_historical_data("^NSEI", period="1mo", interval="1d")
            if df.empty or len(df) < 5:
                self.current_env = base_regime
                return
                
            today = df.iloc[-1]
            yesterday = df.iloc[-2]
            
            # Volatility
            df['tr1'] = df['High'] - df['Low']
            df['tr2'] = abs(df['High'] - df['Close'].shift(1))
            df['tr3'] = abs(df['Low'] - df['Close'].shift(1))
            df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
            atr = df['tr'].rolling(14).mean().iloc[-1] if len(df) >= 14 else df['tr'].mean()
            self.atr_val = atr
            
            atr_pct = (atr / today['Close']) * 100
            
            if atr_pct > 2.0:
                self.volatility = "High Volatility"
            elif atr_pct < 1.0:
                self.volatility = "Low Volatility"
            else:
                self.volatility = "Normal"
                
            # Expiry Day (Thursday for NIFTY)
            # 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri
            is_expiry = datetime.datetime.today().weekday() == 3
            
            # Gaps
            gap_pct = ((today['Open'] - yesterday['Close']) / yesterday['Close']) * 100
            is_gap_up = gap_pct > 0.5
            is_gap_down = gap_pct < -0.5
            
            # Reversal
            # If gap up but close < open, or yesterday was strong down and today gap up
            is_reversal = (today['Open'] > yesterday['Close'] and today['Close'] < today['Open']) or \
                          (today['Open'] < yesterday['Close'] and today['Close'] > today['Open'])
                          
            # Breakout
            # Simple 20-day high breakout
            high_20 = df['High'].iloc[-20:-1].max() if len(df) >= 20 else 0
            low_20 = df['Low'].iloc[-20:-1].min() if len(df) >= 20 else 0
            is_breakout = today['Close'] > high_20 or today['Close'] < low_20
            
            # Determine specific override day types
            if is_expiry:
                self.current_env = "Expiry Day"
            elif is_gap_up and today['Close'] > today['Open']:
                self.current_env = "Gap Up Trend Day"
            elif is_gap_down and today['Close'] < today['Open']:
                self.current_env = "Gap Down Trend Day"
            elif is_breakout:
                self.current_env = "Breakout Day"
            elif is_reversal:
                self.current_env = "Reversal Day"
            elif self.volatility == "High Volatility":
                self.current_env = "High Volatility"
            elif self.volatility == "Low Volatility":
                self.current_env = "Low Volatility"
            else:
                # Map base regime
                if "Strong Bull" in base_regime: self.current_env = "Strong Bull Trend"
                elif "Strong Bear" in base_regime: self.current_env = "Strong Bear Trend"
                elif "Bull" in base_regime: self.current_env = "Bull Trend"
                elif "Bear" in base_regime: self.current_env = "Bear Trend"
                elif "Sideways" in base_regime: self.current_env = "Sideways Range"
                else: self.current_env = base_regime
                
            self.last_update = datetime.datetime.now()
            
        except Exception as e:
            self.current_env = base_regime
