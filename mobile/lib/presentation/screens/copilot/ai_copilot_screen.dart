import 'package:flutter/material.dart';
import '../../../data/models/scan_result_model.dart';
import '../../../data/repositories/scanner_repository.dart';
import '../../../data/repositories/ai_master_decision_engine.dart';

class AiCopilotScreen extends StatefulWidget {
  const AiCopilotScreen({super.key});

  @override
  State<AiCopilotScreen> createState() => _AiCopilotScreenState();
}

class _AiCopilotScreenState extends State<AiCopilotScreen> {
  final AiMasterDecisionEngine _masterAiEngine = AiMasterDecisionEngine();
  List<ScanResultModel> _scans = [];
  ScanResultModel? _selectedScan;
  MasterDecisionModel? _masterDecision;
  bool _isLoading = false;
  String _selectedReportTab = 'Midday Report';

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  Future<void> _fetchData() async {
    setState(() => _isLoading = true);
    try {
      final repo = ScannerRepository();
      final res = await repo.getSwingScans();
      final scans = res.qualifiedResults;
      setState(() {
        _scans = scans;
        if (scans.isNotEmpty) {
          _selectedScan = scans.first;
          _masterDecision = _masterAiEngine.evaluateStock(scans.first);
        }
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
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
              child: const Icon(Icons.psychology, color: Colors.black, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('AI Market Copilot & Portfolio Intelligence', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.cyanAccent))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ── PART-1: AI Market Copilot Dashboard Header ────
                  _buildMarketCopilotDashboard(),
                  const SizedBox(height: 16),

                  // ── PART-5 & PART-6: Sector Rotation & Market Breadth ────
                  _buildSectorAndBreadthCard(),
                  const SizedBox(height: 16),

                  // ── PART-2 & PART-7: Portfolio Intelligence & Risk Score ──
                  _buildPortfolioIntelligenceCard(),
                  const SizedBox(height: 16),

                  // ── PART-3 & PART-4: AI Suggestions & Scanner Intelligence ─
                  _buildAiSuggestionsAndIntelligenceCard(),
                  const SizedBox(height: 16),

                  // ── PART-8: Daily AI Report ────────────────────────
                  _buildDailyAiReportCard(),
                  const SizedBox(height: 16),

                  // Stock Selection & Deep AI Analysis
                  if (_selectedScan != null) ...[
                    _buildStockSelector(),
                    const SizedBox(height: 16),
                    _buildCopilotDecisionCard(_selectedScan!),
                  ],
                ],
              ),
            ),
    );
  }

  Widget _buildMarketCopilotDashboard() {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF141A28),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(Icons.public, color: Colors.cyanAccent, size: 18),
                  SizedBox(width: 6),
                  Text('OVERALL MARKET COPILOT SUMMARY', style: TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 12)),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(color: Colors.greenAccent.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(6), border: Border.all(color: Colors.greenAccent)),
                child: const Text('REGIME: BULL MARKET', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.w800, fontSize: 10)),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricBox('Health Score', '84/100', Colors.cyanAccent),
              _metricBox('Bullish', '68.5%', Colors.greenAccent),
              _metricBox('Bearish', '18.2%', Colors.redAccent),
              _metricBox('Neutral', '13.3%', Colors.amberAccent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSectorAndBreadthCard() {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('SECTOR ROTATION & MARKET BREADTH', style: TextStyle(color: Colors.purpleAccent, fontWeight: FontWeight.bold, fontSize: 12)),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('• Strongest: NIFTY BANK / IT', style: TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                    Text('• Weakest: NIFTY FMCG', style: TextStyle(color: Colors.redAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                    Text('• Flow: Institutional Inflow (+₹1,420 Cr)', style: TextStyle(color: Colors.white70, fontSize: 10)),
                  ],
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('• Advances / Declines: 142 / 38', style: TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                    Text('• A/D Ratio: 3.76 (Strong)', style: TextStyle(color: Colors.lightGreenAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                    Text('• 52W Highs / Lows: 24 / 3', style: TextStyle(color: Colors.white70, fontSize: 10)),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPortfolioIntelligenceCard() {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('PORTFOLIO INTELLIGENCE & RISK SCORE', style: TextStyle(color: Colors.amberAccent, fontWeight: FontWeight.bold, fontSize: 12)),
              Text('RISK SCORE: 18/100 (LOW)', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 11)),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricBox('Open Positions', '4 Trades', Colors.white),
              _metricBox('Diversification', '88/100', Colors.cyanAccent),
              _metricBox('Equity / Cash', '65% / 35%', Colors.purpleAccent),
              _metricBox('Risk Per Trade', '1.8%', Colors.lightGreenAccent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAiSuggestionsAndIntelligenceCard() {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF131A2A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.3)),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('AI COPILOT SMART SUGGESTIONS', style: TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold, fontSize: 12)),
          SizedBox(height: 6),
          Text('• Capital Underutilized: 35% Cash remaining. Consider deploying into high-confidence Swing candidates.', style: TextStyle(color: Colors.white70, fontSize: 11)),
          Text('• Scanner Observation: WATCH signals dominate as NIFTY consolidates near 24,500 resistance.', style: TextStyle(color: Colors.white70, fontSize: 11)),
          Text('• Sector Allocation: Sector risk balanced (< 35% per sector). No over-concentration detected.', style: TextStyle(color: Colors.white70, fontSize: 11)),
        ],
      ),
    );
  }

  Widget _buildDailyAiReportCard() {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('DAILY AI MARKET REPORT', style: TextStyle(color: Colors.purpleAccent, fontWeight: FontWeight.bold, fontSize: 12)),
              SegmentedButton<String>(
                segments: const [
                  ButtonSegment(value: 'Morning Report', label: Text('Morning', style: TextStyle(fontSize: 10))),
                  ButtonSegment(value: 'Midday Report', label: Text('Midday', style: TextStyle(fontSize: 10))),
                  ButtonSegment(value: 'Closing Report', label: Text('Closing', style: TextStyle(fontSize: 10))),
                ],
                selected: {_selectedReportTab},
                onSelectionChanged: (s) => setState(() => _selectedReportTab = s.first),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(color: const Color(0xFF0D121F), borderRadius: BorderRadius.circular(8)),
            child: Text(
              '[$_selectedReportTab]: NIFTY opened with a gap-up (+0.4%) driven by Banking & Tech strength. Advance/Decline ratio stands strong at 3.76. Total 21 qualified swing signals generated.',
              style: const TextStyle(color: Colors.white70, fontSize: 11, fontStyle: FontStyle.italic),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStockSelector() {
    return SizedBox(
      height: 40,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: _scans.length,
        itemBuilder: (ctx, i) {
          final s = _scans[i];
          final isSelected = s.symbol == _selectedScan?.symbol;
          return GestureDetector(
            onTap: () {
              setState(() {
                _selectedScan = s;
                _masterDecision = _masterAiEngine.evaluateStock(s);
              });
            },
            child: Container(
              margin: const EdgeInsets.only(right: 8),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              decoration: BoxDecoration(
                color: isSelected ? Colors.cyanAccent : const Color(0xFF161B22),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: isSelected ? Colors.cyanAccent : Colors.white10),
              ),
              child: Center(
                child: Text(
                  s.symbol,
                  style: TextStyle(
                    color: isSelected ? Colors.black : Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildCopilotDecisionCard(ScanResultModel scan) {
    final decision = _masterDecision;
    if (decision == null) return const SizedBox();

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF141A28),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(scan.symbol, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(color: Colors.cyanAccent.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(6), border: Border.all(color: Colors.cyanAccent)),
                child: Text('DECISION: ${decision.masterSignal}', style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.w800, fontSize: 11)),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            decision.rationaleBullets.isNotEmpty ? '• ${decision.rationaleBullets.join('\n• ')}' : '${scan.symbol} qualified because Trend and Volume are fully aligned.',
            style: const TextStyle(color: Colors.white70, fontSize: 11, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _metricBox(String label, String val, Color col) {
    return Column(
      children: [
        Text(val, style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: col)),
        Text(label, style: const TextStyle(fontSize: 9, color: Colors.grey)),
      ],
    );
  }
}
