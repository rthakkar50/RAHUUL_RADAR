import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/data/models/scan_result_model.dart';

void main() {
  group('ScanResultModel Canonical Signal Normalization', () {
    test('parses canonical signal and entryDecision independently', () {
      final jsonPayload = {
        'Symbol': 'DIVISLAB.NS',
        'Company': 'DIVISLAB',
        'Sector': 'PHARMA',
        'Price': 4500.0,
        'Signal': 'BUY',
        'Entry Decision': 'RETEST FIRST',
        'Score': 90.0,
        'Raw Score': 90.0,
        'Confidence': 88.0,
        'Trend': 'BULLISH',
        'Volume': '500k',
        'Risk Reward': '1:2.0',
        'RS Score': 80.0,
        'Entry': 4500.0,
        'Stop Loss': 4400.0,
        'Target 1': 4700.0,
        'Target 2': 4800.0,
        'Target 3': 4900.0,
        'Trade Grade': 'ELITE',
        'Risk Grade': 'LOW',
        'Timestamp': 'LIVE',
      };

      final model = ScanResultModel.fromJson(jsonPayload);

      expect(model.signal, equals('BUY'));
      expect(model.entryDecision, equals('RETEST FIRST'));
      expect(model.displaySignal, equals('RETEST FIRST | BUY'));
    });

    test('normalizes legacy concatenated signal strings for backward compatibility', () {
      final jsonPayload = {
        'Symbol': 'SUNPHARMA.NS',
        'Price': 1200.0,
        'Signal': 'ENTER NOW | BUY',
        'Score': 92.0,
      };

      final model = ScanResultModel.fromJson(jsonPayload);

      expect(model.signal, equals('BUY'));
      expect(model.entryDecision, equals('ENTER NOW'));
      expect(model.displaySignal, equals('ENTER NOW | BUY'));
    });
  });
}
