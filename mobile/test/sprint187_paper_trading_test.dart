import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile/core/paper_trading/paper_trading_engine.dart';
import 'package:mobile/data/models/paper_trade_model.dart';
import 'package:mobile/data/models/scan_result_model.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  SharedPreferences.setMockInitialValues({});

  group('SPRINT-187 Enterprise Paper Trading Engine Tests', () {
    test('PaperTradingEngine initializes default virtual capital', () {
      final engine = PaperTradingEngine.instance;
      expect(engine.startingCapital, 100000.0);
      expect(engine.availableCash, 100000.0);
    });

    test('PaperTradeModel calculates unrealized and realized PnL correctly for BUY', () {
      final trade = PaperTradeModel(
        id: 'T1',
        symbol: 'RELIANCE.NS',
        signal: 'BUY',
        sector: 'Energy',
        entryPrice: 2500.0,
        currentPrice: 2600.0,
        exitPrice: 2600.0,
        quantity: 10,
        stopLoss: 2450.0,
        target1: 2600.0,
        target2: 2700.0,
        riskReward: 2.0,
        strategy: 'Breakout',
        entryTime: DateTime.now(),
      );

      expect(trade.capitalUsed, 25000.0);
      expect(trade.unrealizedPnL, 1000.0);
      expect(trade.realizedPnL, 1000.0);
      expect(trade.virtualCharges, closeTo(7.5, 0.001));
      expect(trade.netPnL, closeTo(992.5, 0.001));
    });

    test('PaperTradeModel calculates unrealized and realized PnL correctly for SELL', () {
      final trade = PaperTradeModel(
        id: 'T2',
        symbol: 'VEDL.NS',
        signal: 'SELL',
        sector: 'Metal',
        entryPrice: 267.25,
        currentPrice: 257.25,
        exitPrice: 257.25,
        quantity: 100,
        stopLoss: 277.51,
        target1: 246.73,
        target2: 236.47,
        riskReward: 2.0,
        strategy: 'Intraday Short',
        entryTime: DateTime.now(),
      );

      expect(trade.capitalUsed, 26725.0);
      expect(trade.unrealizedPnL, 1000.0);
      expect(trade.realizedPnL, 1000.0);
    });

    test('Engine opens and closes paper trade correctly', () async {
      final engine = PaperTradingEngine.instance;
      await engine.resetVirtualAccount(capital: 100000.0);

      final sampleResult = ScanResultModel.fromJson({
        'Symbol': 'TVSMOTOR.NS',
        'Signal': 'BUY',
        'Score': 88.0,
        'Confidence': 100.0,
        'Trend': 'Strong Bullish',
        'Volume': '450000',
        'Risk Reward': '1:2.0',
        'Entry': 2000.0,
        'Stop Loss': 1950.0,
        'Target 1': 2100.0,
        'Target 2': 2200.0,
        'Sector': 'Auto',
      });

      final success = await engine.executePaperTradeFromScanner(sampleResult, requestedQty: 10);
      expect(success, isTrue);
      expect(engine.openTrades.length, 1);
      expect(engine.usedCapital, 20000.0);

      final tradeId = engine.openTrades.first.id;
      await engine.closePosition(tradeId, customExitPrice: 2100.0);

      expect(engine.openTrades.length, 0);
      expect(engine.closedTrades.length, 1);
      expect(engine.winningTradesCount, 1);
      expect(engine.winRatePct, 100.0);
    });
  });
}
