import 'package:flutter/material.dart';

class AppDesignSystem {
  // Theme Colors — Sober Institutional Palette
  static const Color background = Color(0xFF0B0E14);
  static const Color surface = Color(0xFF121721);
  static const Color surfaceLight = Color(0xFF18202D);
  static const Color border = Color(0xFF1F2735);

  static const Color primary = Color(0xFF3B82F6);
  static const Color secondary = Color(0xFF2563EB);
  static const Color success = Color(0xFF10B981);
  static const Color warning = Color(0xFFF59E0B);
  static const Color danger = Color(0xFFEF4444);
  static const Color textPrimary = Color(0xFFF0F6FC);
  static const Color textSecondary = Color(0xFF8B949E);

  // Gradients — Subtle Monochrome Tones (No Rainbow / Neon Transitions)
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF3B82F6), Color(0xFF1D4ED8)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient successGradient = LinearGradient(
    colors: [Color(0xFF10B981), Color(0xFF059669)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient dangerGradient = LinearGradient(
    colors: [Color(0xFFEF4444), Color(0xFFDC2626)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // Borders & Radius
  static final BorderRadius radiusSmall = BorderRadius.circular(8);
  static final BorderRadius radiusMedium = BorderRadius.circular(12);
  static final BorderRadius radiusLarge = BorderRadius.circular(16);

  // Box Decorations
  static BoxDecoration glassCard({Color? borderColor}) {
    return BoxDecoration(
      color: surface,
      borderRadius: radiusMedium,
      border: Border.all(color: borderColor ?? border, width: 1),
      boxShadow: [
        BoxShadow(
          color: Colors.black.withValues(alpha: 0.2),
          blurRadius: 6,
          offset: const Offset(0, 2),
        ),
      ],
    );
  }
}
