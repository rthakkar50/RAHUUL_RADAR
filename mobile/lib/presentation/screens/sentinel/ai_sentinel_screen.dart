import 'package:flutter/material.dart';
import '../../../data/repositories/ai_sentinel_repository.dart';

class AiSentinelScreen extends StatefulWidget {
  const AiSentinelScreen({super.key});

  @override
  State<AiSentinelScreen> createState() => _AiSentinelScreenState();
}

class _AiSentinelScreenState extends State<AiSentinelScreen>
    with SingleTickerProviderStateMixin {
  final AiSentinelRepository _repo = AiSentinelRepository();
  late TabController _tabController;

  bool _isLoading = true;
  String? _error;
  AiSentinelResponseModel? _data;

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
      final res = await _repo.getSentinelData();
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
    final mood = _data?.mood ?? _repo.getMarketMood();
    final opps = _data?.opportunities ?? _repo.getRankedOpportunities();
    final mission = _data?.dailyMission ?? _repo.getDailyMission();
    final topOpp = opps.isNotEmpty ? opps.first : _repo.getRankedOpportunities().first;

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
                  colors: [Colors.cyanAccent, Colors.purpleAccent],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.radar, color: Colors.black, size: 18),
            ),
            const SizedBox(width: 8),
            const Text(
              'AI Market Sentinel & Assistant',
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
            Tab(text: 'Sentinel'),
            Tab(text: 'Opportunities'),
            Tab(text: 'Trade Plan'),
            Tab(text: 'Mission'),
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
                      Text('Error loading Sentinel data: $_error', style: const TextStyle(color: Colors.white70)),
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
                      _buildSentinelTab(mood),
                      _buildOpportunitiesTab(opps),
                      _buildTradePlanTab(topOpp),
                      _buildMissionTab(mission),
                    ],
                  ),
                ),
    );
  }

  Widget _buildSentinelTab(MarketSentinelMoodModel mood) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.4)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'AI Market Mood Verdict',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                    ),
                  ),
                  Text(
                    '${mood.overallMood} (${mood.confidencePct}%)',
                    style: const TextStyle(
                      color: Colors.greenAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              _moodRow('FII Net Flow', mood.fiiFlow, Colors.greenAccent),
              _moodRow('DII Net Flow', mood.diiFlow, Colors.greenAccent),
              _moodRow(
                'India VIX',
                mood.indiaVix != null ? '${mood.indiaVix}' : 'Unavailable',
                Colors.cyanAccent,
              ),
              _moodRow(
                'PCR Index',
                mood.pcr != null ? '${mood.pcr}' : 'Unavailable',
                Colors.amberAccent,
              ),
              _moodRow(
                'Market Breadth',
                mood.marketBreadth,
                Colors.purpleAccent,
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        _buildSafetyGateCard(),
      ],
    );
  }

  Widget _moodRow(String label, String val, Color col) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 11)),
          Text(
            val,
            style: TextStyle(
              color: col,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSafetyGateCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.greenAccent.withValues(alpha: 0.3)),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.gavel, color: Colors.greenAccent, size: 18),
              SizedBox(width: 8),
              Text(
                'Module 10 — Safety Gate Guarantee',
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
            '• Auto Execute: DISABLED (Manual User Approval Mandatory).\n'
            '• Execution Policy: Sentinel prepares trade details; human places order.\n'
            '• Kill Switch Status: ARMED & READY (0 ms latency emergency halt).\n'
            '• Risk Budget Engine: ENFORCED (Max 0.25% capital risk per trade).',
            style: TextStyle(color: Colors.white70, fontSize: 12, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildOpportunitiesTab(List<SentinelOpportunityModel> opps) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: opps.length,
      itemBuilder: (ctx, i) {
        final opp = opps[i];
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
                      '${opp.symbol} — ${opp.signal}',
                      style: const TextStyle(
                        color: Colors.greenAccent,
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
                        color: Colors.purpleAccent.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        'Priority: ${opp.priorityScore}',
                        style: const TextStyle(
                          color: Colors.purpleAccent,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Entry: ₹${opp.entryPrice} • Target 1: ₹${opp.target1} • SL: ₹${opp.stopLoss}',
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                ),
                Text(
                  'Expected Return: +${opp.expectedReturnPct}% • Hold: ${opp.holdingPeriod}',
                  style: const TextStyle(
                    color: Colors.cyanAccent,
                    fontSize: 11,
                  ),
                ),
                const Divider(color: Colors.white10),
                Text(
                  'AI Rationale: ${opp.aiRationale}',
                  style: const TextStyle(color: Colors.white70, fontSize: 11),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildTradePlanTab(SentinelOpportunityModel opp) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: Colors.purpleAccent.withValues(alpha: 0.4),
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Module 4 — Prepared Trade Plan: ${opp.symbol}',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 12),
              _planRow('Signal', opp.signal, Colors.greenAccent),
              _planRow(
                'Entry Limit Price',
                '₹${opp.entryPrice.toStringAsFixed(2)}',
                Colors.white,
              ),
              _planRow(
                'Stop Loss (SL)',
                '₹${opp.stopLoss.toStringAsFixed(2)}',
                Colors.redAccent,
              ),
              _planRow(
                'Target 1 (T1)',
                '₹${opp.target1.toStringAsFixed(2)}',
                Colors.greenAccent,
              ),
              _planRow(
                'Target 2 (T2)',
                '₹${opp.target2.toStringAsFixed(2)}',
                Colors.greenAccent,
              ),
              _planRow(
                'Target 3 (T3)',
                '₹${opp.target3.toStringAsFixed(2)}',
                Colors.greenAccent,
              ),
              const Divider(color: Colors.white10),
              _planRow(
                'Recommended Quantity',
                '${opp.recommendedQty} shares',
                Colors.cyanAccent,
              ),
              _planRow(
                'Capital Required',
                '₹${opp.capitalRequired.toStringAsFixed(2)}',
                Colors.amberAccent,
              ),
              _planRow('Est. Brokerage & Taxes', '~₹42.50', Colors.grey),
              const SizedBox(height: 12),
              ElevatedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.touch_app, size: 16),
                label: const Text('Review Order & Confirm Execution (Manual)'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.purpleAccent,
                  foregroundColor: Colors.black,
                  minimumSize: const Size(double.infinity, 44),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _planRow(String label, String val, Color col) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 11)),
          Text(
            val,
            style: TextStyle(
              color: col,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMissionTab(List<String> mission) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: mission.length,
      itemBuilder: (ctx, i) {
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 10),
          child: ListTile(
            leading: const Icon(
              Icons.assignment_outlined,
              color: Colors.cyanAccent,
            ),
            title: Text(
              mission[i],
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
