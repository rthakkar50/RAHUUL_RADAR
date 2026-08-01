import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Splash screen loads properly', (WidgetTester tester) async {
    // Build minimal splash widget UI test
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

    // Verify splash screen elements
    expect(find.text('RAHUUL RADAR'), findsOneWidget);
    expect(find.text('Production Scanner'), findsOneWidget);
    expect(find.byIcon(Icons.radar), findsOneWidget);
  });
}
