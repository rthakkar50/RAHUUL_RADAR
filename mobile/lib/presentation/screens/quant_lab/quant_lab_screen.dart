import 'package:flutter/material.dart';

class QuantLabScreen extends StatefulWidget {
  const QuantLabScreen({super.key});

  @override
  State<QuantLabScreen> createState() => _QuantLabScreenState();
}

class _QuantLabScreenState extends State<QuantLabScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0E14),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B0E14),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Colors.indigoAccent, Colors.blue]),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.science_outlined, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('Quant Research Lab', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildMetricsGrid(),
            const SizedBox(height: 16),
            _buildSimulationCard(),
            const SizedBox(height: 16),
            _buildEquityCurveCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricsGrid() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Statistical Risk & Performance Engine', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.white)),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _quantTile('Sharpe Ratio', '2.18', Colors.greenAccent),
              _quantTile('Sortino Ratio', '3.42', Colors.cyanAccent),
              _quantTile('Calmar Ratio', '4.12', Colors.purpleAccent),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(color: Colors.white10, height: 1),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _quantTile('Win Rate', '74.2%', Colors.amberAccent),
              _quantTile('Profit Factor', '2.45', Colors.lightGreenAccent),
              _quantTile('Max Drawdown', '-4.12%', Colors.redAccent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _quantTile(String label, String val, Color col) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 3),
        Text(val, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 14)),
      ],
    );
  }

  Widget _buildSimulationCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.auto_graph, color: Colors.indigoAccent, size: 18),
              SizedBox(width: 6),
              Text('Monte Carlo & Walk Forward Robustness', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.white)),
            ],
          ),
          SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Monte Carlo (10,000 Sims):', style: TextStyle(color: Colors.white70, fontSize: 12)),
              Text('99.2% Survival', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 12)),
            ],
          ),
          SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Walk Forward Out-Of-Sample:', style: TextStyle(color: Colors.white70, fontSize: 12)),
              Text('89.5% Consistency', style: TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 12)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildEquityCurveCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Cumulative Equity Waterfall', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.white)),
          SizedBox(height: 12),
          Center(
            child: Icon(Icons.stacked_line_chart, color: Colors.cyanAccent, size: 56),
          ),
          SizedBox(height: 8),
          Center(
            child: Text('Smooth Upward Slope • Alpha Outperformance vs NIFTY 50', style: TextStyle(color: Colors.white54, fontSize: 11)),
          ),
        ],
      ),
    );
  }
}
