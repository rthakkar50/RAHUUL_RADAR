import 'package:flutter/material.dart';
import '../../../data/models/scan_result_model.dart';

class StockDetailScreen extends StatelessWidget {
  final ScanResultModel result;

  const StockDetailScreen({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(result.symbol),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(result.company, style: Theme.of(context).textTheme.headlineSmall),
            Text(result.sector, style: const TextStyle(color: Colors.grey)),
            const SizedBox(height: 24),
            const Text('Trade Details', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const Divider(),
            ListTile(title: const Text('Signal'), trailing: Text(result.signal, style: const TextStyle(fontWeight: FontWeight.bold))),
            ListTile(title: const Text('Entry'), trailing: Text(result.entry.toStringAsFixed(2))),
            ListTile(title: const Text('Stop Loss'), trailing: Text(result.stopLoss.toStringAsFixed(2))),
            ListTile(title: const Text('Target 1'), trailing: Text(result.target1.toStringAsFixed(2))),
            ListTile(title: const Text('Target 2'), trailing: Text(result.target2.toStringAsFixed(2))),
            const SizedBox(height: 24),
            const Text('AI & Quality', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const Divider(),
            ListTile(title: const Text('Score'), trailing: Text(result.score.toString())),
            ListTile(title: const Text('Confidence'), trailing: Text('${result.confidence}%')),
            ListTile(title: const Text('Trend'), trailing: Text(result.trend)),
            ListTile(title: const Text('Risk Grade'), trailing: Text(result.riskGrade)),
          ],
        ),
      ),
    );
  }
}
