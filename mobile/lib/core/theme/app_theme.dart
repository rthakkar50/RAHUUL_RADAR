import 'package:flutter/material.dart';

class AppTheme {
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: const Color(0xFF0B0E14),
      dividerColor: const Color(0xFF1F2735),
      colorScheme: const ColorScheme.dark(
        primary: Color(0xFF3B82F6),
        secondary: Color(0xFF2563EB),
        surface: Color(0xFF121721),
        error: Color(0xFFEF4444),
        onPrimary: Color(0xFFF0F6FC),
        onSecondary: Color(0xFFF0F6FC),
        onSurface: Color(0xFFF0F6FC),
        onError: Color(0xFFF0F6FC),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: Color(0xFF0B0E14),
        foregroundColor: Color(0xFFF0F6FC),
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
      ),
      cardTheme: CardThemeData(
        color: const Color(0xFF121721),
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: Color(0xFF1F2735), width: 1),
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: Color(0xFF1F2735),
        thickness: 1,
      ),
    );
  }

  // Trading specific colors
  static const Color buyColor = Color(0xFF10B981); // Green for BUY
  static const Color sellColor = Color(0xFFEF4444); // Red for SELL
  static const Color watchColor = Color(0xFFF59E0B); // Amber for WATCH
}
