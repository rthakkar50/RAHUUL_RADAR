import unittest
from unittest.mock import MagicMock, patch
from scanner.scanner_engine import ScannerEngine
from data.stocks import Stock

class TestFix5AIntradayCallerParameters(unittest.TestCase):
    def setUp(self):
        self.mock_provider = MagicMock()
        # Return empty list so process_stock returns early with NO_DATA after calling get_ohlcv
        self.mock_provider.get_ohlcv.return_value = []
        
        self.trend_engine = MagicMock()
        self.momentum_engine = MagicMock()
        self.structure_engine = MagicMock()
        self.score_engine = MagicMock()
        
        self.scanner = ScannerEngine(
            data_provider=self.mock_provider,
            trend_engine=self.trend_engine,
            momentum_engine=self.momentum_engine,
            structure_engine=self.structure_engine,
            score_engine=self.score_engine
        )
        self.stock = Stock(
            symbol="TEST.NS",
            company_name="Test Stock",
            sector="IT",
            is_fno=True,
            is_nifty50=False
        )

    def test_case_a_mode_intraday_requests_5m_5d(self):
        """
        Fix #5A verification:
        When mode='INTRADAY', ScannerEngine MUST explicitly request interval='5m' and period='5d'.
        It must NOT call get_ohlcv(symbol) without interval/period.
        """
        self.mock_provider.reset_mock()
        self.scanner.scan_market([self.stock], mode="INTRADAY")
        
        # Verify get_ohlcv was called
        self.mock_provider.get_ohlcv.assert_called_once_with("TEST.NS", interval="5m", period="5d")
        
        # Extra assertion on kwargs
        args, kwargs = self.mock_provider.get_ohlcv.call_args
        self.assertEqual(args[0], "TEST.NS")
        self.assertEqual(kwargs.get("interval"), "5m")
        self.assertEqual(kwargs.get("period"), "5d")

    @patch("scanner.scanner_engine._fetch_india_vix", return_value=12.0)
    def test_case_b_mode_options_retains_5m_5d(self, mock_vix):
        """
        Verify mode='OPTIONS' behavior is preserved:
        Requests interval='5m', period='5d'.
        """
        self.mock_provider.reset_mock()
        self.scanner.scan_market([self.stock], mode="OPTIONS")
        
        # In OPTIONS mode, first call is base ohlcv_list at 5m/5d
        self.assertTrue(self.mock_provider.get_ohlcv.called)
        first_call = self.mock_provider.get_ohlcv.call_args_list[0]
        args, kwargs = first_call
        self.assertEqual(args[0], "TEST.NS")
        self.assertEqual(kwargs.get("interval"), "5m")
        self.assertEqual(kwargs.get("period"), "5d")

    def test_case_c_mode_swing_retains_1d_3mo(self):
        """
        Verify mode='SWING' (default) behavior is preserved:
        Requests interval='1d', period='3mo'.
        """
        self.mock_provider.reset_mock()
        self.scanner.scan_market([self.stock], mode="SWING")
        
        self.mock_provider.get_ohlcv.assert_called_once_with("TEST.NS", interval="1d", period="3mo")
        args, kwargs = self.mock_provider.get_ohlcv.call_args
        self.assertEqual(args[0], "TEST.NS")
        self.assertEqual(kwargs.get("interval"), "1d")
        self.assertEqual(kwargs.get("period"), "3mo")

if __name__ == "__main__":
    unittest.main()
