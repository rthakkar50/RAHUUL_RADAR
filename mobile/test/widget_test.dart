import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/data/models/scan_response_model.dart';
import 'package:mobile/data/models/scan_result_model.dart';
import 'package:mobile/data/models/dashboard_data_model.dart';
import 'package:mobile/presentation/widgets/footer_status_widget.dart';
import 'package:mobile/presentation/widgets/unified_scanner_card.dart';
import 'package:mobile/presentation/screens/scanner/widgets/scanner_summary_panel.dart';

void main() {
  testWidgets('Splash screen loads properly', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.radar, size: 80, color: Colors.blueAccent),
                SizedBox(height: 16),
                Text(
                  'RAHUUL RADAR',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  'Production Scanner',
                  style: TextStyle(color: Colors.grey),
                ),
              ],
            ),
          ),
        ),
      ),
    );

    expect(find.text('RAHUUL RADAR'), findsOneWidget);
    expect(find.text('Production Scanner'), findsOneWidget);
    expect(find.byIcon(Icons.radar), findsOneWidget);
  });

  test('Scenario 1-4 & 6-7: ScanResponseModel preserves backend timestamps and never uses DateTime.now()', () {
    // Stale 27.3h Yahoo fallback response
    final staleJson = <String, dynamic>{
      'status': 'COMPLETED',
      'server_timestamp': 1791716078.02,
      'scan_timestamp': 1791617902.37,
      'cache_timestamp': 1791617902.37,
      'data_timestamp': '2026-10-09 15:25:00',
      'cache_age_seconds': 98175.65,
      'is_stale': true,
      'is_scanning': false,
      'provider': 'Yahoo Finance (Fallback)',
      'provider_health': 'DEGRADED',
      'fallback_used': true,
      'paytm_authenticated': false,
      'market_status': 'CLOSED',
      'total_universe': 184,
      'total_attempted': 180,
      'total_processed': 180,
      'total_ranked': 180,
      'total_scanned': 180,
      'qualified_results': [
        {
          'Symbol': 'DIVISLAB.NS',
          'Signal': 'BUY',
          'Price': 6214.0,
          'Score': 75.56,
          'Confidence': 78.0,
          'Timestamp': '2026-10-09 15:25:00',
        },
        {
          'Symbol': 'TATASTEEL.NS',
          'Signal': 'WATCH',
          'Price': 152.0,
          'Score': 68.0,
          'Confidence': 70.0,
        },
      ],
    };

    final model = ScanResponseModel.fromJson(staleJson);
    expect(model.isStale, isTrue);
    expect(model.fallbackUsed, isTrue);
    expect(model.paytmAuthenticated, isFalse);
    expect(model.provider, equals('Yahoo Finance (Fallback)'));
    expect(model.providerHealth, equals('DEGRADED'));
    expect(model.marketStatus, equals('CLOSED'));
    expect(model.formattedCacheAge, equals('27.3h'));
    expect(model.dataTimestamp, equals('2026-10-09 15:25:00'));
    expect(model.timestamp, contains('IST'));
    // Missing item timestamp defaults to UNAVAILABLE, never LIVE
    expect(model.qualifiedResults[1].timestamp, equals('UNAVAILABLE'));

    // Empty / missing timestamp response must return UNAVAILABLE, never DateTime.now()
    final emptyModel = ScanResponseModel.fromJson(<String, dynamic>{
      'status': 'DATA_UNAVAILABLE',
      'qualified_results': <dynamic>[],
    });
    expect(emptyModel.timestamp, equals('UNAVAILABLE'));
    expect(emptyModel.isStale, isTrue);
    expect(emptyModel.providerHealth, equals('UNKNOWN'));
    expect(emptyModel.formattedCacheAge, equals('UNKNOWN'));
  });

  testWidgets('FooterStatusWidget and UnifiedScannerCard show truthful provider and cached warnings', (WidgetTester tester) async {
    final item = ScanResultModel.fromJson(<String, dynamic>{
      'Symbol': 'DIVISLAB.NS',
      'Signal': 'BUY',
      'Price': 6214.0,
      'Entry': 6214.0,
      'Stop Loss': 6100.0,
      'Target 1': 6400.0,
      'Target 2': 6550.0,
      'Score': 75.56,
      'Confidence': 78.0,
      'Timestamp': '2026-10-09 15:25:00',
    });

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: Column(
            children: [
              UnifiedScannerCard(
                item: item,
                rank: 1,
                isStale: true,
                fallbackUsed: true,
                marketStatus: 'CLOSED',
                onTap: () {},
              ),
              const FooterStatusWidget(
                provider: 'Yahoo Finance (Fallback)',
                providerHealth: 'DEGRADED',
                fallbackUsed: true,
                marketStatus: 'CLOSED',
              ),
            ],
          ),
        ),
      ),
    );

    expect(find.text('BUY (CACHED)'), findsOneWidget);
    expect(find.textContaining('CACHED SNAPSHOT'), findsOneWidget);
    expect(find.textContaining('Provider: Yahoo Finance (Fallback) [DEGRADED]'), findsOneWidget);
    expect(find.textContaining('Provider: Paytm Money (Live)'), findsNothing);
  });

  testWidgets('ScannerSummaryPanel uses real funnel counts and filters Todays Best to BUY/STRONG_BUY', (WidgetTester tester) async {
    final resp = ScanResponseModel.fromJson(<String, dynamic>{
      'status': 'COMPLETED',
      'scan_timestamp': 1791617902.37,
      'cache_age_seconds': 98175.65,
      'is_stale': true,
      'provider': 'Yahoo Finance (Fallback)',
      'provider_health': 'DEGRADED',
      'fallback_used': true,
      'paytm_authenticated': false,
      'market_status': 'CLOSED',
      'total_universe': 184,
      'total_attempted': 180,
      'total_processed': 180,
      'total_ranked': 180,
      'total_scanned': 180,
      'qualified_results': [
        {'Symbol': 'BUYSTOCK', 'Signal': 'BUY', 'Price': 500.0, 'Score': 82.0},
        {'Symbol': 'WATCHSTOCK', 'Signal': 'WATCH', 'Price': 300.0, 'Score': 90.0},
      ],
    });

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: Column(
              children: [
                ScannerSummaryPanel(response: resp, universeName: 'F&O Stocks'),
                AdvancedDiagnosticsWidget(response: resp),
              ],
            ),
          ),
        ),
      ),
    );

    expect(find.text('184'), findsOneWidget);
    // Expand diagnostics
    await tester.tap(find.text('Show Advanced Diagnostics'));
    await tester.pump();

    expect(find.textContaining('Provider: Yahoo Finance (Fallback)'), findsOneWidget);
    expect(find.text('BUYSTOCK'), findsOneWidget);
    // WATCHSTOCK must be excluded from Today's Best Qualified BUY Candidates
    expect(find.text('WATCHSTOCK'), findsNothing);
  });

  test('DashboardDataModel separates actual broker funds from virtual risk capital and paper balance', () {
    final empty = DashboardDataModel.empty();
    expect(empty.actualBrokerFundsLabel, equals('UNAVAILABLE'));
    expect(empty.virtualRiskCapitalLabel, equals('UNAVAILABLE'));
    expect(empty.paperEquityLabel, equals('UNAVAILABLE'));
    expect(empty.lastScanTime, equals('UNAVAILABLE'));
  });
}
