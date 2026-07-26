import 'package:flutter/material.dart';
import '../../../data/models/journal_model.dart';
import '../../../data/repositories/journal_repository.dart';

class JournalScreen extends StatefulWidget {
  const JournalScreen({super.key});

  @override
  State<JournalScreen> createState() => _JournalScreenState();
}

class _JournalScreenState extends State<JournalScreen> {
  final JournalRepository _repository = JournalRepository();
  JournalResponseModel? _data;
  bool _isLoading = false;
  String? _error;
  String _selectedFilter = 'ALL'; // ALL, BUY, SELL, WIN, LOSS

  final List<String> _filters = ['ALL', 'BUY', 'SELL', 'WIN', 'LOSS'];

  @override
  void initState() {
    super.initState();
    _fetchJournal();
  }

  Future<void> _fetchJournal() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final data = await _repository.getJournal();
      if (mounted) {
        setState(() {
          _data = data;
          _isLoading = false;
          _error = null;
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

  List<JournalTradeModel> get _filteredTrades {
    if (_data == null) return [];
    final all = _data!.trades;
    switch (_selectedFilter) {
      case 'BUY':
        return all.where((t) => t.signal.toUpperCase() == 'BUY').toList();
      case 'SELL':
        return all.where((t) => t.signal.toUpperCase() == 'SELL').toList();
      case 'WIN':
        return all.where((t) => t.pnl > 0 || t.result.toUpperCase() == 'WIN').toList();
      case 'LOSS':
        return all.where((t) => t.pnl < 0 || t.result.toUpperCase() == 'LOSS').toList();
      case 'ALL':
      default:
        return all;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D0D1A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0D0D1A),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF2196F3), Color(0xFF00BCD4)],
                ),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.menu_book, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 10),
            const Text(
              'Trade Journal',
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 18,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white70),
            tooltip: 'Refresh Journal',
            onPressed: _isLoading ? null : _fetchJournal,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _fetchJournal,
        color: const Color(0xFF2196F3),
        backgroundColor: const Color(0xFF1A1A2E),
        child: _buildBody(),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _data == null) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: Color(0xFF2196F3)),
            SizedBox(height: 16),
            Text(
              'Loading Trade Journal...',
              style: TextStyle(color: Colors.white70, fontSize: 14),
            ),
          ],
        ),
      );
    }

    if (_error != null && _data == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.cloud_off_rounded, color: Colors.white30, size: 56),
              const SizedBox(height: 16),
              Text(
                'Failed to load journal',
                style: TextStyle(color: Colors.red.shade300, fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                _error!,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white54, fontSize: 12),
              ),
              const SizedBox(height: 20),
              ElevatedButton.icon(
                onPressed: _fetchJournal,
                icon: const Icon(Icons.refresh, size: 18),
                label: const Text('Retry'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2196F3),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ],
          ),
        ),
      );
    }

    final trades = _filteredTrades;

    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_data != null) ...[
            _buildAnalyticsDashboard(_data!.analytics),
            const SizedBox(height: 16),
            _buildPnLOverviewCard(_data!.analytics),
            const SizedBox(height: 20),
          ],
          _buildFilterChips(),
          const SizedBox(height: 16),
          if (trades.isEmpty)
            _buildEmptyState()
          else
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: trades.length,
              itemBuilder: (context, index) {
                return _buildTradeCard(trades[index]);
              },
            ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  // ── Analytics Overview Cards ─────────────────────────────────────────────

  Widget _buildAnalyticsDashboard(JournalAnalyticsModel analytics) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A2E),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.07)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 4),
          )
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Performance Metrics',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(
                child: _buildMetricTile(
                  label: 'Total Trades',
                  value: '${analytics.totalTrades}',
                  icon: Icons.format_list_bulleted,
                  color: const Color(0xFF64B5F6),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _buildMetricTile(
                  label: 'Win Rate',
                  value: '${analytics.winRate.toStringAsFixed(1)}%',
                  icon: Icons.pie_chart_rounded,
                  color: analytics.winRate >= 50 ? const Color(0xFF00E676) : Colors.orangeAccent,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: _buildMetricTile(
                  label: 'Profit Factor',
                  value: analytics.profitFactor > 0
                      ? analytics.profitFactor.toStringAsFixed(2)
                      : 'N/A',
                  icon: Icons.trending_up_rounded,
                  color: analytics.profitFactor >= 1.5
                      ? const Color(0xFF00E676)
                      : Colors.orangeAccent,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _buildMetricTile(
                  label: 'Avg Hold Time',
                  value: analytics.averageHoldTime,
                  icon: Icons.access_time_rounded,
                  color: const Color(0xFF00BCD4),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPnLOverviewCard(JournalAnalyticsModel analytics) {
    final dailyTotal = analytics.dailyPnl.fold<double>(0.0, (sum, item) => sum + item.pnl);
    final monthlyTotal = analytics.monthlyPnl.fold<double>(0.0, (sum, item) => sum + item.pnl);

    return Row(
      children: [
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: dailyTotal >= 0
                    ? [const Color(0xFF1B5E20), const Color(0xFF2E7D32)]
                    : [const Color(0xFF880E4F), const Color(0xFFAD1457)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Daily P&L',
                  style: TextStyle(color: Colors.white70, fontSize: 12),
                ),
                const SizedBox(height: 6),
                Text(
                  '${dailyTotal >= 0 ? '+' : ''}₹${_fmt(dailyTotal)}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: monthlyTotal >= 0
                    ? [const Color(0xFF004D40), const Color(0xFF00796B)]
                    : [const Color(0xFF4A148C), const Color(0xFF6A1B9A)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Monthly P&L',
                  style: TextStyle(color: Colors.white70, fontSize: 12),
                ),
                const SizedBox(height: 6),
                Text(
                  '${monthlyTotal >= 0 ? '+' : ''}₹${_fmt(monthlyTotal)}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMetricTile({
    required String label,
    required String value,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF131326),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: TextStyle(
                    color: color,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                Text(
                  label,
                  style: const TextStyle(color: Colors.white54, fontSize: 10),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── Filter Chips ─────────────────────────────────────────────────────────

  Widget _buildFilterChips() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: _filters.map((f) {
          final isSelected = _selectedFilter == f;
          return Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: ChoiceChip(
              label: Text(f),
              selected: isSelected,
              selectedColor: const Color(0xFF2196F3),
              backgroundColor: const Color(0xFF1A1A2E),
              labelStyle: TextStyle(
                color: isSelected ? Colors.white : Colors.white70,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                fontSize: 12,
              ),
              side: BorderSide(
                color: isSelected
                    ? const Color(0xFF2196F3)
                    : Colors.white.withOpacity(0.1),
              ),
              onSelected: (val) {
                if (val) setState(() => _selectedFilter = f);
              },
            ),
          );
        }).toList(),
      ),
    );
  }

  // ── Trade Card ───────────────────────────────────────────────────────────

  Widget _buildTradeCard(JournalTradeModel trade) {
    final isBuy = trade.signal.toUpperCase() == 'BUY';
    final isWin = trade.pnl >= 0;
    final pnlColor = isWin ? const Color(0xFF00E676) : Colors.redAccent;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A2E),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isWin ? Colors.green.withOpacity(0.2) : Colors.red.withOpacity(0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Row: Symbol + BUY/SELL badge + Result badge
          Row(
            children: [
              Text(
                trade.symbol,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: isBuy
                      ? Colors.green.withOpacity(0.2)
                      : Colors.red.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  trade.signal.toUpperCase(),
                  style: TextStyle(
                    color: isBuy ? const Color(0xFF00E676) : Colors.redAccent,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: pnlColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: pnlColor.withOpacity(0.5)),
                ),
                child: Text(
                  '${isWin ? '+' : ''}₹${_fmt(trade.pnl)} (${trade.pnlPct.toStringAsFixed(1)}%)',
                  style: TextStyle(
                    color: pnlColor,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Price Row: Entry | Exit | Qty | R-Multiple
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildDetailItem('Entry', '₹${trade.entryPrice.toStringAsFixed(1)}'),
              _buildDetailItem('Exit', '₹${trade.exitPrice.toStringAsFixed(1)}'),
              _buildDetailItem('Qty', '${trade.qty}'),
              _buildDetailItem('R-Mult', trade.rMultiple),
            ],
          ),
          const SizedBox(height: 10),
          const Divider(color: Colors.white10, height: 1),
          const SizedBox(height: 10),

          // Footer Row: AI Score | Confidence | Trade Date
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.auto_awesome, color: Color(0xFF00BCD4), size: 14),
                  const SizedBox(width: 4),
                  Text(
                    'AI Score: ${trade.aiScore.toStringAsFixed(1)}',
                    style: const TextStyle(color: Colors.white70, fontSize: 11),
                  ),
                  const SizedBox(width: 10),
                  Text(
                    'Conf: ${trade.confidence.toStringAsFixed(1)}%',
                    style: const TextStyle(color: Colors.white54, fontSize: 11),
                  ),
                ],
              ),
              Text(
                trade.tradeDate,
                style: const TextStyle(color: Colors.white38, fontSize: 11),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDetailItem(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(color: Colors.white38, fontSize: 10),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 12,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 20),
      child: Column(
        children: [
          const Icon(Icons.history_rounded, color: Colors.white24, size: 48),
          const SizedBox(height: 12),
          Text(
            'No trades match filter "$_selectedFilter"',
            style: const TextStyle(color: Colors.white54, fontSize: 14),
          ),
        ],
      ),
    );
  }

  String _fmt(double v) {
    if (v.abs() >= 100000) return '${(v / 100000).toStringAsFixed(2)}L';
    if (v.abs() >= 1000) return '${(v / 1000).toStringAsFixed(1)}K';
    return v.toStringAsFixed(0);
  }
}

extension ColorsExt on Colors {
  static const Color blueLighten = Color(0xFF64B5F6);
}
