import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/presentation/widgets/decision_center_widget.dart';
import 'package:mobile/presentation/widgets/unified_scanner_card.dart';
import 'package:mobile/presentation/widgets/footer_status_widget.dart';
import 'package:mobile/data/models/scan_result_model.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('SPRINT-186 Enterprise Unified Scanner Framework Tests', () {
    testWidgets('DecisionCenterWidget renders market bias and signal counts', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: DecisionCenterWidget(
              buyCount: 10,
              sellCount: 1,
              watchCount: 10,
              qualifiedCount: 21,
              totalScanned: 200,
            ),
          ),
        ),
      );

      expect(find.text('Enterprise Decision Center'), findsOneWidget);
      expect(find.text('BUY'), findsOneWidget);
      expect(find.text('SELL'), findsOneWidget);
      expect(find.text('WATCH'), findsOneWidget);
      expect(find.text('QUALIFIED'), findsOneWidget);
    });

    testWidgets('UnifiedScannerCard renders item symbol, confidence, and signal', (WidgetTester tester) async {
      final sampleResult = ScanResultModel.fromJson({
        'Symbol': 'VEDL.NS',
        'Signal': 'SELL',
        'Score': 76.19,
        'Confidence': 70.1,
        'Trend': 'Strong Bearish',
        'Volume': '6719712',
        'Risk Reward': '1:2.0',
        'Entry': 267.25,
        'Stop Loss': 277.51,
        'Target 1': 246.73,
        'Target 2': 236.47,
        'Sector': 'Metal',
      });

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: UnifiedScannerCard(
              item: sampleResult,
              rank: 1,
              scannerType: 'Swing',
              onTap: () {},
            ),
          ),
        ),
      );

      expect(find.text('VEDL.NS'), findsOneWidget);
      expect(find.text('SELL'), findsOneWidget);
      expect(find.text('Metal'), findsOneWidget);
    });

    testWidgets('FooterStatusWidget renders provider and version telemetry', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: FooterStatusWidget(),
          ),
        ),
      );

      expect(find.textContaining('Provider: Paytm Money'), findsOneWidget);
      expect(find.textContaining('v6.7.0'), findsOneWidget);
    });
  });
}
