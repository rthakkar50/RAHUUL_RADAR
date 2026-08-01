import 'package:flutter/material.dart';

class PaperTradingScreen extends StatefulWidget {
  const PaperTradingScreen({super.key});

  @override
  State<PaperTradingScreen> createState() => _PaperTradingScreenState();
}

class _PaperTradingScreenState extends State<PaperTradingScreen> {
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
                gradient: const LinearGradient(colors: [Colors.tealAccent, Colors.teal]),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.note_alt_outlined, color: Colors.black, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('Paper Trading Engine', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildBalanceCard(),
            const SizedBox(height: 16),
            _buildLeaderboardCard(),
            const SizedBox(height: 16),
            _buildVirtualPositionsCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildBalanceCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        children: [
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Virtual Balance', style: TextStyle(color: Colors.grey, fontSize: 11)),
              Text('REALTIME SIMULATION', style: TextStyle(color: Colors.tealAccent, fontSize: 10, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 6),
          const Row(
            children: [
              Text('₹10,00,000.00', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white)),
              Spacer(),
              Icon(Icons.verified, color: Colors.tealAccent, size: 20),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(color: Colors.white10, height: 1),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _subTile('Margin', '₹7,23,244'),
              _subTile('Equity', '₹9,93,101'),
              _subTile('Daily P&L', '+₹1,450', col: Colors.greenAccent),
            ],
          )
        ],
      ),
    );
  }

  Widget _subTile(String label, String val, {Color col = Colors.white}) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 2),
        Text(val, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 12)),
      ],
    );
  }

  Widget _buildLeaderboardCard() {
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
          const Row(
            children: [
              Icon(Icons.emoji_events, color: Colors.amberAccent, size: 18),
              SizedBox(width: 6),
              Text('Strategy Leaderboard', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.white)),
            ],
          ),
          const SizedBox(height: 12),
          _leaderRow('1. Swing AI Alpha (RF+GBM)', '77.1% Win', '+24.5%', Colors.greenAccent),
          const SizedBox(height: 8),
          _leaderRow('2. F&O Hedged Momentum', '72.4% Win', '+18.2%', Colors.tealAccent),
          const SizedBox(height: 8),
          _leaderRow('3. Intraday Breakout V2', '68.0% Win', '+12.8%', Colors.blueAccent),
        ],
      ),
    );
  }

  Widget _leaderRow(String strat, String winRate, String pnl, Color col) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(strat, style: const TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.w600)),
        Row(
          children: [
            Text(winRate, style: const TextStyle(color: Colors.grey, fontSize: 11)),
            const SizedBox(width: 10),
            Text(pnl, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 12)),
          ],
        ),
      ],
    );
  }

  Widget _buildVirtualPositionsCard() {
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
          Text('Virtual Positions (Paper Trading)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.white)),
          SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('PAYTM (BUY) • Qty: 29', style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
              Text('+₹1,450.00', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 13)),
            ],
          )
        ],
      ),
    );
  }
}
