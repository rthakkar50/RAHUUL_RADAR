import 'package:flutter/material.dart';
import '../../../data/repositories/quant_repository.dart';

class QuantLabScreen extends StatefulWidget {
  const QuantLabScreen({super.key});

  @override
  State<QuantLabScreen> createState() => _QuantLabScreenState();
}

class _QuantLabScreenState extends State<QuantLabScreen> {
  final QuantRepository _repository = QuantRepository();
  bool _isLoading = true;
  String? _error;
  QuantResponseModel? _data;

  @override
  void initState() {
    super.initState();
    _fetchQuantData();
  }

  Future<void> _fetchQuantData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final data = await _repository.getQuantBacktestData();
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

  void _showReplayModal(String tradeTitle, String analysis) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: const Color(0xFF161B22),
        title: Text(tradeTitle, style: const TextStyle(color: Colors.cyanAccent, fontSize: 14, fontWeight: FontWeight.bold)),
        content: Text(analysis, style: const TextStyle(color: Colors.white70, fontSize: 12, height: 1.4)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close', style: TextStyle(color: Colors.purpleAccent)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final metrics = _data?.metrics ?? _repository.getFallbackData().metrics;
    final buckets = _data?.confidenceBuckets ?? [];
    final rankings = _data?.scannerRankings ?? [];
    final recs = _data?.aiRecommendations ?? _repository.getFallbackData().aiRecommendations;
    final replays = _data?.replays ?? [];

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
                  colors: [Colors.indigoAccent, Colors.purpleAccent],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.science_outlined, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('AI Learning & Self-Improvement Engine', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.cyanAccent),
            onPressed: _isLoading ? null : _fetchQuantData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.indigoAccent))
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.error_outline, color: Colors.redAccent, size: 48),
                      const SizedBox(height: 12),
                      Text('Error loading Quant Lab: $_error', style: const TextStyle(color: Colors.white70)),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _fetchQuantData,
                        style: ElevatedButton.styleFrom(backgroundColor: Colors.cyanAccent),
                        child: const Text('Retry', style: TextStyle(color: Colors.black)),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _fetchQuantData,
                  color: Colors.indigoAccent,
                  backgroundColor: const Color(0xFF161B22),
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Quant Overview Grid
                        _buildMetricsGrid(metrics),
                        const SizedBox(height: 16),

                        // Confidence Calibration Buckets
                        if (buckets.isNotEmpty) ...[
                          _buildConfidenceCalibrationCard(buckets),
                          const SizedBox(height: 16),
                        ],

                        // Scanner Rankings
                        if (rankings.isNotEmpty) ...[
                          _buildRankingsCard(rankings),
                          const SizedBox(height: 16),
                        ],

                        // AI Self-Improvement Recommendations
                        _buildAiRecommendationsCard(recs),
                        const SizedBox(height: 16),

                        // Replay Learning
                        _buildReplayLearningCard(replays),
                      ],
                    ),
                  ),
                ),
    );
  }

  Widget _buildMetricsGrid(QuantMetricsModel metrics) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF141A28),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.indigoAccent.withValues(alpha: 0.3)),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricTile('WIN RATE', '${metrics.winRate.toStringAsFixed(1)}%', Colors.greenAccent),
              _metricTile('PROFIT FACTOR', metrics.profitFactor.toStringAsFixed(2), Colors.cyanAccent),
              _metricTile('SHARPE RATIO', metrics.sharpeRatio.toStringAsFixed(2), Colors.lightGreenAccent),
              _metricTile('SORTINO RATIO', metrics.sortinoRatio.toStringAsFixed(2), Colors.purpleAccent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildConfidenceCalibrationCard(List<ConfidenceBucketModel> buckets) {
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
          const Text('CONFIDENCE BUCKET CALIBRATION', style: TextStyle(color: Colors.purpleAccent, fontWeight: FontWeight.bold, fontSize: 12)),
          const SizedBox(height: 8),
          ...buckets.map((b) => _bucketRow(b.bucket, '${b.winRatePct.toStringAsFixed(1)}% Win Rate', b.ratio, Colors.cyanAccent)),
        ],
      ),
    );
  }

  Widget _buildRankingsCard(List<ScannerRankingModel> rankings) {
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
          const Text('SCANNER PERFORMANCE RANKING', style: TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 12)),
          const SizedBox(height: 8),
          ...rankings.map((r) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Text('${r.rank}. ${r.scanner} — Win Rate: ${r.winRatePct.toStringAsFixed(1)}% | Avg RR: ${r.avgRr}', style: const TextStyle(color: Colors.white70, fontSize: 11)),
              )),
        ],
      ),
    );
  }

  Widget _buildAiRecommendationsCard(List<String> recs) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF131A2A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.indigoAccent.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('AI SELF-IMPROVEMENT RECOMMENDATIONS', style: TextStyle(color: Colors.indigoAccent, fontWeight: FontWeight.bold, fontSize: 12)),
          const SizedBox(height: 6),
          ...recs.map((r) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Text('• $r', style: const TextStyle(color: Colors.white70, fontSize: 11)),
              )),
        ],
      ),
    );
  }

  Widget _buildReplayLearningCard(List<TradeReplayItemModel> replays) {
    final winReplay = replays.firstWhere((r) => r.type == 'WIN', orElse: () => const TradeReplayItemModel(type: 'WIN', title: 'Replay Win', analysis: 'No win trade replay recorded.'));
    final lossReplay = replays.firstWhere((r) => r.type == 'LOSS', orElse: () => const TradeReplayItemModel(type: 'LOSS', title: 'Replay Loss', analysis: 'No loss trade replay recorded.'));

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
          const Text('TRADE REPLAY LEARNING ENGINE', style: TextStyle(color: Colors.amberAccent, fontWeight: FontWeight.bold, fontSize: 12)),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _showReplayModal(winReplay.title, winReplay.analysis),
                  icon: const Icon(Icons.play_circle_fill, size: 14, color: Colors.greenAccent),
                  label: const Text('Replay Win', style: TextStyle(fontSize: 11)),
                  style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF232D48)),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _showReplayModal(lossReplay.title, lossReplay.analysis),
                  icon: const Icon(Icons.replay, size: 14, color: Colors.redAccent),
                  label: const Text('Replay Loss', style: TextStyle(fontSize: 11)),
                  style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF232D48)),
                ),
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
        Text(val, style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: col)),
        Text(label, style: const TextStyle(fontSize: 8, color: Colors.grey)),
      ],
    );
  }

  Widget _bucketRow(String label, String valStr, double ratio, Color col) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          SizedBox(width: 140, child: Text(label, style: const TextStyle(color: Colors.white70, fontSize: 10))),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(value: ratio, minHeight: 6, backgroundColor: Colors.white10, valueColor: AlwaysStoppedAnimation<Color>(col)),
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(width: 75, child: Text(valStr, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 10))),
        ],
      ),
    );
  }
}
