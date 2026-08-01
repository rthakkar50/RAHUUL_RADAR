import 'package:flutter/material.dart';
import '../../../data/models/portfolio_model.dart';

class PositionDetailScreen extends StatelessWidget {
  final PositionModel position;

  const PositionDetailScreen({super.key, required this.position});

  Color get _dirColor => position.direction.toUpperCase() == 'BUY'
      ? Colors.greenAccent
      : Colors.redAccent;

  Color _pnlColor(double pnl) => pnl > 0
      ? Colors.greenAccent
      : pnl < 0
      ? Colors.redAccent
      : Colors.grey;

  @override
  Widget build(BuildContext context) {
    final pnl = position.unrealizedPnl;
    final entry = position.entryPrice;
    final cmp = position.cmp;
    final sl = position.sl;
    final target = position.target;
    final risk = (entry - sl).abs();
    final reward = (target - entry).abs();

    // Approximate position age from entryTime
    String positionAge = 'N/A';
    try {
      if (position.entryTime.isNotEmpty) {
        final entered = DateTime.parse(position.entryTime.split('.').first);
        final diff = DateTime.now().difference(entered);
        if (diff.inDays > 0) {
          positionAge = '${diff.inDays}d ${diff.inHours % 24}h';
        } else if (diff.inHours > 0) {
          positionAge = '${diff.inHours}h ${diff.inMinutes % 60}m';
        } else {
          positionAge = '${diff.inMinutes}m';
        }
      }
    } catch (_) {}

    return Scaffold(
      appBar: AppBar(
        title: Text('${position.symbol} Position'),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: _dirColor.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: _dirColor),
            ),
            child: Text(
              position.direction,
              style: TextStyle(
                color: _dirColor,
                fontWeight: FontWeight.bold,
                fontSize: 13,
              ),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header card
            _sectionCard(
              context,
              title: 'Position Overview',
              icon: Icons.account_balance_wallet,
              iconColor: Colors.blueAccent,
              children: [
                _detailRow('Symbol', position.symbol, Colors.white),
                _detailRow(
                  'Exchange',
                  '${position.exchange} • ${position.direction}',
                  _dirColor,
                ),
                _detailRow('Quantity', '${position.qty} shares', Colors.white),
                _detailRow('Position Age', positionAge, Colors.cyanAccent),
                _detailRow(
                  'Entry Time',
                  position.entryTime.isNotEmpty ? position.entryTime : 'N/A',
                  Colors.grey,
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Price levels card
            _sectionCard(
              context,
              title: 'Price Levels',
              icon: Icons.price_change,
              iconColor: Colors.amberAccent,
              children: [
                _detailRow(
                  'Entry Price',
                  '₹${entry.toStringAsFixed(2)}',
                  Colors.blueAccent,
                ),
                _detailRow(
                  'Current Price (CMP)',
                  '₹${cmp.toStringAsFixed(2)}',
                  cmp > entry ? Colors.greenAccent : Colors.redAccent,
                ),
                _detailRow(
                  'Stop Loss',
                  '₹${sl.toStringAsFixed(2)}',
                  Colors.redAccent,
                ),
                _detailRow(
                  'Target',
                  '₹${target.toStringAsFixed(2)}',
                  Colors.greenAccent,
                ),
              ],
            ),
            const SizedBox(height: 16),

            // P&L & Risk/Reward card
            _sectionCard(
              context,
              title: 'P&L & Risk',
              icon: Icons.analytics,
              iconColor: Colors.purpleAccent,
              children: [
                _detailRow(
                  'Unrealized P&L',
                  '₹${pnl.toStringAsFixed(2)} (${position.pnlPct.toStringAsFixed(2)}%)',
                  _pnlColor(pnl),
                ),
                _detailRow(
                  'Margin Used',
                  '₹${position.usedMargin.toStringAsFixed(2)}',
                  Colors.white,
                ),
                _detailRow(
                  'Risk (per share)',
                  '₹${risk.toStringAsFixed(2)}',
                  Colors.redAccent,
                ),
                _detailRow(
                  'Reward (per share)',
                  '₹${reward.toStringAsFixed(2)}',
                  Colors.greenAccent,
                ),
                _detailRow(
                  'Risk : Reward',
                  position.riskReward,
                  Colors.amberAccent,
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Confidence gauge
            _sectionCard(
              context,
              title: 'Confidence (Unrealized P&L vs Target)',
              icon: Icons.show_chart,
              iconColor: Colors.greenAccent,
              children: [
                const SizedBox(height: 4),
                Builder(
                  builder: (ctx) {
                    final maxMove = reward > 0 ? reward * position.qty : 1.0;
                    final progress = (pnl / maxMove).clamp(0.0, 1.0);
                    return Column(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: progress,
                            minHeight: 10,
                            backgroundColor: Colors.grey.withValues(alpha: 0.2),
                            color: _pnlColor(pnl),
                          ),
                        ),
                        const SizedBox(height: 6),
                        Align(
                          alignment: Alignment.centerRight,
                          child: Text(
                            '${(progress * 100).toStringAsFixed(0)}% towards target',
                            style: TextStyle(
                              fontSize: 11,
                              color: _pnlColor(pnl),
                            ),
                          ),
                        ),
                      ],
                    );
                  },
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Quick actions card (UI only — Task 4)
            _sectionCard(
              context,
              title: 'Quick Actions',
              icon: Icons.bolt,
              iconColor: Colors.orangeAccent,
              children: [
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: _actionButton(
                        context,
                        'Exit',
                        Icons.exit_to_app,
                        Colors.redAccent,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _actionButton(
                        context,
                        'Exit Half',
                        Icons.call_split,
                        Colors.orangeAccent,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: _actionButton(
                        context,
                        'Modify SL',
                        Icons.edit,
                        Colors.blueAccent,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _actionButton(
                        context,
                        'Modify Target',
                        Icons.flag,
                        Colors.greenAccent,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                const Text(
                  'Live execution will be available in v1.1',
                  style: TextStyle(fontSize: 10, color: Colors.grey),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _sectionCard(
    BuildContext context, {
    required String title,
    required IconData icon,
    required Color iconColor,
    required List<Widget> children,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: iconColor, size: 18),
              const SizedBox(width: 8),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(height: 1),
          const SizedBox(height: 10),
          ...children,
        ],
      ),
    );
  }

  Widget _detailRow(String label, String value, Color valueColor) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13)),
          Text(
            value,
            style: TextStyle(
              color: valueColor,
              fontWeight: FontWeight.bold,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }

  Widget _actionButton(
    BuildContext context,
    String label,
    IconData icon,
    Color color,
  ) {
    return OutlinedButton.icon(
      onPressed: () {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('$label — Live execution coming in v1.1'),
            backgroundColor: color.withValues(alpha: 0.8),
            duration: const Duration(seconds: 2),
          ),
        );
      },
      style: OutlinedButton.styleFrom(
        foregroundColor: color,
        side: BorderSide(color: color),
        padding: const EdgeInsets.symmetric(vertical: 10),
      ),
      icon: Icon(icon, size: 16),
      label: Text(label, style: const TextStyle(fontSize: 12)),
    );
  }
}
