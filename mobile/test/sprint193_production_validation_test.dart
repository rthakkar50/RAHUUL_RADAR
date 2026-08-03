import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile/core/paper_trading/paper_trading_engine.dart';
import 'package:mobile/core/execution/execution_validator.dart';
import 'package:mobile/core/analytics/analytics_engine.dart';
import 'package:mobile/core/broker/paytm_broker_adapter.dart';
import 'package:mobile/data/models/scan_result_model.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  SharedPreferences.setMockInitialValues({});

  group('SPRINT-193 Production Hardening & Validation Tests', () {
    late ScanResultModel validItem;

    setUp(() async {
      await PaperTradingEngine.instance.resetVirtualAccount(capital: 100000.0);
      ExecutionValidator.instance.resetCircuitBreaker();

      validItem = ScanResultModel.fromJson({
        'Symbol': 'RELIANCE.NS',
        'Signal': 'BUY',
        'Score': 88.0,
        'Confidence': 85.0,
        'Trend': 'Strong Bullish',
        'Volume': '1250000',
        'Risk Reward': '1:2.0',
        'Entry': 2500.0,
        'Stop Loss': 2450.0,
        'Target 1': 2600.0,
        'Target 2': 2700.0,
        'Sector': 'Energy',
      });
    });

    test('E2E Integration Flow: Scanner -> Safety -> Paper Trade -> Analytics -> Broker Preview', () async {
      // 1. Scanner item validation
      final valRes = ExecutionValidator.instance.validateOrder(item: validItem, requestedQty: 10);
      expect(valRes.isValid, isTrue);

      // 2. Paper Trade Execution
      final paperSuccess = await PaperTradingEngine.instance.executePaperTradeFromScanner(validItem, requestedQty: 10);
      expect(paperSuccess, isTrue);
      expect(PaperTradingEngine.instance.openTrades.length, equals(1));

      // 3. Analytics Calculation
      final analytics = AnalyticsEngine.instance.getAnalyticsSummary();
      expect(analytics.winRate, greaterThan(0.0));

      // 4. Broker Order Preview
      final preview = PaytmBrokerAdapter.instance.generateOrderPreview(item: validItem, quantity: 10);
      expect(preview.symbol, equals('RELIANCE.NS'));
      expect(preview.requiredMargin, equals(25000.0));
    });

    test('App Restart Resilience & State Integrity', () async {
      final engine = PaperTradingEngine.instance;
      await engine.executePaperTradeFromScanner(validItem, requestedQty: 5);

      // Re-initialize engine state
      await engine.init();
      expect(engine.openTrades.length, greaterThanOrEqualTo(1));
    });
  });
}
