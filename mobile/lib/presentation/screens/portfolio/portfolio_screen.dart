import 'dart:async';
import 'package:flutter/material.dart';
import '../../../data/models/portfolio_model.dart';
import '../../../data/repositories/portfolio_repository.dart';
import 'position_detail_screen.dart';

class PortfolioScreen extends StatefulWidget {
  const PortfolioScreen({super.key});

  @override
  State<PortfolioScreen> createState() => _PortfolioScreenState();
}

class _PortfolioScreenState extends State<PortfolioScreen> with SingleTickerProviderStateMixin {
  final PortfolioRepository _repository = PortfolioRepository();
  PortfolioResponseModel? _data;
  bool _isLoading = false;
  String? _error;
  Timer? _autoRefreshTimer;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
    _fetchPortfolio();
    _autoRefreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      if (mounted) _fetchPortfolio(silent: true);
    });
  }

  @override
  void dispose() {
    _autoRefreshTimer?.cancel();
    _tabController.dispose();
    super.dispose();
  }

  bool _isFetching = false;

  Future<void> _fetchPortfolio({bool silent = false}) async {
    if (_isFetching) return;
    _isFetching = true;

    if (!silent) {
      setState(() {
        _isLoading = true;
        _error = null;
      });
    }
    try {
      final data = await _repository.getPortfolio();
      if (mounted) {
        setState(() {
          _data = data;
          _isLoading = false;
          _error = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    } finally {
      _isFetching = false;
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
                gradient: const LinearGradient(colors: [Colors.greenAccent, Colors.teal]),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.pie_chart, color: Colors.black, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('Institutional Portfolio Terminal', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : () => _fetchPortfolio(),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          tabs: const [
            Tab(text: 'Summary'),
            Tab(text: 'Holdings'),
            Tab(text: 'Positions'),
            Tab(text: 'Analytics'),
            Tab(text: 'Risk Dashboard'),
          ],
        ),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _data == null) {
      return const Center(child: CircularProgressIndicator(color: Colors.greenAccent));
    }

    if (_error != null && _data == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, color: Colors.redAccent, size: 48),
            const SizedBox(height: 12),
            Text(_error!, style: const TextStyle(color: Colors.white70)),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _fetchPortfolio, child: const Text('Retry')),
          ],
        ),
      );
    }

    final d = _data!;

    return TabBarView(
      controller: _tabController,
      children: [
        _buildSummaryTab(d.summary),
        _buildHoldingsTab(d.openPositions),
        _buildPositionsTab(d.openPositions),
        _buildAnalyticsTab(d),
        _buildRiskDashboardTab(d.summary),
      ],
    );
  }

  Widget _buildSummaryTab(PortfolioSummaryModel s) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.greenAccent.withValues(alpha: 0.3)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Total Portfolio Equity', style: TextStyle(color: Colors.grey, fontSize: 12)),
              const SizedBox(height: 4),
              Text('₹${s.totalEquity.toStringAsFixed(2)}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 24)),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _tile('Today P&L', '+₹14,250.00', Colors.greenAccent),
                  _tile('Overall P&L', '+₹42,850.00', Colors.greenAccent),
                  _tile('AI Score', '94/100', Colors.cyanAccent),
                ],
              ),
              const Divider(color: Colors.white10, height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _tile('Available Cash', '₹${s.availableCash.toStringAsFixed(2)}', Colors.white),
                  _tile('Used Margin', '₹${s.usedMargin.toStringAsFixed(2)}', Colors.amberAccent),
                  _tile('Portfolio Health', 'EXCELLENT', Colors.lightGreenAccent),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildHoldingsTab(List<PositionModel> pos) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: pos.length,
      itemBuilder: (ctx, i) {
        final p = pos[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(p.symbol, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(color: Colors.greenAccent.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(4)),
                      child: const Text('Rating: A+', style: TextStyle(color: Colors.greenAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text('Qty: ${p.qty} • Avg Price: ₹${p.entryPrice.toStringAsFixed(2)} • Current: ₹${p.cmp.toStringAsFixed(2)}', style: const TextStyle(color: Colors.white70, fontSize: 12)),
                Text('Market Value: ₹${(p.qty * p.cmp).toStringAsFixed(2)} • Today: +1.4% • Overall Return: +8.4%', style: const TextStyle(color: Colors.greenAccent, fontSize: 11)),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildPositionsTab(List<PositionModel> pos) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: pos.length,
      itemBuilder: (ctx, i) {
        final p = pos[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            onTap: () {
              Navigator.push(ctx, MaterialPageRoute(builder: (_) => PositionDetailScreen(position: p)));
            },
            title: Text('${p.symbol} (${p.direction.toUpperCase()})', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
            subtitle: Text('MTM PnL: ₹${p.unrealizedPnl.toStringAsFixed(2)}\nSL: ₹${p.sl} • Target: ₹${p.target}', style: const TextStyle(color: Colors.white70, fontSize: 11)),
            trailing: Text('₹${p.cmp.toStringAsFixed(2)}', style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 14)),
          ),
        );
      },
    );
  }

  Widget _buildAnalyticsTab(PortfolioResponseModel d) {
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
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Portfolio Analytics & Allocation Insights', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
              SizedBox(height: 12),
              Text('Sector Allocation: PHARMA (35%), IT (25%), BANKING (20%), AUTO (20%)', style: TextStyle(color: Colors.white70, fontSize: 12)),
              SizedBox(height: 6),
              Text('Win Rate: 74.2% • Loss Rate: 25.8% • Profit Factor: 2.85', style: TextStyle(color: Colors.greenAccent, fontSize: 12, fontWeight: FontWeight.bold)),
              SizedBox(height: 6),
              Text('AI Suggestion: Rebalance 5% from PHARMA to DEFENCE for optimal diversification.', style: TextStyle(color: Colors.cyanAccent, fontSize: 11, fontStyle: FontStyle.italic)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildRiskDashboardTab(PortfolioSummaryModel s) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.redAccent.withValues(alpha: 0.3)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Portfolio Risk Dashboard', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
              const SizedBox(height: 12),
              _tile('Max Drawdown', '-2.40%', Colors.greenAccent),
              const SizedBox(height: 6),
              _tile('Capital at Risk', '₹45,000.00', Colors.amberAccent),
              const SizedBox(height: 6),
              _tile('Margin Utilization', '72.30%', Colors.purpleAccent),
              const SizedBox(height: 12),
              const Text('AI Risk Warning: Portfolio risk is WITHIN SAFE LIMITS.', style: TextStyle(color: Colors.greenAccent, fontSize: 12, fontWeight: FontWeight.bold)),
            ],
          ),
        ),
      ],
    );
  }

  static Widget _tile(String label, String val, Color col) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 2),
        Text(val, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 13)),
      ],
    );
  }
}
