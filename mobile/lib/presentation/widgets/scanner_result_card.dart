import 'package:flutter/material.dart';
import '../../data/models/scan_result_model.dart';
import '../screens/stock_detail/stock_detail_screen.dart';

class ScannerResultCard extends StatelessWidget {
  final ScanResultModel result;

  const ScannerResultCard({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final isBuy = result.signal.toUpperCase().contains('BUY');
    final sigColor = isBuy ? Colors.greenAccent : Colors.redAccent;
    final target3 = result.entry > 0
        ? (isBuy ? result.entry * 1.25 : result.entry * 0.75)
        : 0.0;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: sigColor.withValues(alpha: 0.3), width: 1.2),
      ),
      color: const Color(0xFF161B22),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => StockDetailScreen(result: result),
            ),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Row 1: Symbol, Company & Signal Badge
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            result.symbol,
                            style: const TextStyle(
                              fontSize: 17,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          const SizedBox(width: 6),
                          _gradeBadge(result.tradeGrade, Colors.amberAccent),
                        ],
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${result.company} • ${result.sector}',
                        style: const TextStyle(
                          color: Colors.grey,
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 5,
                    ),
                    decoration: BoxDecoration(
                      color: sigColor.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: sigColor, width: 1.2),
                    ),
                    child: Text(
                      result.signal.toUpperCase(),
                      style: TextStyle(
                        color: sigColor,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              const Divider(color: Colors.white10, height: 1),
              const SizedBox(height: 10),

              // Row 2: Price, AI Score, Confidence & RS Score
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _stat(
                    'Price',
                    '₹${result.price.toStringAsFixed(2)}',
                    Colors.white,
                  ),
                  _stat(
                    'AI Score',
                    result.score.toStringAsFixed(1),
                    Colors.cyanAccent,
                  ),
                  _stat(
                    'Confidence',
                    '${result.confidence.toStringAsFixed(1)}%',
                    Colors.purpleAccent,
                  ),
                  _stat(
                    'RS Score',
                    result.rsScore.toStringAsFixed(1),
                    Colors.amberAccent,
                  ),
                ],
              ),
              const SizedBox(height: 10),

              // Row 3: Entry, SL, Target 1, Target 2, Target 3
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 8,
                ),
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _level(
                      'Entry',
                      '₹${result.entry.toStringAsFixed(1)}',
                      Colors.blueAccent,
                    ),
                    _level(
                      'SL',
                      '₹${result.stopLoss.toStringAsFixed(1)}',
                      Colors.redAccent,
                    ),
                    _level(
                      'T1',
                      '₹${result.target1.toStringAsFixed(1)}',
                      Colors.greenAccent,
                    ),
                    _level(
                      'T2',
                      '₹${result.target2.toStringAsFixed(1)}',
                      Colors.greenAccent,
                    ),
                    _level(
                      'T3',
                      '₹${target3.toStringAsFixed(1)}',
                      Colors.amberAccent,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 10),

              // Row 4: Indicators & Risk Grade
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      _badge('R:R ${result.riskReward}', Colors.cyanAccent),
                      const SizedBox(width: 6),
                      _badge('Vol ${result.volume}', Colors.amberAccent),
                    ],
                  ),
                  Text(
                    'Risk Grade: ${result.riskGrade}',
                    style: const TextStyle(
                      color: Colors.grey,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _stat(String label, String val, Color col) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 2),
        Text(
          val,
          style: TextStyle(
            color: col,
            fontWeight: FontWeight.bold,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _level(String label, String val, Color col) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 9)),
        const SizedBox(height: 2),
        Text(
          val,
          style: TextStyle(
            color: col,
            fontWeight: FontWeight.bold,
            fontSize: 11,
          ),
        ),
      ],
    );
  }

  Widget _gradeBadge(String grade, Color col) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
      decoration: BoxDecoration(
        color: col.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: col, width: 0.8),
      ),
      child: Text(
        grade,
        style: TextStyle(color: col, fontSize: 9, fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget _badge(String text, Color col) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: col.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: TextStyle(color: col, fontSize: 10, fontWeight: FontWeight.bold),
      ),
    );
  }
}
