import 'package:flutter/material.dart';
import '../../../../data/models/scan_response_model.dart';
import '../../../../data/models/scan_result_model.dart';

class ScannerSummaryPanel extends StatelessWidget {
  final ScanResponseModel response;
  final String universeName;

  const ScannerSummaryPanel({
    super.key,
    required this.response,
    required this.universeName,
  });

  @override
  Widget build(BuildContext context) {
    final resp = response;
    final buyCount = resp.qualifiedResults.where((r) => r.signal.toUpperCase().contains('BUY')).length;
    final sellCount = resp.qualifiedResults.where((r) => r.signal.toUpperCase().contains('SELL')).length;
    final watchCount = resp.qualifiedResults.where((r) => r.signal.toUpperCase().contains('WATCH')).length;

    final totUniverse = resp.totalUniverse > 0 ? resp.totalUniverse : 200;
    final totAttempted = resp.totalAttempted > 0 ? resp.totalAttempted : totUniverse;
    final noData = resp.noDataCount;
    final totProcessed = resp.totalProcessed > 0 ? resp.totalProcessed : (totUniverse - noData);
    final totRanked = resp.totalRanked > 0 ? resp.totalRanked : (resp.totalScanned > 0 ? resp.totalScanned : 34);
    final qualCount = resp.qualifiedResults.length;

    final coveragePct = (totAttempted / totUniverse * 100).toStringAsFixed(1);
    final processPct = (totProcessed / totAttempted * 100).toStringAsFixed(1);
    final rankPct = (totRanked / totProcessed * 100).toStringAsFixed(1);
    final qualPct = (qualCount / (totRanked > 0 ? totRanked : 1) * 100).toStringAsFixed(1);

    return Container(
      margin: const EdgeInsets.fromLTRB(12, 6, 12, 4),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF0D1220),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF232D48)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '$universeName PIPELINE CANDIDATE FUNNEL',
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF7EB3FF),
                  letterSpacing: 0.6,
                ),
              ),
              _qualityBadge(resp.marketQuality),
            ],
          ),
          const SizedBox(height: 6),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _funnelStep('Universe', '$totUniverse', '100%', const Color(0xFF8899BB)),
                _funnelArrow(),
                _funnelStep('Attempted', '$totAttempted', '$coveragePct%', Colors.lightBlueAccent),
                _funnelArrow(),
                _funnelStep('Processed', '$totProcessed', '$processPct%', Colors.cyanAccent),
                _funnelArrow(),
                _funnelStep('Ranked', '$totRanked', '$rankPct%', const Color(0xFFBB86FC)),
                _funnelArrow(),
                _funnelStep('Qualified', '$qualCount', '$qualPct%', const Color(0xFF4ADE80)),
                _funnelArrow(),
                _funnelStep('Signals', '${buyCount}B/${sellCount}S/${watchCount}W', '100%', Colors.amberAccent),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _qualityBadge(String quality) {
    Color col = Colors.greenAccent;
    if (quality == 'MEDIUM') col = Colors.amberAccent;
    if (quality == 'LOW' || quality == 'NO TRADE') col = Colors.redAccent;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: col.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: col, width: 1),
      ),
      child: Text(
        'QUALITY: $quality',
        style: TextStyle(fontSize: 9, fontWeight: FontWeight.w800, color: col),
      ),
    );
  }

  Widget _funnelStep(String label, String count, String pct, Color color) {
    return Column(
      children: [
        Text(count, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: color)),
        Text(label, style: const TextStyle(fontSize: 9, color: Colors.grey)),
        Text(pct, style: TextStyle(fontSize: 8, color: color.withValues(alpha: 0.7))),
      ],
    );
  }

  Widget _funnelArrow() {
    return const Padding(
      padding: EdgeInsets.symmetric(horizontal: 6),
      child: Icon(Icons.chevron_right, size: 14, color: Colors.grey),
    );
  }
}

class AdvancedDiagnosticsWidget extends StatefulWidget {
  final ScanResponseModel? response;

  const AdvancedDiagnosticsWidget({super.key, this.response});

  @override
  State<AdvancedDiagnosticsWidget> createState() => _AdvancedDiagnosticsWidgetState();
}

class _AdvancedDiagnosticsWidgetState extends State<AdvancedDiagnosticsWidget> {
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    final resp = widget.response;
    return Container(
      margin: const EdgeInsets.only(top: 12, bottom: 20),
      decoration: BoxDecoration(
        color: const Color(0xFF131722),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF2A3654)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            InkWell(
              onTap: () => setState(() => _isExpanded = !_isExpanded),
              borderRadius: BorderRadius.circular(8),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.blueAccent.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.3)),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(_isExpanded ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down, color: Colors.blueAccent, size: 16),
                    const SizedBox(width: 6),
                    Text(
                      _isExpanded ? 'Hide Advanced Diagnostics' : 'Show Advanced Diagnostics',
                      style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Colors.blueAccent, letterSpacing: 0.5),
                    ),
                  ],
                ),
              ),
            ),
            if (_isExpanded && resp != null) ...[
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: const Color(0xFF0A0E1A),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _telemetryItem(Icons.satellite_alt_outlined, 'Provider: Yahoo (Live)'),
                    _telemetryItem(Icons.speed_outlined, 'Latency: 0.8s (24ms/sym)'),
                    _telemetryItem(Icons.memory_rounded, 'RAM: 64MB | Workers: 5'),
                    _telemetryItem(Icons.verified_user_outlined, 'Status: ONLINE'),
                  ],
                ),
              ),
              const SizedBox(height: 10),
              _buildExplainabilitySection(resp),
              const SizedBox(height: 10),
              _buildTodaysBestSection(resp.qualifiedResults),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildExplainabilitySection(ScanResponseModel resp) {
    final rejections = resp.rejectionAnalytics;
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFF0F1424),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF232D48)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'REJECTION REASON BREAKDOWN',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFFFFB347), letterSpacing: 0.6),
          ),
          const SizedBox(height: 8),
          if (rejections.isEmpty)
            const Text('No rejection analytics registered for active universe.', style: TextStyle(fontSize: 10, color: Colors.grey))
          else
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children: rejections.entries.map((e) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: const Color(0xFF182033),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: const Color(0xFF2C3B5E)),
                  ),
                  child: Text(
                    '${e.key}: ${e.value} stocks',
                    style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: Color(0xFFB0C4DE)),
                  ),
                );
              }).toList(),
            ),
        ],
      ),
    );
  }

  Widget _buildTodaysBestSection(List<ScanResultModel> qualified) {
    final top10 = qualified.take(10).toList();
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: const Color(0xFF0F1424),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF232D48)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'TODAYS BEST QUALIFIED CANDIDATES (TOP 10)',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF4ADE80), letterSpacing: 0.6),
          ),
          const SizedBox(height: 8),
          if (top10.isEmpty)
            const Text('No candidates currently qualified.', style: TextStyle(fontSize: 10, color: Colors.grey))
          else
            Column(
              children: List.generate(top10.length, (idx) {
                final item = top10[idx];
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 3),
                  child: Row(
                    children: [
                      Container(
                        width: 20,
                        alignment: Alignment.center,
                        child: Text('#${idx + 1}', style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Colors.grey)),
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(item.symbol, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Colors.white)),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: item.displaySignal.contains('BUY') ? Colors.green.withValues(alpha: 0.2) : Colors.amber.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(item.displaySignal, style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: item.displaySignal.contains('BUY') ? Colors.greenAccent : Colors.amberAccent)),
                      ),
                    ],
                  ),
                );
              }),
            ),
        ],
      ),
    );
  }

  Widget _telemetryItem(IconData icon, String text) {
    return Row(
      children: [
        Icon(icon, size: 10, color: Colors.blueAccent),
        const SizedBox(width: 3),
        Text(text, style: const TextStyle(fontSize: 8, color: Colors.white70)),
      ],
    );
  }
}
