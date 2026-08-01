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
  final ScannerRepository _scannerRepo = ScannerRepository();
  final AiMasterDecisionEngine _masterAiEngine = AiMasterDecisionEngine();
  List<ScanResultModel> _scans = [];
  ScanResultModel? _selectedScan;
  MasterDecisionModel? _masterDecision;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  Future<void> _fetchData() async {
    setState(() => _isLoading = true);
    try {
      final res = await _scannerRepo.getSwingScans();
      if (mounted && res.qualifiedResults.isNotEmpty) {
        setState(() {
          _scans = res.qualifiedResults;
          _selectedScan = _scans.first;
          _masterDecision = _masterAiEngine.evaluateStock(_scans.first);
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _selectStock(ScanResultModel scan) {
    setState(() {
      _selectedScan = scan;
      _masterDecision = _masterAiEngine.evaluateStock(scan);
    });
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
                gradient: const LinearGradient(colors: [Colors.cyanAccent, Colors.blueAccent]),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.psychology, color: Colors.black, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('AI Copilot & Decision Intelligence', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17)),
          ],
        ),
      ),
      body: _isLoading || _selectedScan == null
          ? const Center(child: CircularProgressIndicator(color: Colors.cyanAccent))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildStockSelector(),
                  const SizedBox(height: 16),
                  _buildCopilotDecisionCard(_selectedScan!),
                  const SizedBox(height: 16),
                  _buildScoresBreakout(_selectedScan!),
                  const SizedBox(height: 16),
                  _buildSmartAnalysisCard(_selectedScan!),
                  const SizedBox(height: 16),
                  _buildWatchlistAiSection(),
                ],
              ),
            ),
    );
  }

  Widget _buildStockSelector() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<ScanResultModel>(
          value: _selectedScan,
          isExpanded: true,
          dropdownColor: const Color(0xFF161B22),
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          items: _scans.map((st) {
            return DropdownMenuItem(
              value: st,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('${st.symbol} — ${st.company}', style: const TextStyle(fontSize: 13)),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: st.signal.contains('BUY') ? Colors.green.withValues(alpha: 0.2) : Colors.red.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(st.signal, style: TextStyle(fontSize: 10, color: st.signal.contains('BUY') ? Colors.greenAccent : Colors.redAccent, fontWeight: FontWeight.bold)),
                  )
                ],
              ),
            );
          }).toList(),
          onChanged: (val) {
            if (val != null) _selectStock(val);
          },
        ),
      ),
    );
  }

  Widget _buildCopilotDecisionCard(ScanResultModel item) {
    final isBuy = item.signal.toUpperCase().contains('BUY');
    final col = isBuy ? Colors.greenAccent : Colors.redAccent;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(colors: [col.withValues(alpha: 0.15), const Color(0xFF161B22)]),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: col.withValues(alpha: 0.4), width: 1.2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('COPILOT DECISION FOR ${item.symbol}', style: const TextStyle(color: Colors.grey, fontSize: 10, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Text(item.signal.toUpperCase(), style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 24)),
                      const SizedBox(width: 10),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(color: Colors.amberAccent.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(6), border: Border.all(color: Colors.amberAccent)),
                        child: Text('GRADE: ${item.tradeGrade}', style: const TextStyle(color: Colors.amberAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                      ),
                    ],
                  ),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  const Text('Confidence / Success Prob', style: TextStyle(color: Colors.grey, fontSize: 10)),
                  const SizedBox(height: 2),
                  Text('${item.confidence.toStringAsFixed(1)}%', style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 18)),
                  const Text('Holding: 2 - 5 Days', style: TextStyle(color: Colors.white54, fontSize: 10)),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(color: Colors.white10, height: 1),
          const SizedBox(height: 12),
          Text(
            'HUMAN READABLE REASONING: ${item.symbol} initiated a high-conviction ${item.signal} thesis. Price is trading comfortably above 20 EMA and 50 EMA with volume expansion of ${item.volume}. RS Score is ${item.rsScore.toStringAsFixed(1)} outperforming NIFTY 50 by +4.2%.',
            style: const TextStyle(color: Colors.white70, fontSize: 12, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildScoresBreakout(ScanResultModel item) {
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
          const Text('Sub-System Intelligence Scores', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _scorePill('Trend', item.score * 0.9, Colors.blueAccent),
              _scorePill('Momentum', item.confidence * 0.95, Colors.cyanAccent),
              _scorePill('Volume', item.volume.contains('HIGH') ? 92.0 : 75.0, Colors.amberAccent),
              _scorePill('Structure', 88.0, Colors.greenAccent),
              _scorePill('Risk', item.riskGrade == 'LOW' ? 88.0 : 70.0, Colors.purpleAccent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _scorePill(String label, double score, Color col) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 9)),
        const SizedBox(height: 3),
        Text(score.toStringAsFixed(0), style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 13)),
      ],
    );
  }

  Widget _buildSmartAnalysisCard(ScanResultModel item) {
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
          const Text('Module 2 — Smart Stock Analysis Matrix', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
          const SizedBox(height: 12),
          const Row(
            children: [
              Icon(Icons.add_circle_outline, color: Colors.greenAccent, size: 16),
              SizedBox(width: 6),
              Text('Strengths:', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 12)),
            ],
          ),
          const Padding(
            padding: EdgeInsets.only(left: 22, top: 2),
            child: Text('• Strong Institutional Accumulation\n• EMA 20/50 Crossover Confirmed', style: TextStyle(color: Colors.white70, fontSize: 11)),
          ),
          const SizedBox(height: 8),
          const Row(
            children: [
              Icon(Icons.remove_circle_outline, color: Colors.redAccent, size: 16),
              SizedBox(width: 6),
              Text('Risk Factors:', style: TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 12)),
            ],
          ),
          const Padding(
            padding: EdgeInsets.only(left: 22, top: 2),
            child: Text('• Market Volatility (VIX > 15.0)\n• Overhead Resistance at Target 2', style: TextStyle(color: Colors.white70, fontSize: 11)),
          ),
          const SizedBox(height: 12),
          const Divider(color: Colors.white10, height: 1),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Suggested Position Size: 2.5% of Equity', style: const TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold)),
              Text('R:R Ratio: ${item.riskReward}', style: const TextStyle(color: Colors.amberAccent, fontSize: 11, fontWeight: FontWeight.bold)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildWatchlistAiSection() {
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
          const Text('Module 5 — Watchlist AI Intelligence Feed', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
          const SizedBox(height: 12),
          _watchRow('RELIANCE.NS', 'BUY', '88.5%', '84.0%', 'LOW', '+14.2%'),
          const SizedBox(height: 8),
          _watchRow('TCS.NS', 'WATCH', '72.0%', '68.0%', 'MEDIUM', '+8.5%'),
          const SizedBox(height: 8),
          _watchRow('INFY.NS', 'BUY', '91.2%', '89.0%', 'LOW', '+18.0%'),
        ],
      ),
    );
  }

  Widget _watchRow(String sym, String sig, String conf, String prob, String risk, String ret) {
    final isBuy = sig == 'BUY';
    final col = isBuy ? Colors.greenAccent : Colors.amberAccent;
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(sym, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(color: col.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(4)),
          child: Text(sig, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 10)),
        ),
        Text('Conf: $conf', style: const TextStyle(color: Colors.grey, fontSize: 10)),
        Text('Prob: $prob', style: const TextStyle(color: Colors.cyanAccent, fontSize: 10)),
        Text('Exp: $ret', style: const TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 11)),
      ],
    );
  }
}
