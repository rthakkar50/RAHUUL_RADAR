import 'package:flutter/material.dart';

class PaperTradingScreen extends StatefulWidget {
  const PaperTradingScreen({super.key});

  @override
  State<PaperTradingScreen> createState() => _PaperTradingScreenState();
}

class _PaperTradingScreenState extends State<PaperTradingScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

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
                gradient: const LinearGradient(
                  colors: [Colors.tealAccent, Colors.teal],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(
                Icons.note_alt_outlined,
                color: Colors.black,
                size: 18,
              ),
            ),
            const SizedBox(width: 8),
            const Text(
              'Paper Trading Engine',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
          ],
        ),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.tealAccent,
          labelColor: Colors.tealAccent,
          unselectedLabelColor: Colors.grey,
          isScrollable: true,
          tabs: const [
            Tab(text: 'Portfolio'),
            Tab(text: 'Orders'),
            Tab(text: 'Journal'),
            Tab(text: 'Analytics'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildPortfolioTab(),
          _buildOrdersTab(),
          _buildJournalTab(),
          _buildAnalyticsTab(),
        ],
      ),
    );
  }

  Widget _buildPortfolioTab() {
    return SingleChildScrollView(
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
              Text(
                'Virtual Account Balance',
                style: TextStyle(color: Colors.grey, fontSize: 11),
              ),
              Text(
                'PAPER TRADING ONLY (ZERO REAL MONEY)',
                style: TextStyle(
                  color: Colors.tealAccent,
                  fontSize: 9,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          const Row(
            children: [
              Text(
                '₹10,00,000.00',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
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
              _subTile('Buying Power', '₹40,00,000'),
              _subTile('Used Margin', '₹7,23,244'),
              _subTile('Daily P&L', '+₹1,450', col: Colors.greenAccent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _subTile(String label, String val, {Color col = Colors.white}) {
    return Column(
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
              Text(
                'Paper Trading Strategy Ranks',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 15,
                  color: Colors.white,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _leaderRow('1. Swing AI Scanner Signal', '77.1% Win', '+24.5%', Colors.greenAccent),
          const SizedBox(height: 8),
          _leaderRow('2. F&O Breakout Engine', '72.4% Win', '+18.2%', Colors.tealAccent),
          const SizedBox(height: 8),
          _leaderRow('3. Intraday Momentum V2', '68.0% Win', '+12.8%', Colors.blueAccent),
        ],
      ),
    );
  }

  Widget _leaderRow(String strat, String winRate, String pnl, Color col) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          strat,
          style: const TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.w600),
        ),
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
          Text(
            'Virtual Positions (Paper Trading)',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.white),
          ),
          SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('PAYTM (BUY) • Qty: 29', style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
              Text('+₹1,450.00', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 13)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildOrdersTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
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
              const Text('Simulated Order Preview', style: TextStyle(color: Colors.tealAccent, fontWeight: FontWeight.bold, fontSize: 14)),
              const SizedBox(height: 12),
              _orderDetailRow('Symbol', 'RELIANCE.NS'),
              _orderDetailRow('Product', 'CNC (Delivery Paper)'),
              _orderDetailRow('Order Type', 'MARKET'),
              _orderDetailRow('Entry Price', '₹1,000.00'),
              _orderDetailRow('Risk / Reward', '1 : 2.50'),
              _orderDetailRow('Estimated Charges', '₹21.00'),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.play_arrow, color: Colors.black),
                label: const Text('EXECUTE PAPER ORDER', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.tealAccent,
                  minimumSize: const Size.fromHeight(44),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _orderDetailRow(String label, String val) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
          Text(val, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 12)),
        ],
      ),
    );
  }

  Widget _buildJournalTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _journalTile('PAYTM.NS', 'BUY', '+₹1,450.00', 'WIN', 'Scanner Signal Breakout', '2026-07-25'),
        _journalTile('EXIDEIND.NS', 'BUY', '+₹234.00', 'OPEN', 'High Volume ADX', '2026-07-29'),
      ],
    );
  }

  Widget _journalTile(String sym, String sig, String pnl, String status, String strat, String date) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('$sym ($sig)', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
              const SizedBox(height: 4),
              Text('$strat • $date', style: const TextStyle(color: Colors.grey, fontSize: 11)),
            ],
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(pnl, style: TextStyle(color: pnl.contains('+') ? Colors.greenAccent : Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 13)),
              const SizedBox(height: 4),
              Text(status, style: const TextStyle(color: Colors.tealAccent, fontSize: 10, fontWeight: FontWeight.bold)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAnalyticsTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _statGrid(),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white10),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Strategy & Sector Intelligence', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
              SizedBox(height: 12),
              Text('• Best Sector: Auto & Financials', style: TextStyle(color: Colors.tealAccent, fontSize: 12)),
              SizedBox(height: 6),
              Text('• Best Time: 09:30 - 11:30 AM', style: TextStyle(color: Colors.white70, fontSize: 12)),
              SizedBox(height: 6),
              Text('• Avg Holding Time: 2.4 Days', style: TextStyle(color: Colors.white70, fontSize: 12)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _statGrid() {
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      childAspectRatio: 2.2,
      children: [
        _statBox('Win Rate', '74.2%', Colors.greenAccent),
        _statBox('Profit Factor', '2.34', Colors.tealAccent),
        _statBox('Expectancy', '₹1,025.50', Colors.white),
        _statBox('Max Drawdown', '-1.2%', Colors.amberAccent),
      ],
    );
  }

  Widget _statBox(String label, String val, Color col) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 11)),
          const SizedBox(height: 4),
          Text(val, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 16)),
        ],
      ),
    );
  }
}
