import 'package:flutter/material.dart';
import '../../../../data/models/scan_response_model.dart';

class ScannerSummaryPanel extends StatelessWidget {
  final ScanResponseModel response;
  final String universeName;

  const ScannerSummaryPanel({
    super.key,
    required this.response,
    required this.universeName,
  });

  @override
  Widget build(BuildContext context) {
    final buyCount   = response.qualifiedResults.where((r) => r.signal.toUpperCase().contains('BUY')).length;
    final sellCount  = response.qualifiedResults.where((r) => r.signal.toUpperCase().contains('SELL')).length;
    final watchCount = response.qualifiedResults.where((r) => r.signal.toUpperCase().contains('WATCH')).length;

    final health  = response.scannerHealth;
    final summary = response.marketSummary;
    final perf    = response.performanceMetrics;

    return Container(
      margin: const EdgeInsets.fromLTRB(12, 10, 12, 4),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [const Color(0xFF161B27), const Color(0xFF1A2035)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF2A3550), width: 1),
        boxShadow: [
          BoxShadow(
            color: Colors.blueAccent.withValues(alpha: 0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Header row ──────────────────────────────────────────
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(5),
                  decoration: BoxDecoration(
                    color: Colors.blueAccent.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.radar_rounded, color: Colors.blueAccent, size: 15),
                ),
                const SizedBox(width: 8),
                Text(
                  '$universeName SCANNER SUMMARY',
                  style: const TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 12,
                    letterSpacing: 0.8,
                    color: Color(0xFF7EB3FF),
                  ),
                ),
                const Spacer(),
                _qualityBadge(response.marketQuality),
              ],
            ),

            const SizedBox(height: 10),

            // ── Stats single row ─────────────────────────────────────
            IntrinsicHeight(
              child: Row(
                children: [
                  _statCard('Universe', '${response.totalUniverse}',
                      Icons.hub_outlined, const Color(0xFF8899BB)),
                  _divider(),
                  _statCard('Scanned', '${response.totalScanned}',
                      Icons.manage_search_rounded, Colors.cyanAccent),
                  _divider(),
                  _statCard('Qualified', '${response.qualifiedResults.length}',
                      Icons.check_circle_outline_rounded, const Color(0xFF4ADE80)),
                  _divider(),
                  _statCard('BUY', '$buyCount',
                      Icons.arrow_upward_rounded, const Color(0xFF4ADE80)),
                  _divider(),
                  _statCard('SELL', '$sellCount',
                      Icons.arrow_downward_rounded, const Color(0xFFFF6B6B)),
                  _divider(),
                  _statCard('WATCH', '$watchCount',
                      Icons.visibility_outlined, const Color(0xFFFFB347)),
                  _divider(),
                  _statCard('Exec', '${response.execTime.toStringAsFixed(1)}s',
                      Icons.timer_outlined, const Color(0xFFBB86FC)),
                ],
              ),
            ),

            const SizedBox(height: 8),

            // ── Footer info bar ──────────────────────────────────────
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                color: const Color(0xFF0D1120),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _footerItem(
                    Icons.satellite_alt_outlined,
                    health['primary_provider'] ?? 'Paytm Money',
                  ),
                  _footerItem(
                    Icons.show_chart_rounded,
                    'Regime: ${summary['regime'] ?? 'BULLISH'} · '
                    '${summary['advances'] ?? 0}A / ${summary['declines'] ?? 0}D',
                  ),
                  _footerItem(
                    Icons.speed_outlined,
                    '${perf['avg_symbol_ms'] ?? 24} ms/sym',
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Helpers ────────────────────────────────────────────────────────────────

  Widget _statCard(String label, String value, IconData icon, Color color) {
    return Expanded(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 13),
          const SizedBox(height: 3),
          Text(
            value,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w800,
              color: color,
              height: 1.1,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: const TextStyle(
              fontSize: 9,
              color: Color(0xFF8899BB),
              fontWeight: FontWeight.w500,
              letterSpacing: 0.3,
            ),
          ),
        ],
      ),
    );
  }

  Widget _divider() => Container(
        width: 1,
        height: 36,
        margin: const EdgeInsets.symmetric(horizontal: 2),
        color: const Color(0xFF2A3550),
      );

  Widget _qualityBadge(String quality) {
    final isHigh = quality.toUpperCase().contains('HIGH');
    final color  = isHigh ? const Color(0xFF4ADE80) : const Color(0xFFFFB347);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.35), width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.fiber_manual_record, color: color, size: 7),
          const SizedBox(width: 4),
          Text(
            quality,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w700,
              fontSize: 10,
              letterSpacing: 0.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget _footerItem(IconData icon, String text) => Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: const Color(0xFF556680), size: 11),
          const SizedBox(width: 4),
          Text(
            text,
            style: const TextStyle(fontSize: 9, color: Color(0xFF556680), fontWeight: FontWeight.w500),
          ),
        ],
      );
}
