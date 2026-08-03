import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile/core/execution/execution_validator.dart';
import 'package:mobile/core/execution/execution_audit_engine.dart';
import 'package:mobile/core/paper_trading/paper_trading_engine.dart';
import 'package:mobile/data/models/scan_result_model.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  SharedPreferences.setMockInitialValues({});

  group('SPRINT-190 Execution Safety Layer & Order Preview Tests', () {
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

    test('Valid order passes all safety validations', () {
      final res = ExecutionValidator.instance.validateOrder(
        item: validItem,
        requestedQty: 10,
      );

      expect(res.isValid, isTrue);
      expect(res.failedChecks.isEmpty, isTrue);
      expect(res.passedChecks.length, greaterThanOrEqualTo(7));
    });

    test('Low confidence signal fails validation', () {
      final lowConfItem = ScanResultModel.fromJson({
        'Symbol': 'RELIANCE.NS',
        'Signal': 'BUY',
        'Score': 88.0,
        'Confidence': 55.0,
        'Trend': 'Strong Bullish',
        'Volume': '1250000',
        'Risk Reward': '1:2.0',
        'Entry': 2500.0,
        'Stop Loss': 2450.0,
        'Target 1': 2600.0,
        'Target 2': 2700.0,
        'Sector': 'Energy',
      });

      final res = ExecutionValidator.instance.validateOrder(
        item: lowConfItem,
        requestedQty: 10,
      );

      expect(res.isValid, isFalse);
      expect(res.failedChecks.any((c) => c.contains('Confidence low')), isTrue);
    });

    test('Invalid Stop Loss fails validation', () {
      final invalidSLItem = ScanResultModel(
        symbol: 'RELIANCE.NS',
        company: 'Reliance Industries',
        sector: 'Energy',
        price: 2500.0,
        signal: 'BUY',
        score: 88.0,
        rawScore: 88.0,
        confidence: 85.0,
        trend: 'Strong Bullish',
        volume: '1250000',
        riskReward: '1:2.0',
        rsScore: 80.0,
        entry: 2500.0,
        stopLoss: 0.0, // Invalid 0.0 SL
        target1: 2600.0,
        target2: 2700.0,
        target3: 2800.0,
        tradeGrade: 'A',
        riskGrade: 'LOW',
        timestamp: '2026-08-03',
      );

      final res = ExecutionValidator.instance.validateOrder(
        item: invalidSLItem,
        requestedQty: 10,
      );

      expect(res.isValid, isFalse);
      expect(res.failedChecks.any((c) => c.contains('Stop Loss invalid')), isTrue);
    });

    test('Insufficient cash fails validation', () {
      final res = ExecutionValidator.instance.validateOrder(
        item: validItem,
        requestedQty: 100, // Requires ₹250,000 > ₹100,000 cash
      );

      expect(res.isValid, isFalse);
      expect(res.failedChecks.any((c) => c.contains('Insufficient Cash')), isTrue);
    });

    test('Duplicate position prevents re-entry', () async {
      await PaperTradingEngine.instance.executePaperTradeFromScanner(validItem, requestedQty: 10);

      final res = ExecutionValidator.instance.validateOrder(
        item: validItem,
        requestedQty: 5,
      );

      expect(res.isValid, isFalse);
      expect(res.failedChecks.any((c) => c.contains('Duplicate Open Position')), isTrue);
    });

    test('Circuit breaker trips after 5 consecutive losses', () {
      final validator = ExecutionValidator.instance;
      for (int i = 0; i < 5; i++) {
        validator.recordTradeOutcome(false);
      }

      expect(validator.isCircuitBreakerTripped, isTrue);

      final res = validator.validateOrder(
        item: validItem,
        requestedQty: 5,
      );
      expect(res.isValid, isFalse);
      expect(res.message.contains('Circuit Breaker Active'), isTrue);
    });

    test('ExecutionAuditEngine records confirmation and cancellation audits', () async {
      final audit = ExecutionAuditEngine.instance;
      await audit.recordAudit(
        symbol: 'TVSMOTOR.NS',
        signal: 'BUY',
        entry: 2000.0,
        quantity: 5,
        validationPassed: true,
        validationMessage: 'All Validations Passed',
        userAction: 'CONFIRMED',
      );

      expect(audit.totalValidationsCount, greaterThanOrEqualTo(1));
      expect(audit.confirmedExecutionsCount, greaterThanOrEqualTo(1));
    });
  });
}
