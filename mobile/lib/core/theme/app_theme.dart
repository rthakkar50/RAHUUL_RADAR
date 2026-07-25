import 'package:flutter/material.dart';

class AppTheme {
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: const Color(0xFF121212),
      colorScheme: const ColorScheme.dark(
        primary: Color(0xFFBB86FC),
        secondary: Color(0xFF03DAC6),
        surface: Color(0xFF1E1E1E),
        error: Color(0xFFCF6679),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: Color(0xFF1E1E1E),
        elevation: 0,
        centerTitle: true,
      ),
      cardTheme: CardThemeData(
        color: const Color(0xFF1E1E1E),
        elevation: 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }

  // Trading specific colors
  static const Color buyColor = Color(0xFF4CAF50); // Green for BUY
  static const Color sellColor = Color(0xFFF44336); // Red for SELL
  static const Color watchColor = Color(0xFFFF9800); // Orange for WATCH
}
