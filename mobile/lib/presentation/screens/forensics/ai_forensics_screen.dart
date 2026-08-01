import 'package:flutter/material.dart';
import '../../../data/repositories/trade_forensics_repository.dart';

class AiForensicsScreen extends StatefulWidget {
  const AiForensicsScreen({super.key});

  @override
  State<AiForensicsScreen> createState() => _AiForensicsScreenState();
}

class _AiForensicsScreenState extends State<AiForensicsScreen>
    with SingleTickerProviderStateMixin {
  final TradeForensicsRepository _repo = TradeForensicsRepository();
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
    final records = _repo.getForensicHistory();
    final timeline = _repo.getEvolutionTimeline();

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
                  colors: [Colors.purpleAccent, Colors.cyanAccent],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(
                Icons.psychology_alt,
                color: Colors.black,
                size: 18,
              ),
            ),
            const SizedBox(width: 8),
            const Text(
              'AI Forensics & Learning Hub',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
          ],
        ),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Learning'),
            Tab(text: 'Forensics'),
            Tab(text: 'Replay'),
            Tab(text: 'Evolution'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildLearningDashboardTab(),
          _buildForensicsListTab(records),
          _buildTradeReplayTab(records.first),
          _buildEvolutionTimelineTab(timeline),
        ],
      ),
    );
  }

  Widget _buildLearningDashboardTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildAccuracyCard(),
        const SizedBox(height: 16),
        _buildSelfImprovementCard(),
        const SizedBox(height: 16),
        _buildFailureAnalysisCard(),
      ],
    );
  }

  Widget _buildAccuracyCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.purpleAccent.withValues(alpha: 0.4)),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'AI Calibration Accuracy',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              Text(
                '88.4% (HIGHLY ACCURATE)',
                style: TextStyle(
                  color: Colors.greenAccent,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
            ],
          ),
          SizedBox(height: 12),
          LinearProgressIndicator(
            value: 0.884,
            color: Colors.greenAccent,
            backgroundColor: Colors.white10,
            minHeight: 8,
          ),
          SizedBox(height: 14),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricTile('Calibration Error', '2.1%', Colors.greenAccent),
              _metricTile(
                'Prediction Drift',
                '0.04 (STABLE)',
                Colors.cyanAccent,
              ),
              _metricTile(
                'Best Strategy',
                'Breakout Momentum',
                Colors.purpleAccent,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metricTile(String label, String val, Color col) {
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

  Widget _buildSelfImprovementCard() {
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
              Icon(Icons.auto_graph, color: Colors.cyanAccent, size: 18),
              SizedBox(width: 8),
              Text(
                'Module 6 — AI Self-Improvement Recommendations',
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
            '• Auto-adjusted confidence threshold for Sideways Market Regimes (-5.0%).\n'
            '• Increased weight on Volume Confirmation (from 15% to 20% total weight).\n'
            '• Implemented dynamic position reduction during India VIX > 16.5.\n'
            '• Sector Filter: Overweight Pharma & IT (+12.5% win rate correlation).',
            style: TextStyle(color: Colors.white70, fontSize: 12, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildFailureAnalysisCard() {
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
            'Module 3 — Root Cause Failure Breakdown',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 13,
            ),
          ),
          SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'High VIX Whipsaw: 42%',
                style: TextStyle(
                  color: Colors.orangeAccent,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                'False Breakout: 28%',
                style: TextStyle(
                  color: Colors.redAccent,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                'Sector Drag: 18%',
                style: TextStyle(
                  color: Colors.amberAccent,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildForensicsListTab(List<TradeForensicRecordModel> records) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: records.length,
      itemBuilder: (ctx, i) {
        final rec = records[i];
        final isWin = rec.outcome == 'WIN';
        final col = isWin ? Colors.greenAccent : Colors.redAccent;

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
                      '${rec.symbol} (${rec.signal}) — ${rec.tradeId}',
                      style: TextStyle(
                        color: col,
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
                        color: col.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        rec.outcome,
                        style: TextStyle(
                          color: col,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Strategy: ${rec.strategy} • Sector: ${rec.sector} • Regime: ${rec.marketRegime}',
                  style: const TextStyle(color: Colors.white70, fontSize: 11),
                ),
                const SizedBox(height: 4),
                Text(
                  'PnL: ₹${rec.pnl.toStringAsFixed(2)} (${rec.pnlPct}%) • R: ${rec.rMultiple} • AI Score: ${rec.masterAiScore}',
                  style: const TextStyle(color: Colors.grey, fontSize: 11),
                ),
                const Divider(color: Colors.white10),
                Text(
                  'Root Cause: ${rec.failureRootCause}',
                  style: const TextStyle(
                    color: Colors.amberAccent,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'Lesson: ${rec.lessonLearned}',
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

  Widget _buildTradeReplayTab(TradeForensicRecordModel rec) {
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
              Text(
                'Module 7 — Historical Trade Replay Simulator: ${rec.tradeId}',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 12),
              _replayRow(
                'Symbol & Signal',
                '${rec.symbol} ${rec.signal}',
                Colors.greenAccent,
              ),
              _replayRow(
                'Entry Price',
                '₹${rec.entryPrice.toStringAsFixed(2)}',
                Colors.white,
              ),
              _replayRow(
                'Exit Target Price',
                '₹${rec.exitPrice.toStringAsFixed(2)}',
                Colors.cyanAccent,
              ),
              _replayRow(
                'PnL Achieved',
                '+₹${rec.pnl.toStringAsFixed(2)} (${rec.pnlPct}%)',
                Colors.greenAccent,
              ),
              _replayRow(
                'Master AI Score at Entry',
                '${rec.masterAiScore} / 100',
                Colors.purpleAccent,
              ),
              _replayRow('Market Regime', rec.marketRegime, Colors.amberAccent),
              const Divider(color: Colors.white10),
              const Text(
                'AI Post-Trade Retrospective Lesson:',
                style: TextStyle(color: Colors.grey, fontSize: 11),
              ),
              const SizedBox(height: 4),
              Text(
                rec.lessonLearned,
                style: const TextStyle(
                  color: Colors.cyanAccent,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _replayRow(String label, String val, Color col) {
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

  Widget _buildEvolutionTimelineTab(List<AiEvolutionMetricsModel> timeline) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: timeline.length,
      itemBuilder: (ctx, i) {
        final ev = timeline[i];
        final isLatest = i == timeline.length - 1;

        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            title: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  ev.version,
                  style: TextStyle(
                    color: isLatest ? Colors.cyanAccent : Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                if (isLatest)
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 6,
                      vertical: 2,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.cyanAccent.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: const Text(
                      'ACTIVE',
                      style: TextStyle(
                        color: Colors.cyanAccent,
                        fontSize: 9,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
              ],
            ),
            subtitle: Text(
              'Accuracy: ${ev.accuracyPct}% • Profit Factor: ${ev.profitFactor} • Max DD: ${ev.maxDrawdownPct}% • Latency: ${ev.avgLatencyMs}ms',
              style: const TextStyle(color: Colors.grey, fontSize: 11),
            ),
          ),
        );
      },
    );
  }
}
