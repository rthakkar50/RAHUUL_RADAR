import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile/core/broker/paytm_broker_adapter.dart';
import 'package:mobile/presentation/screens/broker/broker_dashboard_screen.dart';
import 'package:mobile/data/models/scan_result_model.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  SharedPreferences.setMockInitialValues({});

  group('SPRINT-192 Paytm Money Broker Adapter Tests', () {
    test('PaytmBrokerAdapter fetches funds, holdings, and previews orders', () async {
      final adapter = PaytmBrokerAdapter.instance;
      final funds = await adapter.fetchFunds();
      expect(funds.availableCash, greaterThan(0.0));

      final holdings = await adapter.fetchHoldings();
      expect(holdings.isNotEmpty, isTrue);

      final item = ScanResultModel.fromJson({
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

      final preview = adapter.generateOrderPreview(item: item, quantity: 10);
      expect(preview.symbol, equals('RELIANCE.NS'));
      expect(preview.exchange, equals('NSE'));
      expect(preview.requiredMargin, equals(25000.0));
      expect(preview.estimatedCharges, greaterThan(0.0));
    });

    testWidgets('BrokerDashboardScreen renders tabs and connection status', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: BrokerDashboardScreen(),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Paytm Money Broker Dashboard'), findsOneWidget);
      expect(find.text('Funds & Status'), findsOneWidget);
      expect(find.text('Holdings'), findsOneWidget);
      expect(find.text('Positions & Orders'), findsOneWidget);
    });
  });
}
