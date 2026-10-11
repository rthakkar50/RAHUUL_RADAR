import 'package:flutter/material.dart';
import '../../data/models/scan_result_model.dart';
import '../screens/scanner/widgets/scanner_inspector_dialog.dart';
import 'order_preview_modal.dart';

class UnifiedScannerCard extends StatelessWidget {
  final ScanResultModel item;
  final int rank;
  final String scannerType;
  final bool isHeld;
  final bool isPending;
  final bool isStale;
  final bool fallbackUsed;
  final String marketStatus;
  final VoidCallback onTap;
  final void Function(ScanResultModel)? onCompareSelect;

  const UnifiedScannerCard({
    super.key,
    required this.item,
    required this.rank,
    this.scannerType = 'Swing',
    this.isHeld = false,
    this.isPending = false,
    this.isStale = false,
    this.fallbackUsed = false,
    this.marketStatus = 'UNKNOWN',
    required this.onTap,
    this.onCompareSelect,
  });

  Color get sigColor {
    final sig = item.signal.toUpperCase();
    if (sig.contains('BUY')) return Colors.greenAccent;
    if (sig.contains('SELL')) return Colors.redAccent;
    return Colors.amberAccent;
  }

  @override
  Widget build(BuildContext context) {
    final String footerNote;
    final Color footerColor;
    if (isStale) {
      footerNote = '⚠️ CACHED SNAPSHOT • Verify Live Price Before Acting';
      footerColor = Colors.amberAccent;
    } else if (fallbackUsed) {
      footerNote = '⚠️ Fallback Feed • Verify Broker LTP Before Entry';
      footerColor = Colors.amberAccent;
    } else if (marketStatus.toUpperCase() == 'CLOSED') {
      footerNote = 'Market Closed • Last Recorded Setup (${item.riskGrade} Risk)';
      footerColor = Colors.white70;
    } else if (item.entryDecision.isNotEmpty) {
      footerNote = 'Decision: ${item.entryDecision} • Risk: ${item.riskGrade}';
      footerColor = sigColor;
    } else {
      footerNote = 'Signal: ${item.signal} • Risk Grade: ${item.riskGrade}';
      footerColor = sigColor;
    }

    return Card(
      color: const Color(0xFF161B22),
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(color: sigColor.withValues(alpha: 0.6), width: 1.5),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        onLongPress: () => ScannerInspectorDialog.show(context, item),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header Row
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Flexible(
                    child: Wrap(
                      crossAxisAlignment: WrapCrossAlignment.center,
                      spacing: 6,
                      runSpacing: 4,
                      children: [
                        Text(
                          item.symbol,
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                        _badge(isStale ? '${item.signal} (CACHED)' : item.signal, isStale ? Colors.amberAccent : sigColor),
                        if (isHeld)
                          _badge('Holding', Colors.purpleAccent)
                        else if (isPending)
                          _badge('Pending Order', Colors.amberAccent)
                        else
                          _badge(item.sector, Colors.cyanAccent),
                      ],
                    ),
                  ),
                  Row(
                    children: [
                      Text(
                        'Score: ${item.score.toStringAsFixed(1)} (${item.confidence.toStringAsFixed(0)}%)',
                        style: TextStyle(color: sigColor, fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                      const SizedBox(width: 4),
                      IconButton(
                        icon: const Icon(Icons.info_outline, size: 16, color: Colors.cyanAccent),
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                        onPressed: () => ScannerInspectorDialog.show(context, item),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 8),

              // Badges Row
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _chip('Trend: ${item.trend}', item.signal == 'SELL' ? Colors.redAccent : Colors.greenAccent),
                  _chip('Grade: ${item.tradeGrade} | Risk: ${item.riskGrade}', Colors.lightGreenAccent),
                  _chip('R:R ${item.riskReward}', Colors.cyanAccent),
                ],
              ),
              const SizedBox(height: 8),

              // Trade Metrics Grid
              Text(
                'Entry: ₹${item.entry.toStringAsFixed(2)} • Price: ₹${item.price.toStringAsFixed(2)} • SL: ₹${item.stopLoss.toStringAsFixed(2)}',
                style: const TextStyle(color: Colors.white, fontSize: 12),
              ),
              Text(
                'T1: ₹${item.target1.toStringAsFixed(2)} • T2: ₹${item.target2.toStringAsFixed(2)} • Vol: ${item.volume} • Data: ${item.timestamp}',
                style: const TextStyle(color: Colors.white70, fontSize: 11),
              ),
              const SizedBox(height: 6),

              // Footer Actions Row
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Flexible(
                    child: Text(
                      footerNote,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(color: footerColor, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
                  Row(
                    children: [
                      GestureDetector(
                        onTap: () => ScannerInspectorDialog.show(context, item),
                        child: const Text('🔍 Inspect', style: TextStyle(color: Colors.blueAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                      ),
                      const SizedBox(width: 10),
                      if (onCompareSelect != null) ...[
                        GestureDetector(
                          onTap: () => onCompareSelect!(item),
                          child: const Text('⚡ Compare', style: TextStyle(color: Colors.cyanAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                        ),
                        const SizedBox(width: 10),
                      ],
                      GestureDetector(
                        onTap: () => _showPaperTradeModal(context),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: Colors.green.withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(4),
                            border: Border.all(color: Colors.greenAccent, width: 0.8),
                          ),
                          child: const Text('▶ Paper Trade', style: TextStyle(color: Colors.greenAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showPaperTradeModal(BuildContext context) {
    OrderPreviewModal.show(context, item);
  }

  Widget _badge(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withValues(alpha: 0.5)),
      ),
      child: Text(
        text,
        style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget _chip(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: TextStyle(color: color, fontSize: 9, fontWeight: FontWeight.w600),
      ),
    );
  }
}
