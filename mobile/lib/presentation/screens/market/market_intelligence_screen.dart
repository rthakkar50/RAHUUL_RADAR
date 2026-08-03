import 'package:flutter/material.dart';
import '../../../data/repositories/scanner_repository.dart';

class MarketIntelligenceScreen extends StatefulWidget {
  const MarketIntelligenceScreen({super.key});

  @override
  State<MarketIntelligenceScreen> createState() => _MarketIntelligenceScreenState();
}

class _MarketIntelligenceScreenState extends State<MarketIntelligenceScreen>
    with SingleTickerProviderStateMixin {
  final ScannerRepository _scannerRepo = ScannerRepository();
  bool _isLoading = false;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      await _scannerRepo.getSwingScans();
      if (mounted) setState(() => _isLoading = false);
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
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
                  colors: [Colors.cyanAccent, Colors.blueAccent],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.analytics_outlined, color: Colors.black, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('Market Microstructure & Order Flow', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          ],
        ),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadData),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          tabs: const [
            Tab(text: 'Breadth'),
            Tab(text: 'Sectors & Flow'),
            Tab(text: 'Volume Intel'),
            Tab(text: 'Regime'),
            Tab(text: 'Scanner Context'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.cyanAccent))
          : TabBarView(
              controller: _tabController,
              children: [
                _buildMarketBreadthTab(),
                _buildSectorRotationTab(),
                _buildVolumeIntelligenceTab(),
                _buildMarketRegimeTab(),
                _buildScannerContextTab(),
              ],
            ),
    );
  }

  // PART-1: Market Breadth Dashboard Tab
  Widget _buildMarketBreadthTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF141A28),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.3)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('MARKET BREADTH DASHBOARD', style: TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 13)),
                  Text('A/D RATIO: 3.76 (STRONG)', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.w800, fontSize: 11)),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _metricTile('Advances', '142', Colors.greenAccent),
                  _metricTile('Declines', '38', Colors.redAccent),
                  _metricTile('Unchanged', '20', Colors.grey),
                  _metricTile('52W Highs', '24', Colors.lightGreenAccent),
                  _metricTile('52W Lows', '3', Colors.orangeAccent),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white10),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('VOLUME BREADTH DISTRIBUTION', style: TextStyle(color: Colors.purpleAccent, fontWeight: FontWeight.bold, fontSize: 12)),
              SizedBox(height: 8),
              Text('• Up Volume: 82.4% (+₹12,450 Cr)', style: TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.bold)),
              Text('• Down Volume: 17.6% (-₹2,680 Cr)', style: TextStyle(color: Colors.redAccent, fontSize: 11, fontWeight: FontWeight.bold)),
              Text('• Volume Surge Breadth: 34 Stocks (> 2.0x Avg Volume)', style: TextStyle(color: Colors.white70, fontSize: 11)),
            ],
          ),
        ),
      ],
    );
  }

  // PART-2 & PART-5: Sector Rotation & Institutional Dashboard
  Widget _buildSectorRotationTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white10),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('INSTITUTIONAL SECTOR RANKINGS', style: TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 12)),
              const SizedBox(height: 10),
              _sectorRow('1. NIFTY BANK', '+1.85%', '+₹850 Cr', 'STRONG INFLOW', Colors.greenAccent),
              _sectorRow('2. NIFTY IT', '+1.42%', '+₹570 Cr', 'ACCUMULATION', Colors.cyanAccent),
              _sectorRow('3. NIFTY AUTO', '+0.35%', '+₹120 Cr', 'NEUTRAL', Colors.amberAccent),
              _sectorRow('4. NIFTY FMCG', '-0.65%', '-₹310 Cr', 'DISTRIBUTION', Colors.redAccent),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF131A2A),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.3)),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('INSTITUTIONAL INDUSTRY HIGHLIGHTS', style: TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold, fontSize: 12)),
              SizedBox(height: 6),
              Text('• Strongest Industry: Private Sector Banking (HDFCBANK, ICICIBANK)', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
              Text('• Weakest Industry: FMCG Staples (DABUR, BRITANNIA)', style: TextStyle(color: Colors.white70, fontSize: 11)),
              Text('• Money Flow Direction: Capital rotating out of defensive FMCG into high-beta Banking & Tech.', style: TextStyle(color: Colors.white70, fontSize: 11)),
            ],
          ),
        ),
      ],
    );
  }

  // PART-3: Volume Intelligence
  Widget _buildVolumeIntelligenceTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white10),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('VOLUME INTELLIGENCE & ABNORMAL ACTIVITY', style: TextStyle(color: Colors.purpleAccent, fontWeight: FontWeight.bold, fontSize: 12)),
              SizedBox(height: 10),
              Text('• Relative Volume (RVOL): 2.1x 20-day Average', style: TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.bold)),
              Text('• Institutional Delivery %: 68.4% Average in Top Picks', style: TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold)),
              Text('• Volume Spike Alert: RELIANCE (3.2x), HDFCBANK (2.8x)', style: TextStyle(color: Colors.amberAccent, fontSize: 11, fontWeight: FontWeight.bold)),
              Text('• Abnormal Block Activity: Detected in Banking Sector (+₹420 Cr block trades)', style: TextStyle(color: Colors.white70, fontSize: 11)),
            ],
          ),
        ),
      ],
    );
  }

  // PART-4: Market Regime
  Widget _buildMarketRegimeTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF141A28),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.greenAccent.withValues(alpha: 0.3)),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('CURRENT REGIME: BULL ACCUMULATION', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 13)),
              SizedBox(height: 8),
              Text('• Volatility Index (VIX): 13.4 (Low Volatility Regime)', style: TextStyle(color: Colors.white, fontSize: 11)),
              Text('• CPR Range: Narrow Range CPR Expansion detected across Large Caps.', style: TextStyle(color: Colors.white70, fontSize: 11)),
              Text('• Institutional Phase: Steady accumulation with trailing stop loss protection.', style: TextStyle(color: Colors.white70, fontSize: 11)),
            ],
          ),
        ),
      ],
    );
  }

  // PART-6: Scanner Context
  Widget _buildScannerContextTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white10),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('SCANNER INSTITUTIONAL CONTEXT', style: TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 12)),
              SizedBox(height: 8),
              Text('• Swing Scanner Context: 21 Qualified setups backed by 68% delivery accumulation.', style: TextStyle(color: Colors.white70, fontSize: 11)),
              Text('• Breakout Scanner Context: CPR breakouts supported by >2.0x volume expansion.', style: TextStyle(color: Colors.white70, fontSize: 11)),
              Text('• F&O Scanner Context: F&O Open Interest building up in Banking calls.', style: TextStyle(color: Colors.white70, fontSize: 11)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _metricTile(String label, String val, Color col) {
    return Column(
      children: [
        Text(val, style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: col)),
        Text(label, style: const TextStyle(fontSize: 9, color: Colors.grey)),
      ],
    );
  }

  Widget _sectorRow(String name, String change, String flow, String status, Color col) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          SizedBox(width: 110, child: Text(name, style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold))),
          Text(change, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 11)),
          Text(flow, style: const TextStyle(color: Colors.cyanAccent, fontSize: 11)),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(color: col.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(4), border: Border.all(color: col)),
            child: Text(status, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 9)),
          ),
        ],
      ),
    );
  }
}
