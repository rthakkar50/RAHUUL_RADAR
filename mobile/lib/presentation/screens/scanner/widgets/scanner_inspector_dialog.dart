import 'package:flutter/material.dart';
import '../../../../data/models/scan_result_model.dart';

class ScannerInspectorDialog extends StatelessWidget {
  final ScanResultModel item;

  const ScannerInspectorDialog({super.key, required this.item});

  static void show(BuildContext context, ScanResultModel item) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => ScannerInspectorDialog(item: item),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final bgColor = isDark ? const Color(0xFF1E222D) : Colors.white;
    final cardColor = isDark ? const Color(0xFF2A2E39) : const Color(0xFFF2F4F7);
    final isBuy = item.signal.toUpperCase().contains('BUY');
    final sigColor = isBuy ? Colors.green : (item.signal.toUpperCase().contains('SELL') ? Colors.red : Colors.orange);

    final scores = item.scores;
    final indicators = item.indicators;

    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        children: [
          // Drag Handle
          const SizedBox(height: 12),
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey.withValues(alpha: 0.4),
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: 12),

          // Header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.symbol,
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      '${item.company} • ${item.sector}',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.textTheme.bodySmall?.color?.withValues(alpha: 0.7),
                      ),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: sigColor.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: sigColor.withValues(alpha: 0.5)),
                  ),
                  child: Text(
                    item.signal,
                    style: TextStyle(
                      color: sigColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ),
              ],
            ),
          ),

          const Divider(height: 24),

          // Main Inspector Content
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              children: [
                // Price & Target Grid
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: cardColor,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _buildPriceBox('CMP', '₹${item.price.toStringAsFixed(2)}', theme),
                          _buildPriceBox('Entry', '₹${item.entry.toStringAsFixed(2)}', theme),
                          _buildPriceBox('Stop Loss', '₹${item.stopLoss.toStringAsFixed(2)}', theme, color: Colors.red),
                          _buildPriceBox('Target 1', '₹${item.target1.toStringAsFixed(2)}', theme, color: Colors.green),
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // Decision Trace & Reasons
                _buildSectionHeader('DECISION TRACE & EXPLANATION', Icons.analytics_outlined, theme),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: cardColor,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('AI Score: ${item.score.toStringAsFixed(1)}/100', style: const TextStyle(fontWeight: FontWeight.bold)),
                          Text('Confidence: ${item.confidence.toStringAsFixed(1)}%', style: TextStyle(fontWeight: FontWeight.bold, color: sigColor)),
                        ],
                      ),
                      const SizedBox(height: 8),
                      if (item.whySelected.isNotEmpty) ...[
                        const Text('Top Accept Reasons:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey)),
                        const SizedBox(height: 4),
                        ...item.whySelected.map((r) => Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Row(
                            children: [
                              const Icon(Icons.check_circle, size: 14, color: Colors.green),
                              const SizedBox(width: 6),
                              Expanded(child: Text(r, style: const TextStyle(fontSize: 13))),
                            ],
                          ),
                        )),
                      ],
                      if (item.reasons.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        const Text('Pipeline Decision Factors:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey)),
                        const SizedBox(height: 4),
                        ...item.reasons.map((r) => Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Row(
                            children: [
                              const Icon(Icons.info_outline, size: 14, color: Colors.blue),
                              const SizedBox(width: 6),
                              Expanded(child: Text(r, style: const TextStyle(fontSize: 13))),
                            ],
                          ),
                        )),
                      ],
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // Scores Breakdown
                _buildSectionHeader('QUANT SCORE BREAKDOWN', Icons.speed, theme),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: cardColor,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    children: [
                      _buildScoreRow('Trend Score', scores['trend'] ?? 50.0, theme),
                      _buildScoreRow('Momentum Score', scores['momentum'] ?? 50.0, theme),
                      _buildScoreRow('Structure Score', scores['structure'] ?? 50.0, theme),
                      _buildScoreRow('Volume Score', scores['volume'] ?? 50.0, theme),
                      _buildScoreRow('Risk Score', scores['risk'] ?? 50.0, theme),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // Technical Indicators Inspector
                _buildSectionHeader('TECHNICAL INDICATOR INSPECTOR', Icons.bar_chart, theme),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: cardColor,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      _buildIndicatorChip('RSI (14)', (indicators['rsi'] as num?)?.toStringAsFixed(1) ?? '55.0'),
                      _buildIndicatorChip('ADX (14)', (indicators['adx'] as num?)?.toStringAsFixed(1) ?? '25.0'),
                      _buildIndicatorChip('EMA 20', '₹${(indicators['ema_20'] as num?)?.toStringAsFixed(1) ?? '--'}'),
                      _buildIndicatorChip('EMA 50', '₹${(indicators['ema_50'] as num?)?.toStringAsFixed(1) ?? '--'}'),
                      _buildIndicatorChip('VWAP', '₹${(indicators['vwap'] as num?)?.toStringAsFixed(1) ?? '--'}'),
                      _buildIndicatorChip('ATR (14)', '₹${(indicators['atr'] as num?)?.toStringAsFixed(2) ?? '--'}'),
                      _buildIndicatorChip('Volume', item.volume),
                      _buildIndicatorChip('Delivery', '${(indicators['delivery_pct'] as num?)?.toStringAsFixed(0) ?? '45'}%'),
                      _buildIndicatorChip('Rel Strength', item.rsScore.toStringAsFixed(1)),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPriceBox(String label, String value, ThemeData theme, {Color? color}) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
        const SizedBox(height: 2),
        Text(
          value,
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.bold,
            color: color ?? theme.textTheme.bodyLarge?.color,
          ),
        ),
      ],
    );
  }

  Widget _buildSectionHeader(String title, IconData icon, ThemeData theme) {
    return Row(
      children: [
        Icon(icon, size: 16, color: Colors.blue),
        const SizedBox(width: 6),
        Text(
          title,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Colors.blue),
        ),
      ],
    );
  }

  Widget _buildScoreRow(String label, dynamic val, ThemeData theme) {
    final double v = (val as num?)?.toDouble() ?? 50.0;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(width: 120, child: Text(label, style: const TextStyle(fontSize: 13))),
          Expanded(
            child: LinearProgressIndicator(
              value: (v / 100.0).clamp(0.0, 1.0),
              backgroundColor: Colors.grey.withValues(alpha: 0.2),
              color: v >= 70 ? Colors.green : (v >= 50 ? Colors.blue : Colors.orange),
              minHeight: 6,
            ),
          ),
          const SizedBox(width: 12),
          Text('${v.toStringAsFixed(0)}/100', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildIndicatorChip(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.blue.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontSize: 10, color: Colors.grey)),
          Text(value, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
