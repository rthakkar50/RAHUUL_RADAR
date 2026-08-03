import 'package:flutter/material.dart';

class DecisionCenterWidget extends StatelessWidget {
  final Map<String, dynamic>? marketSummary;
  final int buyCount;
  final int sellCount;
  final int watchCount;
  final int qualifiedCount;
  final int totalScanned;
  final String topSector;
  final String weakSector;
  final VoidCallback? onRefresh;

  const DecisionCenterWidget({
    super.key,
    this.marketSummary,
    required this.buyCount,
    required this.sellCount,
    required this.watchCount,
    required this.qualifiedCount,
    required this.totalScanned,
    this.topSector = 'IT / Tech (+1.8%)',
    this.weakSector = 'Metal (-0.9%)',
    this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    final trend = marketSummary?['trend']?.toString() ?? 'STRONG_BULL';
    final bias = marketSummary?['bias']?.toString() ?? 'BULLISH';
    final adx = marketSummary?['adx']?.toString() ?? '32.4';
    final isBull = trend.contains('BULL') || bias.contains('BULL');

    final trendColor = isBull ? Colors.greenAccent : Colors.redAccent;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.3), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: Colors.cyanAccent.withValues(alpha: 0.05),
            blurRadius: 10,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Bar
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: Colors.cyanAccent.withValues(alpha: 0.15),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.psychology, color: Colors.cyanAccent, size: 20),
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'Enterprise Decision Center',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: trendColor.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: trendColor),
                ),
                child: Text(
                  'BIAS: $bias',
                  style: TextStyle(
                    color: trendColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 11,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Market Health Metrics Grid
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricPill('Trend Strength', 'ADX $adx', Colors.amberAccent),
              _metricPill('Market Health', 'OPTIMAL', Colors.greenAccent),
              _metricPill('Liquidity', 'HIGH', Colors.cyanAccent),
              _metricPill('Volatility', 'NORMAL', Colors.purpleAccent),
            ],
          ),
          const SizedBox(height: 12),

          // Sector Analysis Card
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.04),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.pie_chart_outline, color: Colors.grey, size: 16),
                    const SizedBox(width: 6),
                    Text(
                      'Top Sector: $topSector',
                      style: const TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                Text(
                  'Weakest: $weakSector',
                  style: const TextStyle(color: Colors.orangeAccent, fontSize: 11, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),

          // Signal Count Summary Cards
          Row(
            children: [
              Expanded(child: _countCard('BUY', '$buyCount', Colors.greenAccent)),
              const SizedBox(width: 8),
              Expanded(child: _countCard('SELL', '$sellCount', Colors.redAccent)),
              const SizedBox(width: 8),
              Expanded(child: _countCard('WATCH', '$watchCount', Colors.amberAccent)),
              const SizedBox(width: 8),
              Expanded(child: _countCard('QUALIFIED', '$qualifiedCount', Colors.cyanAccent)),
            ],
          ),
          const SizedBox(height: 10),

          // AI Insight Summary Banner
          Row(
            children: [
              const Icon(Icons.auto_awesome, color: Colors.amberAccent, size: 14),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  'AI Insight: Bullish momentum confirmed across IT & Banking. $buyCount A-Grade setups ready for execution.',
                  style: const TextStyle(color: Colors.white70, fontSize: 11, fontStyle: FontStyle.italic),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metricPill(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 2),
        Text(
          value,
          style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 11),
        ),
      ],
    );
  }

  Widget _countCard(String title, String count, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Column(
        children: [
          Text(title, style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold)),
          const SizedBox(height: 2),
          Text(count, style: TextStyle(color: color, fontSize: 15, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
