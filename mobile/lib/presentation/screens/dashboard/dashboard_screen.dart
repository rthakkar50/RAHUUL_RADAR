import 'dart:async';
import 'package:flutter/material.dart';
import '../../../core/theme/app_design_system.dart';
import '../../../data/models/dashboard_data_model.dart';
import '../../../data/models/scan_result_model.dart';
import '../../../data/repositories/dashboard_repository.dart';
import '../notifications/notification_screen.dart';
import '../stock_detail/stock_detail_screen.dart';

class DashboardScreen extends StatefulWidget {
  final Function(int) onNavigate;

  const DashboardScreen({super.key, required this.onNavigate});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen>
    with SingleTickerProviderStateMixin {
  final DashboardRepository _repository = DashboardRepository();
  DashboardDataModel? _data;
  bool _isLoading = false;
  String? _error;
  Timer? _autoRefreshTimer;
  String _searchQuery = '';
  final TextEditingController _searchController = TextEditingController();

  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);

    _pulseAnimation = Tween<double>(begin: 0.4, end: 1.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    _fetchDashboard();
    _autoRefreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      if (mounted) _fetchDashboard(silent: true);
    });
  }

  @override
  void dispose() {
    _autoRefreshTimer?.cancel();
    _searchController.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  Future<void> _fetchDashboard({bool silent = false}) async {
    if (!silent) {
      setState(() {
        _isLoading = true;
        _error = null;
      });
    }

    try {
      final data = await _repository.getDashboardData();
      if (mounted) {
        setState(() {
          _data = data;
          _error = null;
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppDesignSystem.background,
      body: SafeArea(
        child: Column(
          children: [
            _buildTopHeader(),
            if (_isLoading && _data != null)
              const LinearProgressIndicator(
                minHeight: 2,
                color: AppDesignSystem.primary,
                backgroundColor: AppDesignSystem.surface,
              ),
            Expanded(child: _buildBody()),
          ],
        ),
      ),
    );
  }

  Widget _buildTopHeader() {
    final d = _data;
    final String brokerLabel = d?.brokerStatusLabel ?? 'Broker: Verifying...';
    final Color brokerColor = (d != null && d.paytmAuthenticated)
        ? AppDesignSystem.success
        : Colors.amberAccent;

    return RepaintBoundary(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: AppDesignSystem.surface.withValues(alpha: 0.95),
          border: const Border(
            bottom: BorderSide(color: AppDesignSystem.border, width: 1),
          ),
        ),
        child: Column(
          children: [
            Row(
              children: [
                GestureDetector(
                  onTap: () => widget.onNavigate(16), // Profile
                  child: Container(
                    padding: const EdgeInsets.all(2),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: AppDesignSystem.primary,
                        width: 1.5,
                      ),
                    ),
                    child: const CircleAvatar(
                      radius: 18,
                      backgroundColor: Color(0xFF1F2937),
                      child: Icon(
                        Icons.person,
                        color: AppDesignSystem.primary,
                        size: 20,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        children: [
                          Text(
                            'RAHUUL THAKKAR',
                            style: TextStyle(
                              color: AppDesignSystem.textPrimary,
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                              letterSpacing: 0.5,
                            ),
                          ),
                          SizedBox(width: 6),
                          DecoratedBox(
                            decoration: BoxDecoration(
                              color: Color(0xFF1E293B),
                              borderRadius: BorderRadius.all(
                                Radius.circular(4),
                              ),
                            ),
                            child: Padding(
                              padding: EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 2,
                              ),
                              child: Text(
                                'INSTITUTIONAL PRO+',
                                style: TextStyle(
                                  color: AppDesignSystem.primary,
                                  fontSize: 9,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 2),
                      Row(
                        children: [
                          _buildConnectionBadge(),
                          const SizedBox(width: 8),
                          Flexible(
                            child: Text(
                              brokerLabel,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                color: brokerColor,
                                fontSize: 11,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(
                    Icons.notifications_outlined,
                    color: AppDesignSystem.textPrimary,
                    size: 22,
                  ),
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => const NotificationScreen(),
                      ),
                    );
                  },
                ),
                IconButton(
                  icon: const Icon(
                    Icons.refresh,
                    color: AppDesignSystem.primary,
                    size: 22,
                  ),
                  onPressed: _isLoading ? null : () => _fetchDashboard(),
                ),
              ],
            ),
            const SizedBox(height: 10),
            // Header Stats Bar — Explicitly separates Actual Broker Funds vs Virtual Risk Capital vs Paper Equity
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: const Color(0xFF0D1117),
                borderRadius: AppDesignSystem.radiusSmall,
                border: Border.all(color: AppDesignSystem.border),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Flexible(
                    child: _headerStatItem(
                      'ACTUAL BROKER CASH',
                      d?.actualBrokerFundsLabel ?? 'UNAVAILABLE',
                      (d != null && d.paytmAuthenticated)
                          ? AppDesignSystem.textPrimary
                          : Colors.amberAccent,
                    ),
                  ),
                  Container(
                    height: 20,
                    width: 1,
                    color: AppDesignSystem.border,
                  ),
                  Flexible(
                    child: _headerStatItem(
                      'VIRTUAL RISK CAP',
                      d?.virtualRiskCapitalLabel ?? 'UNAVAILABLE',
                      AppDesignSystem.primary,
                    ),
                  ),
                  Container(
                    height: 20,
                    width: 1,
                    color: AppDesignSystem.border,
                  ),
                  Flexible(
                    child: _headerStatItem(
                      'PAPER EQUITY',
                      d?.paperEquityLabel ?? 'UNAVAILABLE',
                      AppDesignSystem.textPrimary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _headerStatItem(String label, String val, Color col) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            color: Colors.grey.shade500,
            fontSize: 9,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          val,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            color: col,
            fontWeight: FontWeight.bold,
            fontSize: 11,
          ),
        ),
      ],
    );
  }

  Widget _buildConnectionBadge() {
    final d = _data;
    final isOnline = d?.isOnline ?? false;
    final isDegraded = isOnline &&
        (d == null || d.isStale || d.fallbackUsed || !d.paytmAuthenticated || d.providerHealth != 'HEALTHY');

    final Color badgeColor = !isOnline
        ? AppDesignSystem.danger
        : (isDegraded ? Colors.amberAccent : AppDesignSystem.success);
    final String badgeText = !isOnline
        ? 'OFFLINE'
        : (isDegraded ? 'FALLBACK / CACHED' : 'ONLINE');

    return FadeTransition(
      opacity: _pulseAnimation,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        decoration: BoxDecoration(
          color: badgeColor.withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: badgeColor,
            width: 0.8,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 5,
              height: 5,
              decoration: BoxDecoration(
                color: badgeColor,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 4),
            Text(
              badgeText,
              style: TextStyle(
                color: badgeColor,
                fontSize: 9,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _data == null) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: AppDesignSystem.primary),
            SizedBox(height: 16),
            Text(
              'Initializing Institutional Terminal...',
              style: TextStyle(color: Colors.grey, fontSize: 13),
            ),
          ],
        ),
      );
    }

    if (_error != null && _data == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.cloud_off,
              color: AppDesignSystem.warning,
              size: 54,
            ),
            const SizedBox(height: 16),
            const Text(
              'Terminal Data Connection Interrupted',
              style: TextStyle(
                color: AppDesignSystem.textPrimary,
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _error!,
              style: const TextStyle(color: Colors.grey, fontSize: 12),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: _fetchDashboard,
              icon: const Icon(Icons.refresh),
              label: const Text('Reconnect Terminal'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppDesignSystem.primary,
                foregroundColor: Colors.black,
              ),
            ),
          ],
        ),
      );
    }

    final d = _data!;

    return RefreshIndicator(
      onRefresh: () => _fetchDashboard(),
      color: AppDesignSystem.primary,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (_error != null)
              Container(
                width: double.infinity,
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppDesignSystem.danger.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppDesignSystem.danger),
                ),
                child: Text(
                  'REFRESH FAILED: Displaying last cached dashboard state from ${d.lastScanTime} (Age: ${d.cacheAgeDisplay}).',
                  style: const TextStyle(
                    color: AppDesignSystem.danger,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            if (d.isStale || d.fallbackUsed || !d.paytmAuthenticated)
              Container(
                width: double.infinity,
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.amber.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.amberAccent.withValues(alpha: 0.6)),
                ),
                child: Text(
                  'DATA INTEGRITY NOTICE: ${d.isStale ? "Stale Cache (${d.cacheAgeDisplay} old • Scan: ${d.lastScanTime})" : "Scan: ${d.lastScanTime}"} • Provider: ${d.provider} • Paytm Auth: ${d.paytmAuthenticated ? "YES" : "NO (401)"} • Market: ${d.marketStatus}. Cached signals are NOT actionable live signals.',
                  style: const TextStyle(
                    color: Colors.amberAccent,
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            _buildSearchBar(d),
            const SizedBox(height: 16),
            _buildMarketOverviewSection(d),
            const SizedBox(height: 16),
            _buildPortfolioSnapshotCard(d),
            const SizedBox(height: 16),
            _buildScannerSummaryCard(d),
            const SizedBox(height: 16),
            _buildAiIntelligencePanel(d),
            const SizedBox(height: 16),
            _buildQuickActionsGrid(),
            const SizedBox(height: 16),
            _buildWatchlistWidget(d),
          ],
        ),
      ),
    );
  }

  Widget _buildSearchBar(DashboardDataModel d) {
    final query = _searchQuery.trim().toUpperCase();
    final results = query.length < 2
        ? <ScanResultModel>[]
        : d.qualifiedResults
            .where((item) =>
                item.symbol.toUpperCase().contains(query) ||
                item.company.toUpperCase().contains(query) ||
                item.sector.toUpperCase().contains(query))
            .toList();

    return Column(
      children: [
        Container(
          decoration: AppDesignSystem.glassCard(),
          child: TextField(
            controller: _searchController,
            onChanged: (val) => setState(() => _searchQuery = val),
            style: const TextStyle(
              color: AppDesignSystem.textPrimary,
              fontSize: 13,
            ),
            decoration: InputDecoration(
              hintText: 'Search symbols from current backend scan results...',
              hintStyle: TextStyle(color: Colors.grey.shade600, fontSize: 13),
              prefixIcon: const Icon(
                Icons.search,
                color: AppDesignSystem.primary,
                size: 20,
              ),
              suffixIcon: _searchQuery.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear, color: Colors.grey, size: 18),
                      onPressed: () {
                        _searchController.clear();
                        setState(() => _searchQuery = '');
                      },
                    )
                  : const Icon(Icons.tune, color: Colors.grey, size: 18),
              border: InputBorder.none,
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 14,
              ),
            ),
          ),
        ),
        if (query.length >= 2 && results.isEmpty)
          Container(
            width: double.infinity,
            margin: const EdgeInsets.only(top: 8),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF161B22),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.white10),
            ),
            child: Text(
              'No symbol matching "$query" in current backend scan results.',
              style: const TextStyle(color: Colors.grey, fontSize: 11),
            ),
          ),
        if (results.isNotEmpty)
          Container(
            margin: const EdgeInsets.only(top: 8),
            decoration: BoxDecoration(
              color: const Color(0xFF161B22),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppDesignSystem.primary.withValues(alpha: 0.5)),
            ),
            child: ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: results.length,
              separatorBuilder: (_, _) => const Divider(color: Colors.white10, height: 1),
              itemBuilder: (ctx, idx) {
                final item = results[idx];
                return ListTile(
                  dense: true,
                  leading: CircleAvatar(
                    backgroundColor: AppDesignSystem.primary.withValues(alpha: 0.15),
                    child: Text(
                      item.symbol.isNotEmpty ? item.symbol[0] : '?',
                      style: const TextStyle(color: AppDesignSystem.primary, fontWeight: FontWeight.bold, fontSize: 12),
                    ),
                  ),
                  title: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(item.symbol, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                      Text('₹${item.price.toStringAsFixed(2)}', style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 12)),
                    ],
                  ),
                  subtitle: Text('${item.sector} • ${item.displaySignal} • Data: ${item.timestamp}', style: const TextStyle(color: Colors.grey, fontSize: 10)),
                  onTap: () {
                    _searchController.clear();
                    setState(() => _searchQuery = '');
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => StockDetailScreen(result: item)),
                    );
                  },
                );
              },
            ),
          ),
      ],
    );
  }

  Widget _buildMarketOverviewSection(DashboardDataModel d) {
    final bool isMarketOpen = d.marketStatus.toUpperCase() == 'OPEN';
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Row(
              children: [
                Icon(
                  Icons.show_chart,
                  color: AppDesignSystem.primary,
                  size: 18,
                ),
                SizedBox(width: 6),
                Text(
                  'MARKET & FEED TELEMETRY',
                  style: TextStyle(
                    color: AppDesignSystem.textPrimary,
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                    letterSpacing: 0.8,
                  ),
                ),
              ],
            ),
            Text(
              'MARKET: ${d.marketStatus}',
              style: TextStyle(
                color: isMarketOpen ? AppDesignSystem.success : Colors.amberAccent,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              _buildIndexSparklineCard(
                'NSE INDICES',
                'UNAVAILABLE',
                'Index feed not connected',
                Colors.grey,
                const [],
              ),
              const SizedBox(width: 10),
              _buildIndexSparklineCard(
                'DATA PROVIDER',
                d.provider,
                d.fallbackUsed ? 'Fallback Active' : 'Primary Feed',
                d.fallbackUsed ? Colors.amberAccent : AppDesignSystem.success,
                const [],
              ),
              const SizedBox(width: 10),
              _buildIndexSparklineCard(
                'PAYTM AUTH',
                d.paytmAuthenticated ? 'AUTHENTICATED' : 'UNAUTHENTICATED',
                d.paytmAuthenticated ? 'OAuth Token Valid' : 'HTTP 401 / Reauth Req',
                d.paytmAuthenticated ? AppDesignSystem.success : AppDesignSystem.danger,
                const [],
              ),
              const SizedBox(width: 10),
              _buildIndexSparklineCard(
                'CACHE AGE',
                d.cacheAgeDisplay,
                d.isStale ? 'STALE SNAPSHOT' : 'FRESH SCAN',
                d.isStale ? Colors.amberAccent : AppDesignSystem.success,
                const [],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildIndexSparklineCard(
    String title,
    String price,
    String change,
    Color color,
    List<double> sparkPoints,
  ) {
    return Container(
      width: 165,
      padding: const EdgeInsets.all(12),
      decoration: AppDesignSystem.glassCard(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Flexible(
                child: Text(
                  title,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: Colors.grey.shade400,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Icon(
                color == AppDesignSystem.success
                    ? Icons.check_circle_outline
                    : Icons.info_outline,
                color: color,
                size: 14,
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            price,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              color: AppDesignSystem.textPrimary,
              fontWeight: FontWeight.bold,
              fontSize: 13,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            change,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              color: color,
              fontSize: 10,
              fontWeight: FontWeight.w600,
            ),
          ),
          if (sparkPoints.length >= 2) ...[
            const SizedBox(height: 8),
            SizedBox(
              height: 24,
              width: double.infinity,
              child: CustomPaint(
                painter: _SparklinePainter(points: sparkPoints, color: color),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildPortfolioSnapshotCard(DashboardDataModel d) {
    final bool isBrokerAuth = d.paytmAuthenticated;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: AppDesignSystem.glassCard(
        borderColor: AppDesignSystem.primary.withValues(alpha: 0.3),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(
                    Icons.pie_chart,
                    color: AppDesignSystem.primary,
                    size: 18,
                  ),
                  SizedBox(width: 6),
                  Text(
                    'BROKER vs VIRTUAL / PAPER SNAPSHOT',
                    style: TextStyle(
                      color: AppDesignSystem.textPrimary,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                      letterSpacing: 0.6,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: (isBrokerAuth ? AppDesignSystem.success : Colors.amberAccent)
                      .withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(
                    color: isBrokerAuth ? AppDesignSystem.success : Colors.amberAccent,
                    width: 0.8,
                  ),
                ),
                child: Text(
                  isBrokerAuth ? 'BROKER: AUTH' : 'BROKER: UNAUTH (401)',
                  style: TextStyle(
                    color: isBrokerAuth ? AppDesignSystem.success : Colors.amberAccent,
                    fontSize: 9,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Flexible(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Actual Broker Cash (Paytm)',
                      style: TextStyle(color: Colors.grey, fontSize: 10),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      d.actualBrokerFundsLabel,
                      style: TextStyle(
                        color: isBrokerAuth ? AppDesignSystem.textPrimary : Colors.amberAccent,
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Flexible(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    const Text(
                      'Paper Portfolio Equity (Virtual)',
                      style: TextStyle(color: Colors.grey, fontSize: 10),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      d.paperEquityLabel,
                      style: const TextStyle(
                        color: AppDesignSystem.textPrimary,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(color: AppDesignSystem.border, height: 1),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricItem(
                'Paper Cash',
                d.paperAvailableCashLabel,
                AppDesignSystem.primary,
              ),
              _metricItem('Paper Invested', d.paperUsedMarginLabel, Colors.purpleAccent),
              _metricItem(
                'Open Positions',
                d.paperOpenPositionsLabel,
                AppDesignSystem.textPrimary,
              ),
              _metricItem('Paper P&L', d.paperPnlLabel, AppDesignSystem.warning),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metricItem(String label, String val, Color col) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 9)),
        const SizedBox(height: 3),
        Text(
          val,
          style: TextStyle(
            color: col,
            fontWeight: FontWeight.bold,
            fontSize: 11,
          ),
        ),
      ],
    );
  }

  Widget _buildScannerSummaryCard(DashboardDataModel d) {
    final top = d.topPick;
    final String topPickText = top != null
        ? 'TOP PICK: ${top.symbol} (${top.signal}${d.isStale ? " • CACHED" : ""}) — Score: ${top.score.toStringAsFixed(1)} | T1: ₹${top.target1.toStringAsFixed(2)}'
        : 'TOP PICK: No qualified BUY signal in current scan';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: AppDesignSystem.glassCard(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(Icons.radar, color: AppDesignSystem.primary, size: 18),
                  SizedBox(width: 6),
                  Text(
                    'AI SWING SCANNER WIDGET',
                    style: TextStyle(
                      color: AppDesignSystem.textPrimary,
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                      letterSpacing: 0.8,
                    ),
                  ),
                ],
              ),
              ElevatedButton(
                onPressed: () => widget.onNavigate(2), // Scanner
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppDesignSystem.primary,
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: const Text(
                  'Open Scanner',
                  style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _scannerStat(
                'Scanned',
                '${d.totalScanned}',
                AppDesignSystem.textPrimary,
              ),
              _scannerStat(
                'Qualified',
                '${d.qualifiedSignals}',
                AppDesignSystem.success,
              ),
              _scannerStat(
                'Market Quality',
                d.marketQuality,
                AppDesignSystem.primary,
              ),
              _scannerStat('Scan Timestamp', d.lastScanTime, Colors.cyanAccent),
            ],
          ),
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: const Color(0xFF0D1117),
              borderRadius: AppDesignSystem.radiusSmall,
              border: Border.all(color: AppDesignSystem.border),
            ),
            child: Row(
              children: [
                Icon(
                  top != null ? Icons.star : Icons.info_outline,
                  color: top != null ? Colors.amberAccent : Colors.grey,
                  size: 16,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    topPickText,
                    style: const TextStyle(
                      color: AppDesignSystem.textPrimary,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                TextButton(
                  onPressed: () => widget.onNavigate(2),
                  child: const Text(
                    'Details',
                    style: TextStyle(
                      color: AppDesignSystem.primary,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _scannerStat(String label, String val, Color col) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 4),
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

  Widget _buildAiIntelligencePanel(DashboardDataModel d) {
    final buyCount = d.qualifiedResults.where((r) => r.signal.toUpperCase().contains('BUY')).length;
    final sellCount = d.qualifiedResults.where((r) => r.signal.toUpperCase().contains('SELL')).length;
    final watchCount = d.qualifiedResults.where((r) => r.signal.toUpperCase().contains('WATCH')).length;

    final String avgScoreStr = d.qualifiedResults.isNotEmpty
        ? '${(d.qualifiedResults.map((r) => r.score).reduce((a, b) => a + b) / d.qualifiedResults.length).toStringAsFixed(1)} / 100'
        : 'N/A';
    final String avgConfStr = d.qualifiedResults.isNotEmpty
        ? '${(d.qualifiedResults.map((r) => r.confidence).reduce((a, b) => a + b) / d.qualifiedResults.length).toStringAsFixed(1)}%'
        : 'N/A';

    final String verdictLabel = d.isStale
        ? 'STALE CACHE (NO TRADE)'
        : (d.fallbackUsed || !d.paytmAuthenticated
            ? 'FALLBACK FEED ONLY'
            : (d.marketStatus.toUpperCase() != 'OPEN' ? 'MARKET CLOSED' : 'QUALITY: ${d.marketQuality}'));
    final Color verdictColor = (d.isStale || d.fallbackUsed || !d.paytmAuthenticated || d.marketStatus.toUpperCase() != 'OPEN')
        ? Colors.amberAccent
        : AppDesignSystem.success;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppDesignSystem.secondary.withValues(alpha: 0.2),
            AppDesignSystem.surface,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: AppDesignSystem.radiusMedium,
        border: Border.all(
          color: AppDesignSystem.secondary.withValues(alpha: 0.4),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(Icons.auto_awesome, color: Colors.cyanAccent, size: 18),
                  SizedBox(width: 6),
                  Text(
                    'AI MARKET INTELLIGENCE PANEL',
                    style: TextStyle(
                      color: AppDesignSystem.textPrimary,
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                      letterSpacing: 0.8,
                    ),
                  ),
                ],
              ),
              Text(
                verdictLabel,
                style: TextStyle(
                  color: verdictColor,
                  fontWeight: FontWeight.bold,
                  fontSize: 10,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(color: AppDesignSystem.border, height: 1),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _aiIntelItem(
                'Avg Score',
                avgScoreStr,
                AppDesignSystem.primary,
              ),
              _aiIntelItem(
                'Signal Split',
                '${buyCount}B / ${watchCount}W / ${sellCount}S',
                AppDesignSystem.success,
              ),
              _aiIntelItem('Avg Confidence', avgConfStr, Colors.amberAccent),
              _aiIntelItem(
                'Cache Age',
                d.cacheAgeDisplay,
                verdictColor,
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.purple.withValues(alpha: 0.15),
              borderRadius: AppDesignSystem.radiusSmall,
              border: Border.all(
                color: Colors.purpleAccent.withValues(alpha: 0.3),
              ),
            ),
            child: Row(
              children: [
                const Icon(Icons.psychology, color: Colors.purpleAccent, size: 18),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'TELEMETRY BRIEF: Provider ${d.provider} (${d.providerHealth}) • Scan ${d.lastScanTime} • ${d.qualifiedSignals} qualified setups ($buyCount BUY, $watchCount WATCH, $sellCount SELL).',
                    style: const TextStyle(
                      color: Colors.purpleAccent,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _aiIntelItem(String label, String val, Color col) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 9)),
        const SizedBox(height: 3),
        Text(
          val,
          style: TextStyle(
            color: col,
            fontWeight: FontWeight.bold,
            fontSize: 11,
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActionsGrid() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Icon(Icons.grid_view, color: AppDesignSystem.primary, size: 18),
            SizedBox(width: 6),
            Text(
              'INSTITUTIONAL QUICK ACTIONS',
              style: TextStyle(
                color: AppDesignSystem.textPrimary,
                fontWeight: FontWeight.bold,
                fontSize: 13,
                letterSpacing: 0.8,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 3,
          crossAxisSpacing: 10,
          mainAxisSpacing: 10,
          childAspectRatio: 1.45,
          children: [
            _quickActionCard(
              'Scanner',
              Icons.radar,
              AppDesignSystem.primary,
              () => widget.onNavigate(2),
            ),
            _quickActionCard(
              'F&O Terminal',
              Icons.show_chart,
              AppDesignSystem.primary,
              () => widget.onNavigate(4),
            ),
            _quickActionCard(
              'Portfolio',
              Icons.pie_chart,
              AppDesignSystem.primary,
              () => widget.onNavigate(6),
            ),
            _quickActionCard(
              'Orders',
              Icons.receipt_long,
              AppDesignSystem.primary,
              () => widget.onNavigate(5),
            ),
            _quickActionCard(
              'Journal',
              Icons.menu_book,
              AppDesignSystem.primary,
              () => widget.onNavigate(7),
            ),
            _quickActionCard(
              'Risk Center',
              Icons.shield,
              AppDesignSystem.primary,
              () => widget.onNavigate(8),
            ),
            _quickActionCard(
              'AI Copilot',
              Icons.psychology,
              AppDesignSystem.primary,
              () => widget.onNavigate(3),
            ),
            _quickActionCard(
              'AI Sentinel',
              Icons.security,
              AppDesignSystem.primary,
              () => widget.onNavigate(12),
            ),
            _quickActionCard(
              'Global Macro',
              Icons.public,
              AppDesignSystem.primary,
              () => widget.onNavigate(10),
            ),
          ],
        ),
      ],
    );
  }

  Widget _quickActionCard(
    String label,
    IconData icon,
    Color col,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: AppDesignSystem.radiusSmall,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
        decoration: BoxDecoration(
          color: AppDesignSystem.surface,
          borderRadius: AppDesignSystem.radiusSmall,
          border: Border.all(color: AppDesignSystem.border, width: 1),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: col, size: 20),
            const SizedBox(height: 6),
            Text(
              label,
              style: const TextStyle(
                color: AppDesignSystem.textPrimary,
                fontSize: 11,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWatchlistWidget(DashboardDataModel d) {
    final items = d.qualifiedResults.take(5).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Row(
              children: [
                Icon(
                  Icons.remove_red_eye_outlined,
                  color: AppDesignSystem.primary,
                  size: 18,
                ),
                SizedBox(width: 6),
                Text(
                  'SCANNER CANDIDATE MONITOR',
                  style: TextStyle(
                    color: AppDesignSystem.textPrimary,
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                    letterSpacing: 0.8,
                  ),
                ),
              ],
            ),
            Text(
              '${items.length} SHOWN',
              style: const TextStyle(
                color: Colors.grey,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        if (items.isEmpty)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(14),
            decoration: AppDesignSystem.glassCard(),
            child: const Text(
              'No qualified scan candidates currently available.',
              style: TextStyle(color: Colors.grey, fontSize: 11),
            ),
          )
        else
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: items.length,
            separatorBuilder: (ctx, idx) => const SizedBox(height: 8),
            itemBuilder: (ctx, idx) {
              final item = items[idx];
              final sig = item.signal.toUpperCase();
              final Color col = sig.contains('BUY')
                  ? AppDesignSystem.success
                  : (sig.contains('SELL') ? AppDesignSystem.danger : AppDesignSystem.warning);
              return InkWell(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => StockDetailScreen(result: item)),
                  );
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: AppDesignSystem.glassCard(),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            item.symbol,
                            style: const TextStyle(
                              color: AppDesignSystem.textPrimary,
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            '${item.sector} • Data: ${item.timestamp}',
                            style: const TextStyle(
                              color: Colors.grey,
                              fontSize: 10,
                            ),
                          ),
                        ],
                      ),
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 6,
                              vertical: 3,
                            ),
                            decoration: BoxDecoration(
                              color: col.withValues(alpha: 0.15),
                              borderRadius: BorderRadius.circular(4),
                              border: Border.all(color: col, width: 0.6),
                            ),
                            child: Text(
                              '${item.signal}${d.isStale ? " (CACHED)" : ""} (${item.confidence.toStringAsFixed(0)}%)',
                              style: TextStyle(
                                color: col,
                                fontSize: 9,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          const SizedBox(width: 14),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text(
                                '₹${item.price.toStringAsFixed(2)}',
                                style: const TextStyle(
                                  color: AppDesignSystem.textPrimary,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 13,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                'R:R ${item.riskReward}',
                                style: TextStyle(
                                  color: col,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
      ],
    );
  }
}

class _SparklinePainter extends CustomPainter {
  final List<double> points;
  final Color color;

  _SparklinePainter({required this.points, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    if (points.length < 2) return;

    final minVal = points.reduce((a, b) => a < b ? a : b);
    final maxVal = points.reduce((a, b) => a > b ? a : b);
    final range = maxVal - minVal == 0 ? 1.0 : maxVal - minVal;

    final paint = Paint()
      ..color = color
      ..strokeWidth = 1.8
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final path = Path();

    for (int i = 0; i < points.length; i++) {
      final x = (i / (points.length - 1)) * size.width;
      final y = size.height - ((points[i] - minVal) / range) * size.height;

      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _SparklinePainter oldDelegate) {
    return oldDelegate.points != points || oldDelegate.color != color;
  }
}
