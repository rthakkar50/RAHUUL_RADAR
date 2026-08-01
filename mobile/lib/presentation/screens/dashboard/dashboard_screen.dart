import 'dart:async';
import 'package:flutter/material.dart';
import '../../../data/models/dashboard_data_model.dart';
import '../../../data/repositories/dashboard_repository.dart';
import '../notifications/notification_screen.dart';

class DashboardScreen extends StatefulWidget {
  final Function(int) onNavigate;

  const DashboardScreen({super.key, required this.onNavigate});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final DashboardRepository _repository = DashboardRepository();
  DashboardDataModel? _data;
  bool _isLoading = false;
  String? _error;
  Timer? _autoRefreshTimer;

  @override
  void initState() {
    super.initState();
    _fetchDashboard();
    _autoRefreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      if (mounted) _fetchDashboard(silent: true);
    });
  }

  @override
  void dispose() {
    _autoRefreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _fetchDashboard({bool silent = false}) async {
    if (!silent) setState(() { _isLoading = true; _error = null; });

    try {
      final data = await _repository.getDashboardData();
      if (mounted) {
        setState(() {
          _data = data;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
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
            Image.asset(
              'assets/icons/logo.png',
              height: 28,
              errorBuilder: (ctx, err, st) => const Icon(Icons.radar, color: Colors.blueAccent),
            ),
            const SizedBox(width: 8),
            const Text('RAHUUL_RADAR', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Colors.white)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const NotificationScreen()));
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : () => _fetchDashboard(),
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _data == null) {
      return const Center(child: CircularProgressIndicator(color: Colors.blueAccent));
    }

    if (_error != null && _data == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.cloud_off, color: Colors.orangeAccent, size: 48),
            const SizedBox(height: 12),
            Text(_error!, style: const TextStyle(color: Colors.white70)),
            const SizedBox(height: 16),
            ElevatedButton.icon(onPressed: _fetchDashboard, icon: const Icon(Icons.refresh), label: const Text('Retry')),
          ],
        ),
      );
    }

    final d = _data!;

    return RefreshIndicator(
      onRefresh: () => _fetchDashboard(),
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildStatusHeader(d),
            const SizedBox(height: 16),
            _buildIndicesSection(),
            const SizedBox(height: 16),
            _buildAiBiasSection(),
            const SizedBox(height: 16),
            _buildPortfolioQuickSummary(),
            const SizedBox(height: 16),
            _buildQuickActionsGrid(),
            const SizedBox(height: 16),
            _buildScannerSummaryCard(d),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusHeader(DashboardDataModel d) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Container(width: 8, height: 8, decoration: BoxDecoration(color: d.isOnline ? Colors.greenAccent : Colors.redAccent, shape: BoxShape.circle)),
              const SizedBox(width: 6),
              Text(d.isOnline ? 'ONLINE' : 'OFFLINE', style: TextStyle(color: d.isOnline ? Colors.greenAccent : Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 12)),
            ],
          ),
          Text(d.marketStatus, style: const TextStyle(color: Colors.white70, fontWeight: FontWeight.w600, fontSize: 12)),
          Text('Scan: ${d.lastScanTime}', style: const TextStyle(color: Colors.grey, fontSize: 11)),
        ],
      ),
    );
  }

  Widget _buildIndicesSection() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _indexCard('NIFTY 50', '24,850.40', '+184.20 (+0.75%)', Colors.greenAccent),
          const SizedBox(width: 10),
          _indexCard('BANK NIFTY', '52,450.15', '+410.50 (+0.79%)', Colors.greenAccent),
          const SizedBox(width: 10),
          _indexCard('FINNIFTY', '23,150.80', '+142.10 (+0.62%)', Colors.greenAccent),
          const SizedBox(width: 10),
          _indexCard('INDIA VIX', '12.45', '-0.45 (-3.48%)', Colors.cyanAccent),
        ],
      ),
    );
  }

  Widget _indexCard(String title, String val, String chg, Color col) {
    return Container(
      padding: const EdgeInsets.all(12),
      width: 135,
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(color: Colors.grey, fontSize: 10)),
          const SizedBox(height: 4),
          Text(val, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
          const SizedBox(height: 2),
          Text(chg, style: TextStyle(color: col, fontSize: 10, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  Widget _buildAiBiasSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(colors: [Colors.blue.shade900.withValues(alpha: 0.4), const Color(0xFF161B22)]),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(Icons.auto_awesome, color: Colors.cyanAccent, size: 18),
                  SizedBox(width: 6),
                  Text('AI Market Intelligence Panel', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.white)),
                ],
              ),
              Text('BULLISH / ACCUMULATION', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 11)),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(color: Colors.white10, height: 1),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _biasItem('Trend Strength', '88.4 / 100', Colors.cyanAccent),
              _biasItem('Market Breadth', '132 Adv / 44 Dec', Colors.greenAccent),
              _biasItem('AI Confidence', '94.2%', Colors.amberAccent),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(color: Colors.purple.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(8), border: Border.all(color: Colors.purpleAccent.withValues(alpha: 0.3))),
            child: const Row(
              children: [
                Icon(Icons.lightbulb_outline, color: Colors.purpleAccent, size: 16),
                SizedBox(width: 6),
                Expanded(
                  child: Text('AI RECOMMENDATION: Prefer Pharma & Auto. Avoid Fresh Shorts in Banking.', style: TextStyle(color: Colors.purpleAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }

  Widget _biasItem(String label, String val, Color col) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 2),
        Text(val, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 12)),
      ],
    );
  }

  Widget _buildPortfolioQuickSummary() {
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
              Text('Portfolio Quick Snapshot', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
              Text('Risk Meter: LOW (0.69%)', style: TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 12),
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('Total Equity', style: TextStyle(color: Colors.grey, fontSize: 10)),
                Text('₹9,93,101.13', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
              ]),
              Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
                Text('Today P&L', style: TextStyle(color: Colors.grey, fontSize: 10)),
                Text('+₹1,450.00', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 16)),
              ]),
            ],
          )
        ],
      ),
    );
  }

  Widget _buildQuickActionsGrid() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Quick Institutional Actions', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
        const SizedBox(height: 10),
        Row(
          children: [
            Expanded(child: _actionBtn('Scanner', Icons.radar, Colors.blueAccent, () => widget.onNavigate(1))),
            const SizedBox(width: 8),
            Expanded(child: _actionBtn('F&O Engine', Icons.show_chart, Colors.purpleAccent, () => widget.onNavigate(2))),
            const SizedBox(width: 8),
            Expanded(child: _actionBtn('Portfolio', Icons.pie_chart, Colors.cyanAccent, () => widget.onNavigate(3))),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(child: _actionBtn('Journal', Icons.menu_book, Colors.amberAccent, () => widget.onNavigate(4))),
            const SizedBox(width: 8),
            Expanded(child: _actionBtn('Paper Trade', Icons.note_alt, Colors.tealAccent, () => widget.onNavigate(5))),
            const SizedBox(width: 8),
            Expanded(child: _actionBtn('Quant Lab', Icons.science, Colors.indigoAccent, () => widget.onNavigate(5))),
          ],
        ),
      ],
    );
  }

  Widget _actionBtn(String label, IconData icon, Color col, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        decoration: BoxDecoration(
          color: const Color(0xFF161B22),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: col.withValues(alpha: 0.3)),
        ),
        child: Column(
          children: [
            Icon(icon, color: col, size: 20),
            const SizedBox(height: 4),
            Text(label, style: const TextStyle(color: Colors.white70, fontSize: 11, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }

  Widget _buildScannerSummaryCard(DashboardDataModel d) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('AI Swing Scanner', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
            const SizedBox(height: 2),
            Text('${d.qualifiedSignals} High Confidence Signals Out of ${d.totalScanned}', style: const TextStyle(color: Colors.grey, fontSize: 11)),
          ]),
          ElevatedButton(
            onPressed: () => widget.onNavigate(1),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
            child: const Text('View All'),
          ),
        ],
      ),
    );
  }
}
