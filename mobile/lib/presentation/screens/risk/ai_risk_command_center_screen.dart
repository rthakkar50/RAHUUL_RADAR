import 'package:flutter/material.dart';
import '../../../data/repositories/risk_command_center_repository.dart';

class AiRiskCommandCenterScreen extends StatefulWidget {
  const AiRiskCommandCenterScreen({super.key});

  @override
  State<AiRiskCommandCenterScreen> createState() =>
      _AiRiskCommandCenterScreenState();
}

class _AiRiskCommandCenterScreenState extends State<AiRiskCommandCenterScreen>
    with SingleTickerProviderStateMixin {
  final RiskCommandCenterRepository _repo = RiskCommandCenterRepository();
  late TabController _tabController;

  bool _isLoading = true;
  String? _error;
  RiskCommandCenterResponseModel? _data;

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
      final res = await _repo.getRiskCommandData();
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
    final overview = _data?.overview ?? _repo.getRiskOverview();
    final heatmap = _data?.heatmap ?? [];
    final stressScenarios = _data?.stressScenarios ?? _repo.getStressScenarios();
    final hedging = _data?.hedgingSuggestions ?? _repo.getHedgingSuggestions();

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
                  colors: [Colors.redAccent, Colors.orangeAccent],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(
                Icons.shield_outlined,
                color: Colors.black,
                size: 18,
              ),
            ),
            const SizedBox(width: 8),
            const Text(
              'AI Risk Command Center',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
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
            Tab(text: 'Dashboard'),
            Tab(text: 'Heat Map'),
            Tab(text: 'Stress Test'),
            Tab(text: 'Hedging'),
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
                      Text('Error loading Risk Command data: $_error', style: const TextStyle(color: Colors.white70)),
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
                      _buildDashboardTab(overview),
                      heatmap.isEmpty
                          ? _buildEmptyStateWidget()
                          : _buildHeatmapTab(heatmap),
                      _buildStressTestTab(stressScenarios),
                      _buildHedgingTab(hedging),
                    ],
                  ),
                ),
    );
  }

  Widget _buildEmptyStateWidget() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [
          Icon(Icons.shield_outlined, color: Colors.white38, size: 64),
          SizedBox(height: 16),
          Text(
            'No Active Positions Available',
            style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 8),
          Text(
            'Execute trades to activate live risk monitoring and position heatmap.',
            style: TextStyle(color: Colors.white54, fontSize: 13),
          ),
        ],
      ),
    );
  }

  Widget _buildDashboardTab(RiskOverviewModel overview) {
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
                    'AI Risk Executive Verdict',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  Text(
                    overview.riskGrade,
                    style: const TextStyle(
                      color: Colors.greenAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _tile(
                    'Portfolio Risk',
                    '${overview.portfolioRiskPct}%',
                    Colors.greenAccent,
                  ),
                  _tile(
                    'Capital Utilization',
                    '${overview.capitalUtilizationPct}%',
                    Colors.cyanAccent,
                  ),
                  _tile(
                    'Margin Used',
                    '${overview.marginUtilizationPct}%',
                    Colors.amberAccent,
                  ),
                  _tile(
                    'Max Drawdown',
                    '${overview.maxDrawdownPct}%',
                    Colors.purpleAccent,
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        _buildAlertsCard(),
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

  Widget _buildAlertsCard() {
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
                Icons.warning_amber_rounded,
                color: Colors.amberAccent,
                size: 18,
              ),
              SizedBox(width: 8),
              Text(
                'Module 7 — AI Live Risk Monitor Alerts',
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
            '• ALL CLEAR: Zero circuit breaker or drawdown violations detected.\n'
            '• Sector Concentration: Pharma exposure at 35% (Monitor rebalancing recommendation).\n'
            '• Emergency Kill Switch: Standing ready. 0 ms execution threshold.\n'
            '• Cash Reserve: ₹2,76,405 available cash buffer active.',
            style: TextStyle(color: Colors.white70, fontSize: 12, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildHeatmapTab(List<PositionRiskHeatmapModel> heatmap) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: heatmap.length,
      itemBuilder: (ctx, i) {
        final item = heatmap[i];
        final isGreen = item.colorCode == 'GREEN';
        final col = isGreen ? Colors.greenAccent : Colors.amberAccent;

        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 10),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: col.withValues(alpha: 0.2),
              child: Icon(
                isGreen
                    ? Icons.check_circle_outline
                    : Icons.warning_amber_rounded,
                color: col,
                size: 18,
              ),
            ),
            title: Text(
              '${item.symbol} (${item.sector})',
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            subtitle: Text(
              'Exposure: ${item.exposurePct}% of Portfolio',
              style: const TextStyle(color: Colors.grey, fontSize: 11),
            ),
            trailing: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: col.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                item.riskLevel,
                style: TextStyle(
                  color: col,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildStressTestTab(List<StressTestScenarioModel> scenarios) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: scenarios.length,
      itemBuilder: (ctx, i) {
        final st = scenarios[i];
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
                      st.scenarioName,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 6,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.greenAccent.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        'Survival: ${st.portfolioSurvivalPct}%',
                        style: const TextStyle(
                          color: Colors.greenAccent,
                          fontSize: 9,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  'Estimated Impact Loss: -₹${st.estimatedLossAmount.toStringAsFixed(2)}',
                  style: const TextStyle(
                    color: Colors.orangeAccent,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Expected Recovery Duration: ${st.recoveryTimeDays}',
                  style: const TextStyle(
                    color: Colors.cyanAccent,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildHedgingTab(List<String> hedging) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: hedging.length,
      itemBuilder: (ctx, i) {
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 10),
          child: ListTile(
            leading: const Icon(Icons.security, color: Colors.cyanAccent),
            title: Text(
              hedging[i],
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
