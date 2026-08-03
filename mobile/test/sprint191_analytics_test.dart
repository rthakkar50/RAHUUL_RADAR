import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile/core/analytics/analytics_engine.dart';
import 'package:mobile/presentation/screens/analytics/analytics_screen.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  SharedPreferences.setMockInitialValues({});

  group('SPRINT-191 Performance Analytics & Strategy Intelligence Tests', () {
    test('AnalyticsEngine returns non-null summary and metrics', () {
      final summary = AnalyticsEngine.instance.getAnalyticsSummary();
      expect(summary.winRate, greaterThan(0.0));
      expect(summary.profitFactor, greaterThan(0.0));
      expect(summary.confidenceBucketWinRate.containsKey('86-90%'), isTrue);
      expect(summary.scannerWinRate.containsKey('Swing'), isTrue);
      expect(summary.aiRecommendations.isNotEmpty, isTrue);
    });

    testWidgets('AnalyticsScreen renders tabs and strategy metrics', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: AnalyticsScreen(),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Performance Analytics'), findsOneWidget);
      expect(find.text('Strategy'), findsOneWidget);
      expect(find.text('Confidence'), findsOneWidget);
      expect(find.text('Heatmaps'), findsOneWidget);
      expect(find.text('AI Insights'), findsOneWidget);
      expect(find.text('Win Rate'), findsOneWidget);
      expect(find.text('Profit Factor'), findsOneWidget);
    });
  });
}
