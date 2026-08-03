import 'package:flutter/material.dart';
import '../../data/models/scan_result_model.dart';
import '../../core/paper_trading/paper_trading_engine.dart';
import '../screens/scanner/widgets/scanner_inspector_dialog.dart';

class UnifiedScannerCard extends StatelessWidget {
  final ScanResultModel item;
  final int rank;
  final String scannerType;
  final bool isHeld;
  final bool isPending;
  final VoidCallback onTap;
  final void Function(ScanResultModel)? onCompareSelect;

  const UnifiedScannerCard({
    super.key,
    required this.item,
    required this.rank,
    this.scannerType = 'Swing',
    this.isHeld = false,
    this.isPending = false,
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
                  Row(
                    children: [
                      Text(
                        item.symbol,
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                      const SizedBox(width: 8),
                      _badge(item.signal, sigColor),
                      const SizedBox(width: 6),
                      if (isHeld)
                        _badge('Holding', Colors.purpleAccent)
                      else if (isPending)
                        _badge('Pending Order', Colors.amberAccent)
                      else
                        _badge(item.sector, Colors.cyanAccent),
                    ],
                  ),
                  Row(
                    children: [
                      Text(
                        '${item.confidence.toStringAsFixed(1)}% AI Score',
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
                  _chip(item.signal == 'SELL' ? 'Daily: Bearish' : 'Daily: Bullish', item.signal == 'SELL' ? Colors.redAccent : Colors.greenAccent),
                  _chip(item.signal == 'SELL' ? 'Weekly: Weak' : 'Weekly: Strong Bull', item.signal == 'SELL' ? Colors.orangeAccent : Colors.lightGreenAccent),
                  _chip('R:R ${item.riskReward}', Colors.cyanAccent),
                ],
              ),
              const SizedBox(height: 8),

              // Trade Metrics Grid
              Text(
                'Ideal Entry Zone: ₹${item.entry} - ₹${(item.entry * 1.005).toStringAsFixed(1)} • SL: ₹${item.stopLoss}',
                style: const TextStyle(color: Colors.white, fontSize: 12),
              ),
              Text(
                'T1: ₹${item.target1} • T2: ₹${item.target2} • Vol: ${item.volume} • Trend: ${item.trend}',
                style: const TextStyle(color: Colors.white70, fontSize: 11),
              ),
              const SizedBox(height: 6),

              // Footer Actions Row
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    item.signal == 'SELL' ? 'Setup Risk: MEDIUM (Short Setup)' : 'Chasing Warning: NO (Ideal Entry)',
                    style: TextStyle(color: sigColor, fontSize: 10, fontWeight: FontWeight.bold),
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
    int qty = (10000.0 / item.entry).floor();
    if (qty < 1) qty = 1;

    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF161B22),
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Execute Paper Trade (${item.symbol})', style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                  IconButton(icon: const Icon(Icons.close, color: Colors.grey), onPressed: () => Navigator.pop(ctx)),
                ],
              ),
              const Divider(color: Colors.white10),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Signal / Side:', style: TextStyle(color: Colors.grey, fontSize: 12)),
                  Text(item.signal, style: TextStyle(color: sigColor, fontWeight: FontWeight.bold, fontSize: 13)),
                ],
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Virtual Entry Price:', style: TextStyle(color: Colors.grey, fontSize: 12)),
                  Text('₹${item.entry}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                ],
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Stop Loss:', style: TextStyle(color: Colors.grey, fontSize: 12)),
                  Text('₹${item.stopLoss}', style: const TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 13)),
                ],
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Target 1 / Target 2:', style: TextStyle(color: Colors.grey, fontSize: 12)),
                  Text('₹${item.target1} / ₹${item.target2}', style: const TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 13)),
                ],
              ),
              const SizedBox(height: 12),
              ElevatedButton.icon(
                onPressed: () async {
                  await PaperTradingEngine.instance.executePaperTradeFromScanner(item, requestedQty: qty);
                  if (ctx.mounted) {
                    Navigator.pop(ctx);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Paper Trade Opened! ${item.symbol} ($qty Qty @ ₹${item.entry})'),
                        backgroundColor: Colors.green,
                      ),
                    );
                  }
                },
                icon: const Icon(Icons.play_arrow, size: 18),
                label: Text('Confirm Virtual Order ($qty Qty • ₹${(item.entry * qty).toStringAsFixed(0)})'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  minimumSize: const Size.fromHeight(44),
                ),
              ),
            ],
          ),
        );
      },
    );
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
