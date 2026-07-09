import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime

class AIPredictionEngine:
    """
    AI Prediction Engine using scikit-learn's RandomForestRegressor.
    Trains on historical technical features to predict future prices.
    """
    def __init__(self):
        self.model_5d = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
        self.is_trained = False
        
    def _calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates technical features for the model.
        Assumes df has 'Close', 'High', 'Low', 'Volume'.
        """
        df = df.copy()
        
        # Trend Features
        df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        
        df['Dist_EMA10'] = (df['Close'] - df['EMA_10']) / df['EMA_10']
        df['Dist_EMA50'] = (df['Close'] - df['EMA_50']) / df['EMA_50']
        
        # Momentum Features (RSI proxy)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        df['RSI'] = 100 - (100 / (1 + rs))
        df['RSI'] = df['RSI'].fillna(50)
        
        # Volatility Features
        df['Daily_Range'] = (df['High'] - df['Low']) / df['Close']
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA'].replace(0, np.nan)
        df['Volume_Ratio'] = df['Volume_Ratio'].fillna(1)
        
        # Returns
        df['Ret_1d'] = df['Close'].pct_change(1)
        df['Ret_3d'] = df['Close'].pct_change(3)
        
        return df
        
    def train_and_predict(self, ohlcv_list) -> dict:
        """
        Trains the model on the fly using the provided OHLCV data.
        Predicts the 5-day forward price.
        """
        if not ohlcv_list or len(ohlcv_list) < 60:
            return None
            
        df = pd.DataFrame([{
            'Date': c.timestamp,
            'Open': c.open,
            'High': c.high,
            'Low': c.low,
            'Close': c.close,
            'Volume': c.volume
        } for c in ohlcv_list])
        
        # Calculate Features
        df = self._calculate_features(df)
        
        # Target: Price 5 days from now
        df['Target_5d'] = df['Close'].shift(-5)
        
        # Prepare Training Data (Drop rows where Target is NaN and drop initial NaN rows)
        train_df = df.dropna(subset=['Target_5d', 'EMA_50', 'Ret_3d'])
        
        if len(train_df) < 20: # Not enough data
            return None
            
        features = ['Dist_EMA10', 'Dist_EMA50', 'RSI', 'Daily_Range', 'Volume_Ratio', 'Ret_1d', 'Ret_3d']
        X_train = train_df[features]
        y_train = train_df['Target_5d']
        
        # Train Model
        self.model_5d.fit(X_train, y_train)
        self.is_trained = True
        
        # Predict on the latest available data point
        latest_data = df.iloc[-1:]
        X_test = latest_data[features]
        
        # Make Prediction
        predicted_price_5d = self.model_5d.predict(X_test)[0]
        
        current_price = latest_data['Close'].values[0]
        percent_change = ((predicted_price_5d - current_price) / current_price) * 100
        
        direction = "UP" if percent_change > 0 else "DOWN"
        
        # Pseudo-confidence based on historical accuracy would be complex to backtest on the fly.
        # We will use a heuristic confidence based on model's R-squared on training data, clamped to reasonable bounds.
        score = self.model_5d.score(X_train, y_train) 
        confidence = min(max(int(score * 100), 50), 95) # Between 50% and 95%
        
        return {
            'predicted_price_5d': predicted_price_5d,
            'percent_change': percent_change,
            'direction': direction,
            'confidence': confidence,
            'current_price': current_price
        }
