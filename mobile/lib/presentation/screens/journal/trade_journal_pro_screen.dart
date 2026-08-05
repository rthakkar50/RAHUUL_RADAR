import 'package:flutter/material.dart';
import '../../../core/network/api_config.dart';

class TradeJournalProScreen extends StatefulWidget {
  const TradeJournalProScreen({super.key});

  @override
  State<TradeJournalProScreen> createState() => _TradeJournalProScreenState();
}

class _TradeJournalProScreenState extends State<TradeJournalProScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    ApiConfig.logProductionEvent(
      'INFO',
      'Trade Journal Pro Max Screen Initialized.',
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D1117),
      appBar: AppBar(
        backgroundColor: const Color(0xFF161B22),
        elevation: 0,
        title: const Row(
          children: [
            Icon(Icons.auto_graph, color: Colors.cyanAccent, size: 20),
            SizedBox(width: 8),
            Text(
              'TRADE JOURNAL PRO MAX',
              style: TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.bold,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.file_download, color: Colors.cyanAccent, size: 20),
            tooltip: 'Export Journal (PDF/CSV)',
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Exporting Trade Journal report...')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.filter_list, color: Colors.white70, size: 20),
            tooltip: 'Filter Trades',
            onPressed: () {},
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.cyanAccent,
          labelColor: Colors.cyanAccent,
          unselectedLabelColor: Colors.white38,
          labelStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
          tabs: const [
            Tab(text: 'TIMELINE'),
            Tab(text: 'ANALYTICS'),
            Tab(text: 'PSYCHOLOGY'),
            Tab(text: 'AI REVIEW'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildTimelineTab(),
          _buildAnalyticsTab(),
          _buildPsychologyTab(),
          _buildAiReviewTab(),
        ],
      ),
    );
  }

  Widget _buildTimelineTab() {
    final trades = [
      {
        'symbol': 'RELIANCE',
        'type': 'BUY',
        'qty': '50',
        'entry': '₹2,420.00',
        'exit': '₹2,485.00',
        'pnl': '+₹3,250.00',
        'isWin': true,
        'tag': 'A+ Setup',
        'time': 'Today, 14:15 IST',
        'discipline': '95/100',
      },
      {
        'symbol': 'TCS',
        'type': 'SELL',
        'qty': '30',
        'entry': '₹3,880.00',
        'exit': '₹3,850.00',
        'pnl': '+₹900.00',
        'isWin': true,
        'tag': 'Breakout',
        'time': 'Yesterday, 11:30 IST',
        'discipline': '90/100',
      },
      {
        'symbol': 'INFY',
        'type': 'BUY',
        'qty': '100',
        'entry': '₹1,510.00',
        'exit': '₹1,495.00',
        'pnl': '-₹1,500.00',
        'isWin': false,
        'tag': 'Stop Hit',
        'time': '02 Aug, 10:45 IST',
        'discipline': '85/100',
      },
    ];

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: trades.length,
      itemBuilder: (ctx, i) {
        final item = trades[i];
        final isWin = item['isWin'] as bool;

        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 10),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
            side: BorderSide(color: isWin ? const Color(0x3300FF00) : const Color(0x33FF0000)),
          ),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: isWin ? const Color(0x3300FF00) : const Color(0x33FF0000),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        item['type'] as String,
                        style: TextStyle(
                          color: isWin ? Colors.greenAccent : Colors.redAccent,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      item['symbol'] as String,
                      style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold),
                    ),
                    const Spacer(),
                    Text(
                      item['pnl'] as String,
                      style: TextStyle(
                        color: isWin ? Colors.greenAccent : Colors.redAccent,
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Entry: ${item['entry']}', style: const TextStyle(color: Colors.white60, fontSize: 10)),
                    Text('Exit: ${item['exit']}', style: const TextStyle(color: Colors.white60, fontSize: 10)),
                    Text('Qty: ${item['qty']}', style: const TextStyle(color: Colors.white60, fontSize: 10)),
                  ],
                ),
                const SizedBox(height: 6),
                const Divider(color: Colors.white12),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: const Color(0x1FFFFFFF),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(item['tag'] as String, style: const TextStyle(color: Colors.cyanAccent, fontSize: 9)),
                    ),
                    const SizedBox(width: 8),
                    Text('Score: ${item['discipline']}', style: const TextStyle(color: Colors.amberAccent, fontSize: 9)),
                    const Spacer(),
                    Text(item['time'] as String, style: const TextStyle(color: Colors.white38, fontSize: 9)),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildAnalyticsTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(child: _statCard('Win Rate', '68.4%', Colors.greenAccent)),
              const SizedBox(width: 8),
              Expanded(child: _statCard('Profit Factor', '2.15', Colors.cyanAccent)),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(child: _statCard('Sharpe Ratio', '1.85', Colors.purpleAccent)),
              const SizedBox(width: 8),
              Expanded(child: _statCard('Max Drawdown', '-4.2%', Colors.redAccent)),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            height: 180,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF161B22),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: Colors.white12),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'EQUITY CURVE GROWTH',
                  style: TextStyle(color: Colors.white70, fontSize: 10, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Expanded(
                  child: Container(
                    alignment: Alignment.center,
                    child: CustomPaint(
                      size: const Size(double.infinity, 120),
                      painter: _EquityCurvePainter(),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _statCard(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(color: Colors.white60, fontSize: 10)),
          const SizedBox(height: 4),
          Text(value, style: TextStyle(color: color, fontSize: 16, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildPsychologyTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF161B22),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0x66E040FB)),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.psychology, color: Colors.purpleAccent, size: 16),
                    SizedBox(width: 6),
                    Text(
                      'TRADER DISCIPLINE DASHBOARD',
                      style: TextStyle(color: Colors.purpleAccent, fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                SizedBox(height: 10),
                Text('• Discipline Index: 92/100 (Optimal Control)', style: TextStyle(color: Colors.white, fontSize: 10)),
                SizedBox(height: 4),
                Text('• FOMO Frequency: 0.0% (Zero impulse entries)', style: TextStyle(color: Colors.white70, fontSize: 10)),
                SizedBox(height: 4),
                Text('• Revenge Trading Risk: LOW', style: TextStyle(color: Colors.greenAccent, fontSize: 10)),
                SizedBox(height: 4),
                Text('• Rule Compliance: 94.5% across 20 trades', style: TextStyle(color: Colors.white70, fontSize: 10)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAiReviewTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF161B22),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0x6600E5FF)),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.auto_awesome, color: Colors.cyanAccent, size: 16),
                    SizedBox(width: 6),
                    Text(
                      'AI COACH MONTHLY REVIEW',
                      style: TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                SizedBox(height: 10),
                Text(
                  'Grade: A+ (Outstanding Execution)\n\n'
                  'Key Takeaways:\n'
                  '1. Best Performing Setup: Scanner Breakout + High ADX (> 25).\n'
                  '2. Top Strength: Strict Risk-Reward compliance (Avg RR 1:2.4).\n'
                  '3. Recommended Improvement: Trail stop-loss more aggressively on gap-up open days.',
                  style: TextStyle(color: Colors.white, fontSize: 10, height: 1.4),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _EquityCurvePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.greenAccent
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;

    final path = Path();
    path.moveTo(0, size.height * 0.8);
    path.lineTo(size.width * 0.2, size.height * 0.7);
    path.lineTo(size.width * 0.4, size.height * 0.5);
    path.lineTo(size.width * 0.6, size.height * 0.6);
    path.lineTo(size.width * 0.8, size.height * 0.3);
    path.lineTo(size.width, size.height * 0.1);

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
