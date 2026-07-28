import 'dart:async';
import 'package:flutter/material.dart';
import '../../../data/models/portfolio_model.dart';
import '../../../data/repositories/portfolio_repository.dart';
import 'position_detail_screen.dart';

class PortfolioScreen extends StatefulWidget {
  const PortfolioScreen({super.key});

  @override
  State<PortfolioScreen> createState() => _PortfolioScreenState();
}

class _PortfolioScreenState extends State<PortfolioScreen>
    with SingleTickerProviderStateMixin {
  final PortfolioRepository _repository = PortfolioRepository();
  PortfolioResponseModel? _data;
  bool _isLoading = false;
  String? _error;
  DateTime? _lastRefreshTime;
  Timer? _autoRefreshTimer;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _fetchPortfolio();
    // Auto-refresh every 30 seconds (Task 5)
    _autoRefreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      if (mounted) _fetchPortfolio(silent: true);
    });
  }

  @override
  void dispose() {
    _autoRefreshTimer?.cancel();
    _tabController.dispose();
    super.dispose();
  }

  bool _isFetching = false;

  Future<void> _fetchPortfolio({bool silent = false}) async {
    if (_isFetching) return;
    _isFetching = true;

    if (!silent) setState(() { _isLoading = true; _error = null; });
    try {
      final data = await _repository.getPortfolio();
      if (mounted) {
        setState(() {
          _data = data;
          _lastRefreshTime = DateTime.now();
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
    } finally {
      _isFetching = false;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Portfolio'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
            onPressed: _isLoading ? null : () => _fetchPortfolio(),
          ),
        ],
        bottom: _data != null
            ? TabBar(
                controller: _tabController,
                tabs: const [
                  Tab(text: 'Open'),
                  Tab(text: 'Insights'),
                  Tab(text: 'Closed'),
                ],
              )
            : null,
      ),
      body: RefreshIndicator(
        onRefresh: () => _fetchPortfolio(),
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
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Loading Portfolio...'),
          ],
        ),
      );
    }

    if (_error != null && _data == null) {
      return Center(
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.cloud_off, color: Colors.orangeAccent, size: 60),
              const SizedBox(height: 16),
              Text('Cannot Load Portfolio', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 8),
              Text(_error!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.grey)),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: _fetchPortfolio,
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    if (_data == null) {
      return const Center(child: Text('No portfolio data available.'));
    }

    return Column(
      children: [
        if (_isLoading) const LinearProgressIndicator(minHeight: 2, color: Colors.blueAccent),
        _buildSummarySection(_data!.summary),
        _buildLastUpdatedBar(),
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildOpenPositionsTab(_data!.openPositions),
              _buildInsightsTab(_data!.insights),
              _buildClosedPositionsTab(_data!.closedPositions),
            ],
          ),
        ),
      ],
    );
  }

  // ── SUMMARY SECTION (Task 1) ────────────────────────────────────────────────

  Widget _buildSummarySection(PortfolioSummaryModel s) {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Theme.of(context).cardColor,
      child: Column(
        children: [
          Row(
            children: [
              Expanded(child: _metricTile('Total Value', '₹${_fmt(s.totalEquity)}', Colors.blueAccent)),
              Expanded(child: _metricTile('Today P&L', '₹${_fmt(s.todayPnl)}', _pnlColor(s.todayPnl), signed: true)),
              Expanded(child: _metricTile('Overall P&L', '₹${_fmt(s.unrealizedPnl + s.realizedPnl)}',
                  _pnlColor(s.unrealizedPnl + s.realizedPnl), signed: true)),
            ],
          ),
          const SizedBox(height: 8),
          const Divider(height: 1, color: Colors.white12),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(child: _metricTile('Available Cash', '₹${_fmt(s.availableCash)}', Colors.white)),
              Expanded(child: _metricTile('Margin Used', '₹${_fmt(s.usedMargin)}', Colors.orangeAccent)),
              Expanded(child: _metricTile('Buying Power', '₹${_fmt(s.buyingPower)}', Colors.cyanAccent)),
            ],
          ),
          const SizedBox(height: 8),
          const Divider(height: 1, color: Colors.white12),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.trending_up, size: 14, color: Colors.grey),
              const SizedBox(width: 4),
              Text(
                'Overall Return: ${s.overallReturnPct >= 0 ? '+' : ''}${s.overallReturnPct.toStringAsFixed(2)}%',
                style: TextStyle(
                  fontSize: 13,
                  color: _pnlColor(s.overallReturnPct),
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metricTile(String label, String value, Color valueColor, {bool signed = false}) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 10, color: Colors.grey)),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: valueColor),
          overflow: TextOverflow.ellipsis,
        ),
      ],
    );
  }

  Widget _buildLastUpdatedBar() {
    if (_lastRefreshTime == null) return const SizedBox.shrink();
    final t = _lastRefreshTime!;
    final ts = '${t.hour.toString().padLeft(2, '0')}:${t.minute.toString().padLeft(2, '0')}:${t.second.toString().padLeft(2, '0')}';
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 5, horizontal: 16),
      color: Colors.black.withValues(alpha: 0.2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.update, size: 12, color: Colors.blueAccent),
          const SizedBox(width: 5),
          Text('Updated: $ts (Auto-refreshes every 30s)',
              style: const TextStyle(fontSize: 11, color: Colors.grey)),
        ],
      ),
    );
  }

  // ── OPEN POSITIONS TAB (Task 2) ─────────────────────────────────────────────

  Widget _buildOpenPositionsTab(List<PositionModel> positions) {
    if (positions.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: const [
          SizedBox(height: 80),
          Center(
            child: Column(children: [
              Icon(Icons.inbox, size: 48, color: Colors.grey),
              SizedBox(height: 12),
              Text('No Open Positions', style: TextStyle(color: Colors.grey, fontSize: 16)),
              SizedBox(height: 8),
              Text('Positions opened by the AI scanner\nwill appear here.',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                  textAlign: TextAlign.center),
            ]),
          ),
        ],
      );
    }

    return ListView.builder(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.only(top: 8, bottom: 16),
      itemCount: positions.length,
      itemBuilder: (ctx, i) => _buildPositionCard(ctx, positions[i]),
    );
  }

  Widget _buildPositionCard(BuildContext context, PositionModel pos) {
    final dirColor = pos.direction.toUpperCase() == 'BUY' ? Colors.greenAccent : Colors.redAccent;
    final pnlColor = _pnlColor(pos.unrealizedPnl);

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: dirColor.withValues(alpha: 0.3), width: 1),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => PositionDetailScreen(position: pos)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header row: Symbol, Exchange, Direction badge
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text(pos.symbol,
                        style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
                    Text('${pos.exchange} • Qty: ${pos.qty}',
                        style: const TextStyle(color: Colors.grey, fontSize: 12)),
                  ]),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: dirColor.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: dirColor, width: 1.2),
                    ),
                    child: Text(pos.direction,
                        style: TextStyle(color: dirColor, fontWeight: FontWeight.bold, fontSize: 12)),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              const Divider(height: 1),
              const SizedBox(height: 10),

              // Prices row
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _cardStat('Avg Price', '₹${pos.entryPrice.toStringAsFixed(2)}', Colors.blueAccent),
                  _cardStat('CMP', '₹${pos.cmp.toStringAsFixed(2)}',
                      pos.cmp > pos.entryPrice ? Colors.greenAccent : Colors.redAccent),
                  _cardStat('R:R', pos.riskReward, Colors.amberAccent),
                ],
              ),
              const SizedBox(height: 12),

              // P&L row
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: pnlColor.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: pnlColor.withValues(alpha: 0.3)),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _cardStat('Today P&L', '₹${pos.unrealizedPnl.toStringAsFixed(2)}', pnlColor),
                    _cardStat('Overall P&L', '₹${pos.unrealizedPnl.toStringAsFixed(2)}', pnlColor),
                    _cardStat('Day %', '${pos.pnlPct.toStringAsFixed(2)}%', pnlColor),
                    _cardStat('Overall %', '${pos.pnlPct.toStringAsFixed(2)}%', pnlColor),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _cardStat(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 3),
        Text(value,
            style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 13),
            overflow: TextOverflow.ellipsis),
      ],
    );
  }

  // ── PORTFOLIO INSIGHTS TAB (Task 6) ─────────────────────────────────────────

  Widget _buildInsightsTab(PortfolioInsightsModel insights) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(16),
      children: [
        _insightCard(
          context,
          title: 'Top Winner',
          symbol: insights.topWinner.symbol,
          value: '₹${_fmt(insights.topWinner.value)}',
          icon: Icons.emoji_events,
          color: Colors.greenAccent,
        ),
        const SizedBox(height: 12),
        _insightCard(
          context,
          title: 'Top Loser',
          symbol: insights.topLoser.symbol,
          value: '₹${_fmt(insights.topLoser.value)}',
          icon: Icons.trending_down,
          color: Colors.redAccent,
        ),
        const SizedBox(height: 12),
        _insightCard(
          context,
          title: 'Largest Position',
          symbol: insights.largestPosition.symbol,
          value: '₹${_fmt(insights.largestPosition.value)}',
          icon: Icons.business_center,
          color: Colors.blueAccent,
        ),
        const SizedBox(height: 12),
        _insightCard(
          context,
          title: 'Highest Profit (Closed)',
          symbol: insights.highestProfit.symbol,
          value: '₹${_fmt(insights.highestProfit.value)}',
          icon: Icons.star,
          color: Colors.amberAccent,
        ),
        const SizedBox(height: 12),
        _insightCard(
          context,
          title: 'Highest Loss (Closed)',
          symbol: insights.highestLoss.symbol,
          value: '₹${_fmt(insights.highestLoss.value)}',
          icon: Icons.warning_amber,
          color: Colors.deepOrangeAccent,
        ),
      ],
    );
  }

  Widget _insightCard(BuildContext context,
      {required String title,
      required String symbol,
      required String value,
      required IconData icon,
      required Color color}) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(color: Colors.grey, fontSize: 12)),
                const SizedBox(height: 4),
                Text(symbol,
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
          Text(value,
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: color)),
        ],
      ),
    );
  }

  // ── CLOSED POSITIONS TAB ────────────────────────────────────────────────────

  Widget _buildClosedPositionsTab(List<ClosedPositionModel> positions) {
    if (positions.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: const [
          SizedBox(height: 80),
          Center(
            child: Column(children: [
              Icon(Icons.history, size: 48, color: Colors.grey),
              SizedBox(height: 12),
              Text('No Closed Positions', style: TextStyle(color: Colors.grey, fontSize: 16)),
              SizedBox(height: 8),
              Text('Completed trades will appear here.',
                  style: TextStyle(color: Colors.grey, fontSize: 12)),
            ]),
          ),
        ],
      );
    }

    return ListView.builder(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.only(top: 8, bottom: 16),
      itemCount: positions.length,
      itemBuilder: (ctx, i) => _buildClosedCard(ctx, positions[i]),
    );
  }

  Widget _buildClosedCard(BuildContext context, ClosedPositionModel pos) {
    final pnlColor = _pnlColor(pos.pnl);
    final dirColor =
        pos.direction.toUpperCase() == 'BUY' ? Colors.greenAccent : Colors.redAccent;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(pos.symbol,
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  Text(pos.direction,
                      style: TextStyle(color: dirColor, fontSize: 12, fontWeight: FontWeight.bold)),
                ]),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: pnlColor.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: pnlColor),
                  ),
                  child: Text(
                    '${pos.pnl >= 0 ? '+' : ''}₹${pos.pnl.toStringAsFixed(2)}',
                    style: TextStyle(color: pnlColor, fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            const Divider(height: 1),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _cardStat('Entry', '₹${pos.entryPrice.toStringAsFixed(2)}', Colors.blueAccent),
                _cardStat('Exit', '₹${pos.exitPrice.toStringAsFixed(2)}', Colors.white),
                _cardStat('Return', '${pos.returnPct >= 0 ? '+' : ''}${pos.returnPct.toStringAsFixed(2)}%', pnlColor),
                _cardStat('Held', pos.holdingDays, Colors.grey),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // ── HELPERS ─────────────────────────────────────────────────────────────────

  String _fmt(double v) {
    if (v.abs() >= 100000) {
      return '${(v / 100000).toStringAsFixed(2)}L';
    } else if (v.abs() >= 1000) {
      return '${(v / 1000).toStringAsFixed(1)}K';
    }
    return v.toStringAsFixed(2);
  }

  Color _pnlColor(double v) =>
      v > 0 ? Colors.greenAccent : v < 0 ? Colors.redAccent : Colors.grey;
}
