import unittest
from unittest.mock import MagicMock
from market.paytm_provider import PaytmMoneyProvider

class TestFix5BPaytmIntradayForwarding(unittest.TestCase):
    def setUp(self):
        # Create provider instance
        self.provider = PaytmMoneyProvider()
        # Mock the fallback provider
        self.mock_fallback = MagicMock()
        self.mock_fallback.get_ohlcv.return_value = []
        self.provider.fallback = self.mock_fallback

    def test_forwarding_5m_5d(self):
        """
        Fix #5B verification:
        When get_intraday is called with 5m/5d, it MUST forward interval='5m' and period='5d'
        to fallback.get_ohlcv() instead of dropping them and falling back to 1d/3mo defaults.
        """
        self.mock_fallback.reset_mock()
        self.provider.get_intraday("TEST.NS", interval="5m", period="5d")
        
        self.mock_fallback.get_ohlcv.assert_called_once_with(
            "TEST.NS",
            interval="5m",
            period="5d"
        )

    def test_forwarding_15m_5d(self):
        """
        Verify multi-timeframe 15m/5d is forwarded without alteration.
        """
        self.mock_fallback.reset_mock()
        self.provider.get_intraday("TEST.NS", interval="15m", period="5d")
        
        self.mock_fallback.get_ohlcv.assert_called_once_with(
            "TEST.NS",
            interval="15m",
            period="5d"
        )

    def test_forwarding_1h_1mo(self):
        """
        Verify hourly 1h/1mo is forwarded without alteration.
        """
        self.mock_fallback.reset_mock()
        self.provider.get_intraday("TEST.NS", interval="1h", period="1mo")
        
        self.mock_fallback.get_ohlcv.assert_called_once_with(
            "TEST.NS",
            interval="1h",
            period="1mo"
        )

    def test_default_parameters_forwarding(self):
        """
        When called with default parameters (interval="15m", period="5d"),
        those defaults MUST be forwarded to fallback.get_ohlcv.
        """
        self.mock_fallback.reset_mock()
        self.provider.get_intraday("TEST.NS")
        
        self.mock_fallback.get_ohlcv.assert_called_once_with(
            "TEST.NS",
            interval="15m",
            period="5d"
        )

if __name__ == "__main__":
    unittest.main()
