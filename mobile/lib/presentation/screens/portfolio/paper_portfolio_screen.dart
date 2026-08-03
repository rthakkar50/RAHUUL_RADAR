import 'package:flutter/material.dart';
import '../../../core/paper_trading/paper_trading_engine.dart';

class PaperPortfolioScreen extends StatefulWidget {
  const PaperPortfolioScreen({super.key});

  @override
  State<PaperPortfolioScreen> createState() => _PaperPortfolioScreenState();
}

class _PaperPortfolioScreenState extends State<PaperPortfolioScreen> {
  final PaperTradingEngine _engine = PaperTradingEngine.instance;

  @override
  void initState() {
    super.initState();
    _engine.addListener(_onEngineUpdate);
    _engine.init();
  }

  @override
  void dispose() {
    _engine.removeListener(_onEngineUpdate);
    super.dispose();
  }

  void _onEngineUpdate() {
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        backgroundColor: const Color(0xFF0B0E14),
        appBar: AppBar(
          backgroundColor: const Color(0xFF0B0E14),
          title: const Text(
            'Enterprise Paper Trading Portfolio',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.restart_alt, color: Colors.amberAccent),
              onPressed: () async {
                final confirm = await showDialog<bool>(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    backgroundColor: const Color(0xFF161B22),
                    title: const Text('Reset Virtual Account?', style: TextStyle(color: Colors.white)),
                    content: const Text('This will reset your paper trading balance to ₹100,000 and clear all positions.', style: TextStyle(color: Colors.white70)),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
                      ElevatedButton(onPressed: () => Navigator.pop(ctx, true), style: ElevatedButton.styleFrom(backgroundColor: Colors.red), child: const Text('Reset Account')),
                    ],
                  ),
                );
                if (confirm == true) {
                  await _engine.resetVirtualAccount();
                }
              },
            ),
          ],
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Open Positions'),
              Tab(text: 'Closed History & Journal'),
              Tab(text: 'Analytics & Risk'),
            ],
          ),
        ),
        body: Column(
          children: [
            _buildPortfolioSummaryHeader(),
            Expanded(
              child: TabBarView(
                children: [
                  _buildOpenPositionsTab(),
                  _buildClosedHistoryTab(),
                  _buildAnalyticsTab(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPortfolioSummaryHeader() {
    final pnlColor = _engine.totalUnrealizedPnL >= 0 ? Colors.greenAccent : Colors.redAccent;

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.3)),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Total Portfolio Equity', style: TextStyle(color: Colors.grey, fontSize: 11)),
                  const SizedBox(height: 2),
                  Text(
                    '₹${_engine.totalPortfolioValue.toStringAsFixed(2)}',
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20),
                  ),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  const Text('Overall Return', style: TextStyle(color: Colors.grey, fontSize: 11)),
                  const SizedBox(height: 2),
                  Text(
                    '${_engine.totalReturnPct >= 0 ? "+" : ""}${_engine.totalReturnPct.toStringAsFixed(2)}%',
                    style: TextStyle(color: pnlColor, fontWeight: FontWeight.bold, fontSize: 18),
                  ),
                ],
              ),
            ],
          ),
          const Divider(color: Colors.white10, height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _subStat('Available Cash', '₹${_engine.availableCash.toStringAsFixed(0)}', Colors.cyanAccent),
              _subStat('Used Margin', '₹${_engine.usedCapital.toStringAsFixed(0)}', Colors.amberAccent),
              _subStat('Unrealized PnL', '₹${_engine.totalUnrealizedPnL.toStringAsFixed(2)}', pnlColor),
              _subStat('Realized PnL', '₹${_engine.totalRealizedPnL.toStringAsFixed(2)}', _engine.totalRealizedPnL >= 0 ? Colors.greenAccent : Colors.redAccent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _subStat(String label, String value, Color color) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 2),
        Text(value, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 11)),
      ],
    );
  }

  Widget _buildOpenPositionsTab() {
    final trades = _engine.openTrades;
    if (trades.isEmpty) {
      return const Center(
        child: Text('No open paper positions. Tap "▶ Paper Trade" on any scanner card to execute virtual orders.', style: TextStyle(color: Colors.grey)),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: trades.length,
      itemBuilder: (ctx, i) {
        final t = trades[i];
        final pnlColor = t.unrealizedPnL >= 0 ? Colors.greenAccent : Colors.redAccent;

        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: pnlColor.withValues(alpha: 0.5))),
          child: Padding(
            padding: const EdgeInsets.all(14.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('${t.symbol} (${t.signal})', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                    Text('PnL: ₹${t.unrealizedPnL.toStringAsFixed(2)}', style: TextStyle(color: pnlColor, fontWeight: FontWeight.bold, fontSize: 14)),
                  ],
                ),
                const SizedBox(height: 6),
                Text('Qty: ${t.quantity} • Entry: ₹${t.entryPrice} • CMP: ₹${t.currentPrice}', style: const TextStyle(color: Colors.white70, fontSize: 12)),
                Text('SL: ₹${t.stopLoss} • T1: ₹${t.target1} • T2: ₹${t.target2}', style: const TextStyle(color: Colors.grey, fontSize: 11)),
                const SizedBox(height: 8),
                Align(
                  alignment: Alignment.centerRight,
                  child: ElevatedButton.icon(
                    onPressed: () async {
                      await _engine.closePosition(t.id);
                    },
                    icon: const Icon(Icons.close, size: 14),
                    label: const Text('Close Position'),
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent, minimumSize: const Size(120, 32)),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildClosedHistoryTab() {
    final trades = _engine.closedTrades;
    if (trades.isEmpty) {
      return const Center(child: Text('No closed trade history yet.', style: TextStyle(color: Colors.grey)));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: trades.length,
      itemBuilder: (ctx, i) {
        final t = trades[i];
        final pnlColor = t.netPnL >= 0 ? Colors.greenAccent : Colors.redAccent;

        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: const BorderSide(color: Colors.white10)),
          child: ListTile(
            title: Text('${t.symbol} (${t.signal})', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: Text('Entry: ₹${t.entryPrice} • Exit: ₹${t.exitPrice} • Qty: ${t.quantity}\nCharges: ₹${t.virtualCharges.toStringAsFixed(2)}', style: const TextStyle(color: Colors.grey, fontSize: 11)),
            trailing: Text('Net PnL\n₹${t.netPnL.toStringAsFixed(2)}', textAlign: TextAlign.right, style: TextStyle(color: pnlColor, fontWeight: FontWeight.bold, fontSize: 13)),
          ),
        );
      },
    );
  }

  Widget _buildAnalyticsTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _diagTile('Total Trades Executed', '${_engine.totalTradesCount}', Colors.cyanAccent),
        _diagTile('Winning Trades', '${_engine.winningTradesCount}', Colors.greenAccent),
        _diagTile('Losing Trades', '${_engine.losingTradesCount}', Colors.redAccent),
        _diagTile('Win Rate %', '${_engine.winRatePct.toStringAsFixed(1)}%', Colors.greenAccent),
        _diagTile('Profit Factor', _engine.profitFactor.toStringAsFixed(2), Colors.amberAccent),
        _diagTile('Starting Capital', '₹${_engine.startingCapital.toStringAsFixed(0)}', Colors.white70),
        _diagTile('Total Portfolio Value', '₹${_engine.totalPortfolioValue.toStringAsFixed(2)}', Colors.cyanAccent),
      ],
    );
  }

  Widget _diagTile(String label, String value, Color color) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(color: const Color(0xFF161B22), borderRadius: BorderRadius.circular(10), border: Border.all(color: Colors.white10)),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
          Text(value, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 13)),
        ],
      ),
    );
  }
}
