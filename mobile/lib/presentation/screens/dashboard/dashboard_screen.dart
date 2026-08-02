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
                      Row(
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
                          const SizedBox(width: 6),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 6,
                              vertical: 2,
                            ),
                            decoration: const BoxDecoration(
                              color: Color(0xFF1E293B),
                              borderRadius: BorderRadius.all(
                                Radius.circular(4),
                              ),
                            ),
                            child: const Text(
                              'INSTITUTIONAL PRO+',
                              style: TextStyle(
                                color: AppDesignSystem.primary,
                                fontSize: 9,
                                fontWeight: FontWeight.bold,
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
                          Text(
                            'Broker: Connected (Paytm Money)',
                            style: TextStyle(
                              color: Colors.grey.shade400,
                              fontSize: 11,
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
            // Header Stats Bar
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
                  _headerStatItem(
                    'PORTFOLIO EQUITY',
                    '₹9,93,101.13',
                    AppDesignSystem.textPrimary,
                  ),
                  Container(
                    height: 20,
                    width: 1,
                    color: AppDesignSystem.border,
                  ),
                  _headerStatItem(
                    'TODAY P&L',
                    '+₹1,450.00 (+0.15%)',
                    AppDesignSystem.success,
                  ),
                  Container(
                    height: 20,
                    width: 1,
                    color: AppDesignSystem.border,
                  ),
                  _headerStatItem(
                    'MARGIN CASH',
                    '₹2,76,405.13',
                    AppDesignSystem.primary,
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
          style: TextStyle(
            color: Colors.grey.shade500,
            fontSize: 9,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 2),
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

  Widget _buildConnectionBadge() {
    final isOnline = _data?.isOnline ?? true;
    return FadeTransition(
      opacity: _pulseAnimation,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        decoration: BoxDecoration(
          color: (isOnline ? AppDesignSystem.success : AppDesignSystem.danger)
              .withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: isOnline ? AppDesignSystem.success : AppDesignSystem.danger,
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
                color: isOnline
                    ? AppDesignSystem.success
                    : AppDesignSystem.danger,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 4),
            Text(
              isOnline ? 'LIVE WS' : 'OFFLINE',
              style: TextStyle(
                color: isOnline
                    ? AppDesignSystem.success
                    : AppDesignSystem.danger,
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
            _buildSearchBar(),
            const SizedBox(height: 16),
            _buildMarketOverviewSection(),
            const SizedBox(height: 16),
            _buildPortfolioSnapshotCard(d),
            const SizedBox(height: 16),
            _buildScannerSummaryCard(d),
            const SizedBox(height: 16),
            _buildAiIntelligencePanel(d),
            const SizedBox(height: 16),
            _buildQuickActionsGrid(),
            const SizedBox(height: 16),
            _buildWatchlistWidget(),
          ],
        ),
      ),
    );
  }

  Widget _buildSearchBar() {
    final query = _searchQuery.trim().toUpperCase();
    final searchUniverse = [
      {'symbol': 'DIVISLAB.NS', 'company': "Divi's Laboratories Ltd.", 'sector': 'PHARMA', 'price': '4850.00', 'exchange': 'NSE'},
      {'symbol': 'RELIANCE.NS', 'company': 'Reliance Industries Ltd.', 'sector': 'ENERGY', 'price': '2980.00', 'exchange': 'NSE'},
      {'symbol': 'PAYTM.NS', 'company': 'One 97 Communications', 'sector': 'FINTECH', 'price': '850.00', 'exchange': 'NSE'},
      {'symbol': 'TCS.NS', 'company': 'Tata Consultancy Services', 'sector': 'IT', 'price': '4250.00', 'exchange': 'NSE'},
      {'symbol': 'INFY.NS', 'company': 'Infosys Ltd.', 'sector': 'IT', 'price': '1820.00', 'exchange': 'NSE'},
      {'symbol': 'SBIN.NS', 'company': 'State Bank of India', 'sector': 'BANKING', 'price': '845.00', 'exchange': 'NSE'},
      {'symbol': 'HDFCBANK.NS', 'company': 'HDFC Bank Ltd.', 'sector': 'BANKING', 'price': '1640.00', 'exchange': 'NSE'},
      {'symbol': 'ICICIBANK.NS', 'company': 'ICICI Bank Ltd.', 'sector': 'BANKING', 'price': '1220.00', 'exchange': 'NSE'},
      {'symbol': 'TATAMOTORS.NS', 'company': 'Tata Motors Ltd.', 'sector': 'AUTO', 'price': '1040.00', 'exchange': 'NSE'},
      {'symbol': 'AXISBANK.NS', 'company': 'Axis Bank Ltd.', 'sector': 'BANKING', 'price': '1180.00', 'exchange': 'NSE'},
      {'symbol': 'BAJFINANCE.NS', 'company': 'Bajaj Finance Ltd.', 'sector': 'FINANCE', 'price': '6850.00', 'exchange': 'NSE'},
      {'symbol': 'BHARTIARTL.NS', 'company': 'Bharti Airtel Ltd.', 'sector': 'TELECOM', 'price': '1540.00', 'exchange': 'NSE'},
      {'symbol': 'LT.NS', 'company': 'Larsen & Toubro Ltd.', 'sector': 'INFRA', 'price': '3620.00', 'exchange': 'NSE'},
      {'symbol': 'MARUTI.NS', 'company': 'Maruti Suzuki India', 'sector': 'AUTO', 'price': '12400.00', 'exchange': 'NSE'},
      {'symbol': 'SUNPHARMA.NS', 'company': 'Sun Pharmaceutical', 'sector': 'PHARMA', 'price': '1710.00', 'exchange': 'NSE'},
      {'symbol': 'WIPRO.NS', 'company': 'Wipro Ltd.', 'sector': 'IT', 'price': '520.00', 'exchange': 'NSE'},
      {'symbol': 'NTPC.NS', 'company': 'NTPC Ltd.', 'sector': 'POWER', 'price': '395.00', 'exchange': 'NSE'},
      {'symbol': 'ONGC.NS', 'company': 'Oil & Natural Gas Corp', 'sector': 'ENERGY', 'price': '310.00', 'exchange': 'NSE'},
      {'symbol': 'HAL.NS', 'company': 'Hindustan Aeronautics', 'sector': 'DEFENCE', 'price': '4820.00', 'exchange': 'NSE'},
      {'symbol': 'BEL.NS', 'company': 'Bharat Electronics', 'sector': 'DEFENCE', 'price': '295.00', 'exchange': 'NSE'},
      {'symbol': 'DIXON.NS', 'company': 'Dixon Technologies', 'sector': 'ELECTRONICS', 'price': '12400.00', 'exchange': 'NSE'},
      {'symbol': 'ZOMATO.NS', 'company': 'Zomato Ltd.', 'sector': 'CONSUMER', 'price': '230.00', 'exchange': 'NSE'},
      {'symbol': 'IREDA.NS', 'company': 'Indian Renewable Energy', 'sector': 'ENERGY', 'price': '240.00', 'exchange': 'NSE'},
      {'symbol': 'JIOFIN.NS', 'company': 'Jio Financial Services', 'sector': 'FINANCE', 'price': '345.00', 'exchange': 'NSE'},
    ];

    final results = query.length < 2
        ? <Map<String, String>>[]
        : searchUniverse.where((item) =>
            item['symbol']!.toUpperCase().contains(query) ||
            item['company']!.toUpperCase().contains(query) ||
            item['sector']!.toUpperCase().contains(query)).toList();

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
              hintText: 'Search DIV, REL, PAY, TCS, INF or Any Stock...',
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
                      item['symbol']![0],
                      style: const TextStyle(color: AppDesignSystem.primary, fontWeight: FontWeight.bold, fontSize: 12),
                    ),
                  ),
                  title: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(item['symbol']!, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                      Text('₹${item['price']}', style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 12)),
                    ],
                  ),
                  subtitle: Text('${item['company']} • ${item['sector']} (${item['exchange']})', style: const TextStyle(color: Colors.grey, fontSize: 10)),
                  onTap: () {
                    final priceVal = double.tryParse(item['price']!) ?? 1000.0;
                    final scanModel = ScanResultModel(
                      symbol: item['symbol']!,
                      company: item['company']!,
                      sector: item['sector']!,
                      price: priceVal,
                      signal: 'BUY',
                      score: 92.0,
                      rawScore: 90.0,
                      confidence: 90.0,
                      trend: 'BULLISH BREAKOUT',
                      volume: '+280%',
                      riskReward: '1:3.0',
                      rsScore: 88.0,
                      entry: priceVal,
                      stopLoss: priceVal * 0.96,
                      target1: priceVal * 1.08,
                      target2: priceVal * 1.15,
                      tradeGrade: 'A+',
                      riskGrade: 'LOW',
                      timestamp: 'LIVE',
                    );
                    _searchController.clear();
                    setState(() => _searchQuery = '');
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => StockDetailScreen(result: scanModel)),
                    );
                  },
                );
              },
            ),
          ),
      ],
    );
  }

  Widget _buildMarketOverviewSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                Icon(
                  Icons.show_chart,
                  color: AppDesignSystem.primary,
                  size: 18,
                ),
                SizedBox(width: 6),
                Text(
                  'LIVE MARKET OVERVIEW',
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
              'NSE/BSE LIVE',
              style: TextStyle(
                color: AppDesignSystem.success,
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
                'NIFTY 50',
                '24,850.40',
                '+184.20 (+0.75%)',
                AppDesignSystem.success,
                [24600, 24650, 24710, 24680, 24790, 24850],
              ),
              const SizedBox(width: 10),
              _buildIndexSparklineCard(
                'BANK NIFTY',
                '52,450.15',
                '+410.50 (+0.79%)',
                AppDesignSystem.success,
                [51900, 52100, 52050, 52300, 52450],
              ),
              const SizedBox(width: 10),
              _buildIndexSparklineCard(
                'FINNIFTY',
                '23,150.80',
                '+142.10 (+0.62%)',
                AppDesignSystem.success,
                [22950, 23010, 23050, 23100, 23150],
              ),
              const SizedBox(width: 10),
              _buildIndexSparklineCard(
                'SENSEX',
                '81,332.90',
                '+602.40 (+0.75%)',
                AppDesignSystem.success,
                [80600, 80850, 81100, 81332],
              ),
              const SizedBox(width: 10),
              _buildIndexSparklineCard(
                'INDIA VIX',
                '12.45',
                '-0.45 (-3.48%)',
                AppDesignSystem.primary,
                [13.8, 13.5, 13.1, 12.8, 12.45],
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
      width: 155,
      padding: const EdgeInsets.all(12),
      decoration: AppDesignSystem.glassCard(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: TextStyle(
                  color: Colors.grey.shade400,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Icon(
                color == AppDesignSystem.success
                    ? Icons.trending_up
                    : Icons.trending_down,
                color: color,
                size: 14,
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            price,
            style: const TextStyle(
              color: AppDesignSystem.textPrimary,
              fontWeight: FontWeight.bold,
              fontSize: 15,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            change,
            style: TextStyle(
              color: color,
              fontSize: 10,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          SizedBox(
            height: 24,
            width: double.infinity,
            child: CustomPaint(
              painter: _SparklinePainter(points: sparkPoints, color: color),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPortfolioSnapshotCard(DashboardDataModel d) {
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
                    'PORTFOLIO SNAPSHOT',
                    style: TextStyle(
                      color: AppDesignSystem.textPrimary,
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                      letterSpacing: 0.8,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: AppDesignSystem.success.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(
                    color: AppDesignSystem.success,
                    width: 0.8,
                  ),
                ),
                child: const Text(
                  'RISK: LOW (0.69%)',
                  style: TextStyle(
                    color: AppDesignSystem.success,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Total Portfolio Capital',
                    style: TextStyle(color: Colors.grey, fontSize: 10),
                  ),
                  SizedBox(height: 4),
                  Text(
                    '₹9,99,649.32',
                    style: TextStyle(
                      color: AppDesignSystem.textPrimary,
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    'Current Equity Value',
                    style: TextStyle(color: Colors.grey, fontSize: 10),
                  ),
                  SizedBox(height: 4),
                  Text(
                    '₹9,93,101.13',
                    style: TextStyle(
                      color: AppDesignSystem.textPrimary,
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                ],
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
                'Available Cash',
                '₹2,76,405.13',
                AppDesignSystem.primary,
              ),
              _metricItem('Used Margin', '₹7,23,244.20', Colors.purpleAccent),
              _metricItem(
                'Open Positions',
                '5 Active',
                AppDesignSystem.textPrimary,
              ),
              _metricItem('Overall Return', '-0.69%', AppDesignSystem.warning),
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
              _scannerStat('Last Scan', d.lastScanTime, Colors.cyanAccent),
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
                const Icon(Icons.star, color: Colors.amberAccent, size: 16),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text(
                    'TOP PICK: DIVISLAB (BUY) — Score: 88.5/100 | Target: ₹6,500',
                    style: TextStyle(
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
            fontSize: 13,
          ),
        ),
      ],
    );
  }

  Widget _buildAiIntelligencePanel(DashboardDataModel d) {
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
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
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
                'BULLISH / ACCUMULATION',
                style: TextStyle(
                  color: AppDesignSystem.success,
                  fontWeight: FontWeight.bold,
                  fontSize: 11,
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
                'Trend Strength',
                '88.4 / 100',
                AppDesignSystem.primary,
              ),
              _aiIntelItem(
                'Market Breadth',
                '132 Adv / 44 Dec',
                AppDesignSystem.success,
              ),
              _aiIntelItem('AI Confidence', '94.2%', Colors.amberAccent),
              _aiIntelItem(
                'Risk Verdict',
                'SAFE TO ENTER',
                AppDesignSystem.success,
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
            child: const Row(
              children: [
                Icon(Icons.psychology, color: Colors.purpleAccent, size: 18),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'INSTITUTIONAL BRIEF: Accumulate Pharma & IT on pullbacks. Banking index testing 52,500 resistance.',
                    style: TextStyle(
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
              Colors.purpleAccent,
              () => widget.onNavigate(4),
            ),
            _quickActionCard(
              'Portfolio',
              Icons.pie_chart,
              Colors.cyanAccent,
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
              Colors.amberAccent,
              () => widget.onNavigate(7),
            ),
            _quickActionCard(
              'Risk Center',
              Icons.shield,
              AppDesignSystem.danger,
              () => widget.onNavigate(8),
            ),
            _quickActionCard(
              'AI Copilot',
              Icons.psychology,
              Colors.cyanAccent,
              () => widget.onNavigate(3),
            ),
            _quickActionCard(
              'AI Sentinel',
              Icons.security,
              Colors.orangeAccent,
              () => widget.onNavigate(12),
            ),
            _quickActionCard(
              'Global Macro',
              Icons.public,
              Colors.tealAccent,
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
        padding: const EdgeInsets.all(10),
        decoration: AppDesignSystem.glassCard(
          borderColor: col.withValues(alpha: 0.3),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: col, size: 20),
            const SizedBox(height: 4),
            Text(
              label,
              style: const TextStyle(
                color: AppDesignSystem.textPrimary,
                fontSize: 11,
                fontWeight: FontWeight.bold,
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

  Widget _buildWatchlistWidget() {
    final watchlist = [
      {
        'symbol': 'DIVISLAB',
        'name': "Divi's Laboratories",
        'price': '₹6,240.50',
        'change': '+3.4%',
        'signal': 'BUY',
        'color': AppDesignSystem.success,
        'conf': '88.5%',
      },
      {
        'symbol': 'DIXON',
        'name': 'Dixon Technologies',
        'price': '₹14,850.00',
        'change': '+2.1%',
        'signal': 'BUY',
        'color': AppDesignSystem.success,
        'conf': '86.2%',
      },
      {
        'symbol': 'PAYTM',
        'name': 'One97 Communications',
        'price': '₹895.40',
        'change': '+5.88%',
        'signal': 'BUY',
        'color': AppDesignSystem.success,
        'conf': '91.0%',
      },
      {
        'symbol': 'TATASTEEL',
        'name': 'Tata Steel Ltd.',
        'price': '₹154.20',
        'change': '-1.2%',
        'signal': 'WATCH',
        'color': AppDesignSystem.warning,
        'conf': '72.0%',
      },
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                Icon(
                  Icons.remove_red_eye_outlined,
                  color: AppDesignSystem.primary,
                  size: 18,
                ),
                SizedBox(width: 6),
                Text(
                  'INSTITUTIONAL WATCHLIST',
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
              '4 STOCKS',
              style: TextStyle(
                color: Colors.grey,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        ListView.separated(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: watchlist.length,
          separatorBuilder: (ctx, idx) => const SizedBox(height: 8),
          itemBuilder: (ctx, idx) {
            final item = watchlist[idx];
            final col = item['color'] as Color;
            return Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: AppDesignSystem.glassCard(),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item['symbol'] as String,
                        style: const TextStyle(
                          color: AppDesignSystem.textPrimary,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        item['name'] as String,
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
                          '${item['signal']} (${item['conf']})',
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
                            item['price'] as String,
                            style: const TextStyle(
                              color: AppDesignSystem.textPrimary,
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            item['change'] as String,
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
