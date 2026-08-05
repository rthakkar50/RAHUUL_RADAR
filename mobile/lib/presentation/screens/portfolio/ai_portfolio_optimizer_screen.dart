import 'package:flutter/material.dart';
import '../../../data/repositories/portfolio_optimizer_repository.dart';

class AiPortfolioOptimizerScreen extends StatefulWidget {
  const AiPortfolioOptimizerScreen({super.key});

  @override
  State<AiPortfolioOptimizerScreen> createState() =>
      _AiPortfolioOptimizerScreenState();
}

class _AiPortfolioOptimizerScreenState extends State<AiPortfolioOptimizerScreen>
    with SingleTickerProviderStateMixin {
  final PortfolioOptimizerRepository _repo = PortfolioOptimizerRepository();
  late TabController _tabController;

  bool _isLoading = true;
  String? _error;
  PortfolioOptimizerResponseModel? _data;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _fetchData();
  }

  Future<void> _fetchData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final res = await _repo.getOptimizerData();
      if (mounted) {
        setState(() {
          _data = res;
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
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final health = _data?.health ?? _repo.getPortfolioHealth();
    final alloc = _data?.allocation ?? _repo.getCapitalAllocation();
    final stressTests = _data?.stressTest ?? _repo.getStressTestSimulations();
    final rebalancing = _data?.suggestions ?? _repo.getRebalancingSuggestions();

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
                  colors: [Colors.amberAccent, Colors.greenAccent],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(
                Icons.pie_chart_outline,
                color: Colors.black,
                size: 18,
              ),
            ),
            const SizedBox(width: 8),
            const Text(
              'AI Portfolio Optimizer & Allocator',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.cyanAccent),
            onPressed: _fetchData,
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Health'),
            Tab(text: 'Allocation'),
            Tab(text: 'Stress Test'),
            Tab(text: 'Rebalance'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.cyanAccent))
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.error_outline, color: Colors.redAccent, size: 48),
                      const SizedBox(height: 12),
                      Text('Error loading Optimizer data: $_error', style: const TextStyle(color: Colors.white70)),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _fetchData,
                        style: ElevatedButton.styleFrom(backgroundColor: Colors.cyanAccent),
                        child: const Text('Retry', style: TextStyle(color: Colors.black)),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _fetchData,
                  color: Colors.cyanAccent,
                  backgroundColor: const Color(0xFF161B22),
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _buildHealthTab(health),
                      _buildAllocationTab(alloc),
                      _buildStressTestTab(stressTests),
                      _buildRebalanceTab(rebalancing),
                    ],
                  ),
                ),
    );
  }

  Widget _buildHealthTab(PortfolioHealthModel health) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: Colors.greenAccent.withValues(alpha: 0.4),
            ),
          ),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'AI Portfolio Health Score',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                    ),
                  ),
                  Text(
                    '${health.overallScore} / 100',
                    style: const TextStyle(
                      color: Colors.greenAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              LinearProgressIndicator(
                value: health.overallScore / 100.0,
                color: Colors.greenAccent,
                backgroundColor: Colors.white10,
                minHeight: 8,
              ),
              const SizedBox(height: 14),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _tile(
                    'Diversification',
                    '${health.diversificationScore}',
                    Colors.cyanAccent,
                  ),
                  _tile(
                    'Sector Balance',
                    '${health.sectorBalanceScore}',
                    Colors.amberAccent,
                  ),
                  _tile(
                    'Cash Position',
                    '${health.cashPositionScore}',
                    Colors.greenAccent,
                  ),
                  _tile(
                    'Risk Usage',
                    '${health.riskUsageScore}',
                    Colors.purpleAccent,
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        _buildAdvisorCard(),
      ],
    );
  }

  Widget _tile(String label, String val, Color col) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 3),
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

  Widget _buildAdvisorCard() {
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
              Icon(
                Icons.lightbulb_outline,
                color: Colors.amberAccent,
                size: 18,
              ),
              SizedBox(width: 8),
              Text(
                'Module 8 — AI Investment Advisor Summary',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
            ],
          ),
          SizedBox(height: 10),
          Text(
            '• Overall portfolio risk is LOW (0.69% of capital exposed).\n'
            '• Cash buffer of 27.6% (₹2.76L) is optimal for high volatility protection.\n'
            '• Pharma sector concentration (35%) requires minor rebalancing.\n'
            '• Expected Annualized Return (CAGR): 34.2% with 2.45 Profit Factor.',
            style: TextStyle(color: Colors.white70, fontSize: 12, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildAllocationTab(CapitalAllocationModel alloc) {
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
              const Text(
                'Module 2 — Capital & Asset Allocation Engine',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 14),
              _allocRow(
                'Available Cash Buffer',
                '${alloc.cashPct}%',
                Colors.greenAccent,
              ),
              _allocRow(
                'Equity Swing Holdings',
                '${alloc.equityPct}%',
                Colors.blueAccent,
              ),
              _allocRow(
                'F&O Options / Futures',
                '${alloc.fnoPct}%',
                Colors.purpleAccent,
              ),
              const Divider(color: Colors.white10),
              _allocRow(
                'Swing Trading Strategy',
                '${alloc.swingPct}%',
                Colors.cyanAccent,
              ),
              _allocRow(
                'Intraday Strategy',
                '${alloc.intradayPct}%',
                Colors.amberAccent,
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _allocRow(String label, String val, Color col) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(color: Colors.white70, fontSize: 12),
          ),
          Text(
            val,
            style: TextStyle(
              color: col,
              fontWeight: FontWeight.bold,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStressTestTab(List<StressTestResultModel> stressTests) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: stressTests.length,
      itemBuilder: (ctx, i) {
        final st = stressTests[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(14.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Simulated ${st.crashPct}% Market Crash',
                      style: const TextStyle(
                        color: Colors.redAccent,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.greenAccent.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        st.riskGrade,
                        style: const TextStyle(
                          color: Colors.greenAccent,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Estimated Portfolio Loss: -₹${st.estimatedLoss.toStringAsFixed(2)}',
                  style: const TextStyle(
                    color: Colors.orangeAccent,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Projected Equity After Crash: ₹${st.portfolioEquityAfterCrash.toStringAsFixed(2)}',
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                ),
                Text(
                  'Estimated Recovery Time: ${st.estimatedRecoveryTime}',
                  style: const TextStyle(
                    color: Colors.cyanAccent,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildRebalanceTab(List<String> rebalancing) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: rebalancing.length,
      itemBuilder: (ctx, i) {
        final sug = rebalancing[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 10),
          child: ListTile(
            leading: const Icon(Icons.sync_alt, color: Colors.amberAccent),
            title: Text(
              sug,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        );
      },
    );
  }
}
