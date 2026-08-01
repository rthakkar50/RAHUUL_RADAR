import 'package:flutter/material.dart';
import '../../../data/models/scan_result_model.dart';

class StockDetailScreen extends StatelessWidget {
  final ScanResultModel result;

  const StockDetailScreen({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final isBuy = result.signal.toUpperCase().contains('BUY');
    final sigColor = isBuy ? Colors.greenAccent : Colors.redAccent;

    final target3 = result.entry > 0 ? (isBuy ? result.entry * 1.25 : result.entry * 0.75) : 0.0;

    return Scaffold(
      backgroundColor: const Color(0xFF0B0E14),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B0E14),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(result.symbol, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            Text(result.company, style: const TextStyle(fontSize: 11, color: Colors.grey)),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: sigColor.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: sigColor),
            ),
            child: Text(result.signal.toUpperCase(), style: TextStyle(color: sigColor, fontWeight: FontWeight.bold, fontSize: 12)),
          )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Price Banner
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Current Price', style: TextStyle(color: Colors.grey, fontSize: 11)),
                    const SizedBox(height: 2),
                    Text('₹${result.price.toStringAsFixed(2)}', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white)),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    const Text('AI Score / Confidence', style: TextStyle(color: Colors.grey, fontSize: 11)),
                    const SizedBox(height: 2),
                    Row(
                      children: [
                        const Icon(Icons.auto_awesome, color: Colors.cyanAccent, size: 16),
                        const SizedBox(width: 4),
                        Text('${result.score.toStringAsFixed(1)} / ${result.confidence.toStringAsFixed(1)}%', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.cyanAccent)),
                      ],
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Candlestick Chart Placeholder / Visual Canvas
            Container(
              height: 180,
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF161B22),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.white10),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Price Action & EMA Trend', style: TextStyle(color: Colors.grey, fontSize: 11, fontWeight: FontWeight.bold)),
                      Text('Sector: ${result.sector}', style: const TextStyle(color: Colors.blueAccent, fontSize: 11)),
                    ],
                  ),
                  const Spacer(),
                  Center(
                    child: Column(
                      children: [
                        Icon(isBuy ? Icons.show_chart : Icons.multiline_chart, color: sigColor, size: 48),
                        const SizedBox(height: 8),
                        Text('Bullish Breakout Above 20 & 50 EMA (${result.trend})', style: const TextStyle(color: Colors.white70, fontSize: 12)),
                      ],
                    ),
                  ),
                  const Spacer(),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Target & Risk Levels Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF161B22),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.white10),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Trading Plan & Targets', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.white)),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _levelTile('Entry', '₹${result.entry.toStringAsFixed(2)}', Colors.blueAccent),
                      _levelTile('Stop Loss', '₹${result.stopLoss.toStringAsFixed(2)}', Colors.redAccent),
                      _levelTile('Target 1', '₹${result.target1.toStringAsFixed(2)}', Colors.greenAccent),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Divider(color: Colors.white10, height: 1),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _levelTile('Target 2', '₹${result.target2.toStringAsFixed(2)}', Colors.greenAccent),
                      _levelTile('Target 3', '₹${target3.toStringAsFixed(2)}', Colors.amberAccent),
                      _levelTile('R : R', result.riskReward, Colors.cyanAccent),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Technicals & XAI Explanation
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF161B22),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.white10),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.psychology, color: Colors.purpleAccent, size: 20),
                      SizedBox(width: 6),
                      Text('XAI Explainable AI Analysis', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.white)),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    '${result.symbol} is showing a high-probability ${result.signal} signal with an AI Confidence of ${result.confidence.toStringAsFixed(1)}%. Volume expansion is ${result.volume} with Relative Strength RS Score of ${result.rsScore.toStringAsFixed(1)}. Trade Grade: ${result.tradeGrade} | Risk Grade: ${result.riskGrade}.',
                    style: const TextStyle(color: Colors.white70, fontSize: 12, height: 1.4),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      _tagBadge('Trend: ${result.trend}', Colors.blueAccent),
                      const SizedBox(width: 8),
                      _tagBadge('Vol: ${result.volume}', Colors.amberAccent),
                    ],
                  )
                ],
              ),
            )
          ],
        ),
      ),
    );
  }

  Widget _levelTile(String label, String val, Color col) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 2),
        Text(val, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 13)),
      ],
    );
  }

  Widget _tagBadge(String text, Color col) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: col.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: col.withValues(alpha: 0.3)),
      ),
      child: Text(text, style: TextStyle(color: col, fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }
}
