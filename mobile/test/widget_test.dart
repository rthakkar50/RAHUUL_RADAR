import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/main.dart'; 

void main() {
  testWidgets('Splash screen loads properly', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const RahuulRadarApp());

    // Verify that the splash screen shows the correct text initially
    expect(find.text('RAHUUL RADAR'), findsOneWidget);
    expect(find.text('Production Scanner'), findsOneWidget);
    expect(find.byIcon(Icons.radar), findsOneWidget);
    
    // Fast forward the 2-second splash screen timer
    await tester.pumpAndSettle(const Duration(seconds: 3));
  });
}
