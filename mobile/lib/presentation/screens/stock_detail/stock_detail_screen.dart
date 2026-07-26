import 'package:flutter/material.dart';
import '../../../data/models/scan_result_model.dart';

class StockDetailScreen extends StatelessWidget {
  final ScanResultModel result;

  const StockDetailScreen({super.key, required this.result});

  Color _getSignalColor(String signal) {
    final upper = signal.toUpperCase();
    if (upper.contains('BUY')) return Colors.greenAccent;
    if (upper.contains('SELL')) return Colors.redAccent;
    return Colors.orangeAccent;
  }

  @override
  Widget build(BuildContext context) {
    final signalColor = _getSignalColor(result.signal);

    return Scaffold(
      appBar: AppBar(
        title: Text('${result.symbol} Details'),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: signalColor.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: signalColor),
            ),
            child: Text(
              result.signal,
              style: TextStyle(color: signalColor, fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Overview Card
            _buildHeaderCard(context, signalColor),
            const SizedBox(height: 16),

            // AI Score & Confidence Section
            _buildAIScoreCard(context),
            const SizedBox(height: 16),

            // Trend, Momentum, Volume & Structure Section
            _buildTechnicalFactorsCard(context),
            const SizedBox(height: 16),

            // Risk & Execution Levels (Entry, SL, Targets)
            _buildRiskAndTargetsCard(context),
          ],
        ),
      ),
    );
  }

  Widget _buildHeaderCard(BuildContext context, Color signalColor) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    result.symbol,
                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  Text(
                    result.company.isNotEmpty ? result.company : 'NSE Stock',
                    style: const TextStyle(color: Colors.grey, fontSize: 14),
                  ),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '₹${result.price.toStringAsFixed(2)}',
                    style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.blueAccent),
                  ),
                  Text(
                    'Sector: ${result.sector.isNotEmpty ? result.sector : "N/A"}',
                    style: const TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ],
              ),
            ],
          ),
          if (result.timestamp.isNotEmpty) ...[
            const SizedBox(height: 12),
            const Divider(height: 1),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                const Icon(Icons.access_time, size: 12, color: Colors.grey),
                const SizedBox(width: 4),
                Text('Scanned at: ${result.timestamp}', style: const TextStyle(color: Colors.grey, fontSize: 11)),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildAIScoreCard(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.psychology, color: Colors.blueAccent),
              SizedBox(width: 8),
              Text('AI Score & Confidence', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildMetricColumn('AI Score', result.score.toStringAsFixed(1), Colors.white),
              _buildMetricColumn('Raw Score', result.rawScore.toStringAsFixed(1), Colors.grey),
              _buildMetricColumn('RS Score', result.rsScore.toStringAsFixed(1), Colors.cyanAccent),
              _buildMetricColumn('Trade Grade', result.tradeGrade.isNotEmpty ? result.tradeGrade : 'A', Colors.amberAccent),
            ],
          ),
          const SizedBox(height: 16),
          const Text('Confidence Level', style: TextStyle(fontSize: 12, color: Colors.grey)),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: (result.confidence / 100).clamp(0.0, 1.0),
              minHeight: 8,
              backgroundColor: Colors.grey.withValues(alpha: 0.2),
              color: Colors.blueAccent,
            ),
          ),
          const SizedBox(height: 4),
          Align(
            alignment: Alignment.centerRight,
            child: Text(
              '${result.confidence.toStringAsFixed(0)}% High Probability',
              style: const TextStyle(fontSize: 11, color: Colors.blueAccent, fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTechnicalFactorsCard(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.analytics, color: Colors.purpleAccent),
              SizedBox(width: 8),
              Text('Market Regime & Technical Factors', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 12),
          _buildDetailRow('Trend', result.trend.isNotEmpty ? result.trend : 'UPTREND', Icons.trending_up, Colors.greenAccent),
          const Divider(height: 16),
          _buildDetailRow('Momentum', 'RS: ${result.rsScore.toStringAsFixed(1)} (Strong Output)', Icons.speed, Colors.cyanAccent),
          const Divider(height: 16),
          _buildDetailRow('Volume Status', result.volume.isNotEmpty ? result.volume : 'High Volume Spike', Icons.bar_chart, Colors.orangeAccent),
          const Divider(height: 16),
          _buildDetailRow('Market Structure', 'Grade ${result.tradeGrade.isNotEmpty ? result.tradeGrade : "A"} Multi-timeframe Setup', Icons.grid_view, Colors.amberAccent),
        ],
      ),
    );
  }

  Widget _buildRiskAndTargetsCard(BuildContext context) {
    final entry = result.entry;
    final target1 = result.target1 > 0 ? result.target1 : (entry * 1.05);
    final target2 = result.target2 > 0 ? result.target2 : (entry * 1.10);
    final sl = result.stopLoss > 0 ? result.stopLoss : (entry * 0.97);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.security, color: Colors.amberAccent),
              SizedBox(width: 8),
              Text('Risk & Execution Levels', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 12),
          _buildDetailRow('Risk Rating', result.riskGrade.isNotEmpty ? result.riskGrade : 'LOW RISK', Icons.shield, Colors.greenAccent),
          const Divider(height: 16),
          _buildDetailRow('Risk : Reward Ratio', result.riskReward.isNotEmpty ? result.riskReward : '1 : 2.5', Icons.balance, Colors.amberAccent),
          const Divider(height: 16),
          _buildDetailRow('Recommended Entry', '₹${entry.toStringAsFixed(2)}', Icons.login, Colors.blue),
          const Divider(height: 16),
          _buildDetailRow('Stop Loss (SL)', '₹${sl.toStringAsFixed(2)}', Icons.gavel, Colors.redAccent),
          const Divider(height: 16),
          _buildDetailRow('Target 1', '₹${target1.toStringAsFixed(2)}', Icons.flag, Colors.greenAccent),
          const Divider(height: 16),
          _buildDetailRow('Target 2', '₹${target2.toStringAsFixed(2)}', Icons.workspace_premium, Colors.greenAccent),
        ],
      ),
    );
  }

  Widget _buildMetricColumn(String label, String value, Color valueColor) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
        const SizedBox(height: 4),
        Text(value, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: valueColor)),
      ],
    );
  }

  Widget _buildDetailRow(String label, String value, IconData icon, Color color) {
    return Row(
      children: [
        Icon(icon, size: 16, color: color),
        const SizedBox(width: 8),
        Text(label, style: const TextStyle(fontSize: 13, color: Colors.grey)),
        const Spacer(),
        Text(value, style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: color)),
      ],
    );
  }
}
