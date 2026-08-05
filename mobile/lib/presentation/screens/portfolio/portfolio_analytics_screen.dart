import 'package:flutter/material.dart';
import '../../../core/network/api_config.dart';

class PortfolioAnalyticsScreen extends StatefulWidget {
  const PortfolioAnalyticsScreen({super.key});

  @override
  State<PortfolioAnalyticsScreen> createState() =>
      _PortfolioAnalyticsScreenState();
}

class _PortfolioAnalyticsScreenState extends State<PortfolioAnalyticsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    ApiConfig.logProductionEvent(
      'INFO',
      'Institutional Portfolio Analytics Screen Initialized.',
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
            Icon(Icons.pie_chart, color: Colors.cyanAccent, size: 20),
            SizedBox(width: 8),
            Text(
              'PORTFOLIO ANALYTICS & RISK LAB',
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
            icon: const Icon(Icons.refresh, color: Colors.cyanAccent, size: 20),
            tooltip: 'Rebalance Portfolio',
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Portfolio rebalancing calculation completed.')),
              );
            },
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.cyanAccent,
          labelColor: Colors.cyanAccent,
          unselectedLabelColor: Colors.white38,
          labelStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
          tabs: const [
            Tab(text: 'OVERVIEW'),
            Tab(text: 'RISK LAB'),
            Tab(text: 'STRESS TEST'),
            Tab(text: 'BENCHMARK'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildOverviewTab(),
          _buildRiskLabTab(),
          _buildStressTestTab(),
          _buildBenchmarkTab(),
        ],
      ),
    );
  }

  Widget _buildOverviewTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF161B22),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0x3300FFFF)),
            ),
            child: Column(
              children: [
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('TOTAL NET WORTH', style: TextStyle(color: Colors.white60, fontSize: 11)),
                    Text('PORTFOLIO HEALTH: 94/100', style: TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                  ],
                ),
                const SizedBox(height: 6),
                const Row(
                  children: [
                    Text(
                      '₹12,45,800.00',
                      style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold),
                    ),
                    SizedBox(width: 8),
                    Text(
                      '+₹18,450.00 (+1.5%)',
                      style: TextStyle(color: Colors.greenAccent, fontSize: 12, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                const Divider(color: Colors.white12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _metricItem('CAGR', '24.8%'),
                    _metricItem('XIRR', '28.2%'),
                    _metricItem('Cash Allocation', '15.5%'),
                    _metricItem('Beta', '0.85'),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'SECTOR ALLOCATION',
            style: TextStyle(color: Colors.white70, fontSize: 11, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          _sectorRow('Banking & Finance', '38.5%', Colors.blueAccent),
          _sectorRow('IT & Technology', '26.2%', Colors.cyanAccent),
          _sectorRow('Automobile', '18.3%', Colors.purpleAccent),
          _sectorRow('Energy & Metals', '17.0%', Colors.amberAccent),
        ],
      ),
    );
  }

  Widget _metricItem(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.white38, fontSize: 9)),
        const SizedBox(height: 2),
        Text(value, style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
      ],
    );
  }

  Widget _sectorRow(String name, String percent, Color color) {
    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Container(width: 10, height: 10, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
          const SizedBox(width: 8),
          Text(name, style: const TextStyle(color: Colors.white, fontSize: 11)),
          const Spacer(),
          Text(percent, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildRiskLabTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(child: _riskCard('Value at Risk (95%)', '₹18,400.00', Colors.amberAccent)),
              const SizedBox(width: 8),
              Expanded(child: _riskCard('Expected Shortfall', '₹26,800.00', Colors.redAccent)),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(child: _riskCard('Portfolio Alpha', '+4.8%', Colors.greenAccent)),
              const SizedBox(width: 8),
              Expanded(child: _riskCard('Diversification Score', '88/100', Colors.cyanAccent)),
            ],
          ),
          const SizedBox(height: 12),
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
                    Icon(Icons.shield, color: Colors.purpleAccent, size: 16),
                    SizedBox(width: 6),
                    Text(
                      'AI RISK ADVISOR RECOMMENDATION',
                      style: TextStyle(color: Colors.purpleAccent, fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                SizedBox(height: 8),
                Text(
                  '• Concentration Risk: High exposure in Banking (38.5%). Consider rebalancing 5% into Defensive FMCG.\n'
                  '• Correlation Matrix: RELIANCE & ICICIBANK exhibit 0.42 low correlation (Good Hedging).\n'
                  '• Volatility Index: Portfolio Volatility is 11.2% vs NIFTY 13.8% (Lower Risk).',
                  style: TextStyle(color: Colors.white, fontSize: 10, height: 1.4),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _riskCard(String label, String value, Color color) {
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
          Text(value, style: TextStyle(color: color, fontSize: 15, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildStressTestTab() {
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        _stressCard('Market Crash (-5.0%)', '-₹52,400.00 (-4.2%)', 'PASSED (Within Risk Limit)', Colors.amberAccent),
        _stressCard('Market Crash (-10.0%)', '-₹108,200.00 (-8.6%)', 'PASSED (Stop-Loss Active)', Colors.redAccent),
        _stressCard('Interest Rate Hike (+50 bps)', '-₹14,500.00 (-1.1%)', 'PASSED', Colors.cyanAccent),
        _stressCard('India VIX Volatility Spike (+25%)', '-₹22,100.00 (-1.7%)', 'PASSED', Colors.purpleAccent),
      ],
    );
  }

  Widget _stressCard(String scenario, String impact, String status, Color color) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(scenario, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Simulated Impact: $impact', style: const TextStyle(color: Colors.white, fontSize: 10)),
              Text(status, style: const TextStyle(color: Colors.greenAccent, fontSize: 9, fontWeight: FontWeight.bold)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildBenchmarkTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF161B22),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: Colors.cyanAccent),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'BENCHMARK COMPARISON (VS NIFTY 50)',
                  style: TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 10),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Portfolio Return: +18.4%', style: TextStyle(color: Colors.greenAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                    Text('NIFTY 50 Return: +13.6%', style: TextStyle(color: Colors.white70, fontSize: 10)),
                  ],
                ),
                SizedBox(height: 6),
                Divider(color: Colors.white12),
                SizedBox(height: 4),
                Text('• Alpha: +4.8% (Outperforming Benchmark)', style: TextStyle(color: Colors.white, fontSize: 10)),
                SizedBox(height: 4),
                Text('• Tracking Error: 3.2%', style: TextStyle(color: Colors.white70, fontSize: 10)),
                SizedBox(height: 4),
                Text('• Information Ratio: 1.50 (High Efficiency)', style: TextStyle(color: Colors.cyanAccent, fontSize: 10, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
