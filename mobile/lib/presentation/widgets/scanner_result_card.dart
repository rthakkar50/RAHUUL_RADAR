import 'package:flutter/material.dart';
import '../../data/models/scan_result_model.dart';
import '../screens/stock_detail/stock_detail_screen.dart';

class ScannerResultCard extends StatelessWidget {
  final ScanResultModel result;

  const ScannerResultCard({super.key, required this.result});

  Color _getSignalColor(String signal) {
    final upper = signal.toUpperCase();
    if (upper.contains('BUY')) {
      return Colors.greenAccent;
    } else if (upper.contains('SELL')) {
      return Colors.redAccent;
    } else {
      return Colors.orangeAccent;
    }
  }

  @override
  Widget build(BuildContext context) {
    final signalColor = _getSignalColor(result.signal);

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: signalColor.withValues(alpha: 0.3), width: 1),
      ),
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
          padding: const EdgeInsets.all(14.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header: Symbol & Signal Badge
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          result.symbol,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 0.5,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                        if (result.company.isNotEmpty) ...[
                          const SizedBox(height: 2),
                          Text(
                            result.company,
                            style: const TextStyle(color: Colors.grey, fontSize: 12),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: signalColor.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: signalColor, width: 1.2),
                    ),
                    child: Text(
                      result.signal,
                      style: TextStyle(
                        color: signalColor,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              const Divider(height: 1),
              const SizedBox(height: 12),

              // Metrics Row: Score, Confidence, R:R, Sector
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildStat('Score', result.score.toStringAsFixed(1), Colors.white),
                  _buildStat('Confidence', '${result.confidence.toStringAsFixed(0)}%', Colors.blueAccent),
                  _buildStat('R:R', result.riskReward.isNotEmpty ? result.riskReward : '1:2.0', Colors.amberAccent),
                  _buildStat('Sector', result.sector.isNotEmpty ? result.sector : 'N/A', Colors.grey),
                ],
              ),

              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _buildLevel('Entry', '₹${result.entry.toStringAsFixed(2)}', Colors.blue),
                    _buildLevel('SL', '₹${result.stopLoss.toStringAsFixed(2)}', Colors.redAccent),
                    _buildLevel(
                      'Target',
                      '₹${result.target1 > 0 ? result.target1.toStringAsFixed(2) : (result.entry * 1.05).toStringAsFixed(2)}',
                      Colors.greenAccent,
                    ),
                  ],
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
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 3),
        Text(
          value,
          style: TextStyle(
            color: valueColor,
            fontWeight: FontWeight.bold,
            fontSize: 13,
          ),
          overflow: TextOverflow.ellipsis,
        ),
      ],
    );
  }

  Widget _buildLevel(String label, String value, Color color) {
    return Row(
      children: [
        Text('$label: ', style: const TextStyle(color: Colors.grey, fontSize: 11)),
        Text(
          value,
          style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 12),
        ),
      ],
    );
  }
}
