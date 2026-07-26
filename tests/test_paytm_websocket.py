"""
Sprint M4.7 — WebSocket Watchdog Unit Tests
============================================
Tests for market/paytm_websocket.py
"""

import pytest
import time
import threading
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from market.paytm_websocket import PaytmLiveBroadcast


@pytest.fixture
def ws_client():
    """Reset singleton and return fresh PaytmLiveBroadcast instance."""
    PaytmLiveBroadcast._instance = None
    client = PaytmLiveBroadcast(stale_timeout=1.0)  # fast 1s timeout for testing
    yield client
    client.disconnect()
    PaytmLiveBroadcast._instance = None


class TestWebSocketWatchdog:

    def test_initial_state(self, ws_client):
        assert not ws_client.is_connected()
        assert ws_client.reconnect_count == 0
        assert ws_client.stale_timeout == 1.0

    def test_prevent_duplicate_sessions(self, ws_client):
        ws_client.set_token("TEST_TOKEN")
        ws_client._connected = True
        ws_client._is_connecting = True

        # Attempt connect when already connected/connecting
        ws_client.connect()

        # Thread loop should not start
        assert ws_client.ws_thread is None or not ws_client.ws_thread.is_alive()

    def test_subscription_management(self, ws_client):
        ws_client.subscribe(["1333", "2885"])
        assert "1333" in ws_client.subscribed_instruments
        assert "2885" in ws_client.subscribed_instruments

        ws_client.unsubscribe(["1333"])
        assert "1333" not in ws_client.subscribed_instruments
        assert "2885" in ws_client.subscribed_instruments

    def test_auto_subscription_restoration_on_open(self, ws_client):
        ws_client.subscribe(["1333", "2885"])

        # Track subscription calls
        subscription_sent = []
        def mock_send_sub(security_ids, action):
            subscription_sent.append((security_ids, action))

        ws_client._send_subscription = mock_send_sub

        # Simulate _on_open event
        ws_client._on_open(None)

        assert ws_client.is_connected()
        assert len(subscription_sent) == 1
        assert subscription_sent[0][1] == "SUBSCRIBE"
        assert "1333" in subscription_sent[0][0]
        assert "2885" in subscription_sent[0][0]

    def test_stale_connection_detection(self, ws_client):
        ws_client.set_token("TEST_TOKEN")
        ws_client._connected = True
        ws_client.last_msg_time = time.time() - 2.0  # 2s old (threshold is 1s)

        close_called = False
        class DummyWS:
            def close(self):
                nonlocal close_called
                close_called = True

        ws_client.ws = DummyWS()
        ws_client._should_reconnect = True

        # Start watchdog
        ws_client._start_heartbeat_monitor()
        time.sleep(3.5)  # wait for watchdog tick

        assert close_called is True
        assert "Stale connection detected" in ws_client.last_disconnect_reason

    def test_tick_and_volume_caching(self, ws_client):
        msg = '{"data": [{"security_id": "1333", "last_price": 2450.5, "volume": 1000}]}'
        ws_client._on_message(None, msg)

        assert ws_client.get_cached_ltp("1333") == 2450.5
        assert ws_client.get_cached_vol("1333") == 1000
        assert ws_client.cache_hits == 1

    def test_reconnect_logging_and_latency(self, ws_client):
        ws_client.disconnect_timestamp = time.time() - 0.5  # 500ms ago
        ws_client.last_disconnect_reason = "Test Disconnect"

        ws_client._on_open(None)
        assert ws_client.is_connected()
