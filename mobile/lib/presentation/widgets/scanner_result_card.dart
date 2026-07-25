import 'package:flutter/material.dart';
import '../../data/models/scan_result_model.dart';
import '../../core/theme/app_theme.dart';
import '../screens/stock_detail/stock_detail_screen.dart';

class ScannerResultCard extends StatelessWidget {
  final ScanResultModel result;

  const ScannerResultCard({super.key, required this.result});

  Color _getSignalColor(String signal) {
    final upper = signal.toUpperCase();
    if (upper.contains('BUY')) return AppTheme.buyColor;
    if (upper.contains('SELL')) return AppTheme.sellColor;
    return AppTheme.watchColor;
  }

  @override
  Widget build(BuildContext context) {
    final signalColor = _getSignalColor(result.signal);

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => StockDetailScreen(result: result),
            ),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      result.symbol,
                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: signalColor.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: signalColor),
                    ),
                    child: Text(
                      result.signal,
                      style: TextStyle(color: signalColor, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                '${result.company} • ${result.sector}',
                style: const TextStyle(color: Colors.grey, fontSize: 12),
              ),
              const Divider(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildStat('Score', '${result.score}', Colors.white),
                  _buildStat('Confidence', '${result.confidence}%', Colors.white),
                  _buildStat('R:R', result.riskReward, Colors.white),
                  _buildStat('Grade', result.tradeGrade.isNotEmpty ? result.tradeGrade : '--', Colors.amber),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildLevel('Entry', result.entry, Colors.blue),
                  _buildLevel('Stop Loss', result.stopLoss, Colors.redAccent),
                  _buildLevel('Target 1', result.target1, Colors.greenAccent),
                ],
              ),
              const SizedBox(height: 8),
              Align(
                alignment: Alignment.centerRight,
                child: Text(
                  result.timestamp,
                  style: const TextStyle(color: Colors.grey, fontSize: 10),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStat(String label, String value, Color valueColor) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
        const SizedBox(height: 4),
        Text(value, style: TextStyle(color: valueColor, fontWeight: FontWeight.bold, fontSize: 14)),
      ],
    );
  }

  Widget _buildLevel(String label, double value, Color color) {
    return Row(
      children: [
        Text('$label: ', style: const TextStyle(color: Colors.grey, fontSize: 12)),
        Text(value.toStringAsFixed(2), style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 12)),
      ],
    );
  }
}
