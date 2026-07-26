import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import '../../../core/network/api_config.dart';

// ─────────────────────────────────────────────────────────────────────────────
// Model
// ─────────────────────────────────────────────────────────────────────────────

class RiskReport {
  final double riskUsed;
  final double riskRemaining;
  final double riskUsedPct;
  final double riskRemainingPct;
  final double availableMargin;
  final double buyingPower;
  final double dailyLoss;
  final double dailyProfit;
  final double dailyLossLimit;
  final double dailyProfitTarget;
  final double capital;
  final double totalExposure;
  final double exposurePct;
  final int openTrades;
  final int maxOpenTrades;
  final int ordersToday;
  final int maxOrdersPerDay;
  final int consecutiveLosses;
  final int maxConsecutiveLosses;
  final bool killSwitch;
  final bool autoTrading;

  const RiskReport({
    required this.riskUsed,
    required this.riskRemaining,
    required this.riskUsedPct,
    required this.riskRemainingPct,
    required this.availableMargin,
    required this.buyingPower,
    required this.dailyLoss,
    required this.dailyProfit,
    required this.dailyLossLimit,
    required this.dailyProfitTarget,
    required this.capital,
    required this.totalExposure,
    required this.exposurePct,
    required this.openTrades,
    required this.maxOpenTrades,
    required this.ordersToday,
    required this.maxOrdersPerDay,
    required this.consecutiveLosses,
    required this.maxConsecutiveLosses,
    required this.killSwitch,
    required this.autoTrading,
  });

  factory RiskReport.fromJson(Map<String, dynamic> j) => RiskReport(
        riskUsed: (j['risk_used'] ?? 0).toDouble(),
        riskRemaining: (j['risk_remaining'] ?? 0).toDouble(),
        riskUsedPct: (j['risk_used_pct'] ?? 0).toDouble(),
        riskRemainingPct: (j['risk_remaining_pct'] ?? 100).toDouble(),
        availableMargin: (j['available_margin'] ?? 0).toDouble(),
        buyingPower: (j['buying_power'] ?? 0).toDouble(),
        dailyLoss: (j['daily_loss'] ?? 0).toDouble(),
        dailyProfit: (j['daily_profit'] ?? 0).toDouble(),
        dailyLossLimit: (j['daily_loss_limit'] ?? 5000).toDouble(),
        dailyProfitTarget: (j['daily_profit_target'] ?? 15000).toDouble(),
        capital: (j['capital'] ?? 0).toDouble(),
        totalExposure: (j['total_exposure'] ?? 0).toDouble(),
        exposurePct: (j['exposure_pct'] ?? 0).toDouble(),
        openTrades: (j['open_trades'] ?? 0).toInt(),
        maxOpenTrades: (j['max_open_trades'] ?? 5).toInt(),
        ordersToday: (j['orders_today'] ?? 0).toInt(),
        maxOrdersPerDay: (j['max_orders_per_day'] ?? 20).toInt(),
        consecutiveLosses: (j['consecutive_losses'] ?? 0).toInt(),
        maxConsecutiveLosses: (j['max_consecutive_losses'] ?? 3).toInt(),
        killSwitch: j['kill_switch'] ?? false,
        autoTrading: j['auto_trading'] ?? true,
      );

  static const empty = RiskReport(
    riskUsed: 0, riskRemaining: 0, riskUsedPct: 0, riskRemainingPct: 100,
    availableMargin: 0, buyingPower: 0, dailyLoss: 0, dailyProfit: 0,
    dailyLossLimit: 5000, dailyProfitTarget: 15000, capital: 0,
    totalExposure: 0, exposurePct: 0, openTrades: 0, maxOpenTrades: 5,
    ordersToday: 0, maxOrdersPerDay: 20, consecutiveLosses: 0,
    maxConsecutiveLosses: 3, killSwitch: false, autoTrading: true,
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Repository
// ─────────────────────────────────────────────────────────────────────────────

class RiskRepository {
  final String _base;
  RiskRepository() : _base = ApiConfig().baseUrl;

  Future<RiskReport> fetchReport() async {
    final res = await http
        .get(Uri.parse('$_base/api/v1/risk/report'))
        .timeout(const Duration(seconds: 8));
    if (res.statusCode == 200) {
      return RiskReport.fromJson(json.decode(res.body) as Map<String, dynamic>);
    }
    throw Exception('Risk report fetch failed: ${res.statusCode}');
  }

  Future<bool> activateKillSwitch() async {
    final res = await http
        .post(Uri.parse('$_base/api/v1/risk/kill-switch/activate'))
        .timeout(const Duration(seconds: 8));
    return res.statusCode == 200;
  }

  Future<bool> deactivateKillSwitch() async {
    final res = await http
        .post(Uri.parse('$_base/api/v1/risk/kill-switch/deactivate'))
        .timeout(const Duration(seconds: 8));
    return res.statusCode == 200;
  }

  Future<bool> disableAutoTrading() async {
    final res = await http
        .post(Uri.parse('$_base/api/v1/risk/auto-trading/disable'))
        .timeout(const Duration(seconds: 8));
    return res.statusCode == 200;
  }

  Future<bool> enableAutoTrading() async {
    final res = await http
        .post(Uri.parse('$_base/api/v1/risk/auto-trading/enable'))
        .timeout(const Duration(seconds: 8));
    return res.statusCode == 200;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Risk Screen
// ─────────────────────────────────────────────────────────────────────────────

class RiskScreen extends StatefulWidget {
  const RiskScreen({super.key});

  @override
  State<RiskScreen> createState() => _RiskScreenState();
}

class _RiskScreenState extends State<RiskScreen> with TickerProviderStateMixin {
  final _repo = RiskRepository();
  RiskReport _report = RiskReport.empty;
  bool _loading = true;
  String? _error;
  Timer? _timer;
  late AnimationController _pulseCtrl;
  late Animation<double> _pulseAnim;

  @override
  void initState() {
    super.initState();
    _pulseCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
    _pulseAnim = Tween<double>(begin: 0.85, end: 1.0).animate(
      CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut),
    );
    _load();
    _timer = Timer.periodic(const Duration(seconds: 30), (_) => _load());
  }

  @override
  void dispose() {
    _timer?.cancel();
    _pulseCtrl.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final r = await _repo.fetchReport();
      if (mounted) setState(() { _report = r; _loading = false; _error = null; });
    } catch (e) {
      if (mounted) setState(() { _loading = false; _error = e.toString(); });
    }
  }

  // ── Kill Switch Dialog ────────────────────────────────────────────────────

  Future<void> _confirmKillSwitch() async {
    final confirmed = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A2E),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(children: [
          Icon(Icons.warning_amber_rounded, color: Colors.red, size: 28),
          SizedBox(width: 10),
          Text('EMERGENCY STOP', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontSize: 18)),
        ]),
        content: const Text(
          'This will IMMEDIATELY stop all live trading and cancel all pending orders.\n\nAre you absolutely sure?',
          style: TextStyle(color: Colors.white70, fontSize: 14, height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel', style: TextStyle(color: Colors.white54)),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('STOP ALL TRADING', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      final ok = await _repo.activateKillSwitch();
      if (ok) {
        await _load();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('🔴 Kill Switch Activated — Trading Halted'),
              backgroundColor: Colors.red,
              duration: Duration(seconds: 5),
            ),
          );
        }
      }
    }
  }

  Future<void> _deactivateKillSwitch() async {
    final ok = await _repo.deactivateKillSwitch();
    if (ok) { await _load(); }
  }

  Future<void> _toggleAutoTrading() async {
    if (_report.autoTrading) {
      await _repo.disableAutoTrading();
    } else {
      await _repo.enableAutoTrading();
    }
    await _load();
  }

  // ── Build ─────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D0D1A),
      body: RefreshIndicator(
        onRefresh: _load,
        color: const Color(0xFF7C4DFF),
        backgroundColor: const Color(0xFF1A1A2E),
        child: CustomScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          slivers: [
            _buildAppBar(),
            if (_loading)
              const SliverFillRemaining(child: Center(child: CircularProgressIndicator(color: Color(0xFF7C4DFF))))
            else if (_error != null)
              SliverFillRemaining(
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.cloud_off_rounded, color: Colors.white30, size: 56),
                      const SizedBox(height: 16),
                      Text('Failed to load risk data', style: TextStyle(color: Colors.white54, fontSize: 15)),
                      const SizedBox(height: 8),
                      ElevatedButton.icon(
                        onPressed: _load,
                        icon: const Icon(Icons.refresh_rounded, size: 18),
                        label: const Text('Retry'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF7C4DFF),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                      ),
                    ],
                  ),
                ),
              )
            else ...[
              SliverToBoxAdapter(child: _buildKillSwitchBanner()),
              SliverPadding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                sliver: SliverList(delegate: SliverChildListDelegate([
                  _buildRiskGauge(),
                  const SizedBox(height: 16),
                  _buildCapitalRow(),
                  const SizedBox(height: 16),
                  _buildDailyPnlCard(),
                  const SizedBox(height: 16),
                  _buildProtectionGrid(),
                  const SizedBox(height: 16),
                  _buildExposureCard(),
                  const SizedBox(height: 16),
                  _buildControlsCard(),
                  const SizedBox(height: 32),
                ])),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildAppBar() {
    return SliverAppBar(
      backgroundColor: const Color(0xFF0D0D1A),
      expandedHeight: 90,
      pinned: true,
      flexibleSpace: FlexibleSpaceBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Color(0xFF7C4DFF), Color(0xFFE040FB)]),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.shield_rounded, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 10),
            const Text('Risk Engine', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        centerTitle: false,
        titlePadding: const EdgeInsets.only(left: 16, bottom: 14),
      ),
    );
  }

  Widget _buildKillSwitchBanner() {
    if (!_report.killSwitch) return const SizedBox.shrink();
    return ScaleTransition(
      scale: _pulseAnim,
      child: Container(
        margin: const EdgeInsets.fromLTRB(16, 8, 16, 4),
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
        decoration: BoxDecoration(
          color: Colors.red.withOpacity(0.15),
          border: Border.all(color: Colors.red, width: 1.5),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Row(
          children: [
            const Icon(Icons.dangerous_rounded, color: Colors.red, size: 28),
            const SizedBox(width: 12),
            const Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('KILL SWITCH ACTIVE', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontSize: 15, letterSpacing: 1)),
                  SizedBox(height: 2),
                  Text('All trading is halted. Tap to deactivate.', style: TextStyle(color: Colors.red, fontSize: 12)),
                ],
              ),
            ),
            TextButton(
              onPressed: _deactivateKillSwitch,
              child: const Text('RESET', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRiskGauge() {
    final usedPct = _report.riskUsedPct.clamp(0.0, 100.0) / 100.0;
    final color = usedPct < 0.5
        ? const Color(0xFF00E676)
        : usedPct < 0.8
            ? const Color(0xFFFFAB00)
            : Colors.red;

    return _GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Daily Risk Budget', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
              _PillBadge(
                label: usedPct < 0.5 ? 'SAFE' : usedPct < 0.8 ? 'CAUTION' : 'DANGER',
                color: color,
              ),
            ],
          ),
          const SizedBox(height: 16),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: usedPct,
              minHeight: 12,
              backgroundColor: Colors.white12,
              valueColor: AlwaysStoppedAnimation<Color>(color),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _StatItem(
                label: 'Risk Used',
                value: '₹${_fmt(_report.riskUsed)}',
                color: Colors.red.shade300,
              ),
              _StatItem(
                label: 'Risk Remaining',
                value: '₹${_fmt(_report.riskRemaining)}',
                color: const Color(0xFF00E676),
              ),
              _StatItem(
                label: 'Daily Limit',
                value: '₹${_fmt(_report.dailyLossLimit)}',
                color: Colors.white54,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCapitalRow() {
    return Row(
      children: [
        Expanded(
          child: _GlassCard(
            gradient: const LinearGradient(
              colors: [Color(0xFF1A237E), Color(0xFF283593)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(children: [
                  Icon(Icons.account_balance_wallet_rounded, color: Color(0xFF7986CB), size: 18),
                  SizedBox(width: 6),
                  Text('Available Margin', style: TextStyle(color: Colors.white54, fontSize: 12)),
                ]),
                const SizedBox(height: 8),
                Text(
                  '₹${_fmt(_report.availableMargin)}',
                  style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _GlassCard(
            gradient: const LinearGradient(
              colors: [Color(0xFF1B5E20), Color(0xFF2E7D32)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(children: [
                  Icon(Icons.bolt_rounded, color: Color(0xFF81C784), size: 18),
                  SizedBox(width: 6),
                  Text('Buying Power', style: TextStyle(color: Colors.white54, fontSize: 12)),
                ]),
                const SizedBox(height: 8),
                Text(
                  '₹${_fmt(_report.buyingPower)}',
                  style: const TextStyle(color: Color(0xFF00E676), fontSize: 20, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDailyPnlCard() {
    final netPnl = _report.dailyProfit - _report.riskUsed;
    final isPositive = netPnl >= 0;

    return _GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Daily P&L', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 14),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _PnlStat(label: 'Profit', value: _report.dailyProfit, target: _report.dailyProfitTarget, isGood: true),
              Container(width: 1, height: 50, color: Colors.white12),
              _PnlStat(label: 'Loss', value: _report.riskUsed, target: _report.dailyLossLimit, isGood: false),
              Container(width: 1, height: 50, color: Colors.white12),
              Column(
                children: [
                  Text(
                    isPositive ? '+₹${_fmt(netPnl)}' : '-₹${_fmt(netPnl.abs())}',
                    style: TextStyle(
                      color: isPositive ? const Color(0xFF00E676) : Colors.redAccent,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text('Net P&L', style: TextStyle(color: Colors.white54, fontSize: 11)),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildProtectionGrid() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Daily Protection', style: TextStyle(color: Colors.white54, fontSize: 13, fontWeight: FontWeight.w600, letterSpacing: 0.5)),
        const SizedBox(height: 10),
        Row(children: [
          Expanded(child: _LimitTile(
            icon: Icons.layers_rounded,
            label: 'Open Trades',
            current: _report.openTrades,
            max: _report.maxOpenTrades,
          )),
          const SizedBox(width: 10),
          Expanded(child: _LimitTile(
            icon: Icons.receipt_long_rounded,
            label: 'Orders Today',
            current: _report.ordersToday,
            max: _report.maxOrdersPerDay,
          )),
        ]),
        const SizedBox(height: 10),
        _LimitTile(
          icon: Icons.trending_down_rounded,
          label: 'Consecutive Losses',
          current: _report.consecutiveLosses,
          max: _report.maxConsecutiveLosses,
          wideMode: true,
        ),
      ],
    );
  }

  Widget _buildExposureCard() {
    final expFraction = (_report.exposurePct / 80.0).clamp(0.0, 1.0);
    final expColor = expFraction < 0.6
        ? const Color(0xFF7C4DFF)
        : expFraction < 0.85
            ? const Color(0xFFFFAB00)
            : Colors.red;

    return _GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
            const Text('Portfolio Exposure', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            Text('${_report.exposurePct.toStringAsFixed(1)}%', style: TextStyle(color: expColor, fontWeight: FontWeight.bold, fontSize: 16)),
          ]),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: LinearProgressIndicator(
              value: expFraction,
              minHeight: 8,
              backgroundColor: Colors.white12,
              valueColor: AlwaysStoppedAnimation<Color>(expColor),
            ),
          ),
          const SizedBox(height: 12),
          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
            Text('Deployed: ₹${_fmt(_report.totalExposure)}', style: const TextStyle(color: Colors.white70, fontSize: 13)),
            Text('Capital: ₹${_fmt(_report.capital)}', style: const TextStyle(color: Colors.white54, fontSize: 13)),
          ]),
        ],
      ),
    );
  }

  Widget _buildControlsCard() {
    return _GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Emergency Controls', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 16),
          // Kill Switch
          Row(
            children: [
              Expanded(
                child: GestureDetector(
                  onTap: _report.killSwitch ? _deactivateKillSwitch : _confirmKillSwitch,
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    decoration: BoxDecoration(
                      color: _report.killSwitch ? Colors.red.withOpacity(0.2) : Colors.red.withOpacity(0.08),
                      border: Border.all(
                        color: _report.killSwitch ? Colors.red : Colors.red.withOpacity(0.4),
                        width: _report.killSwitch ? 2 : 1,
                      ),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Column(children: [
                      Icon(
                        _report.killSwitch ? Icons.stop_circle : Icons.stop_circle_outlined,
                        color: Colors.red,
                        size: 32,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        _report.killSwitch ? 'KILL SWITCH\nACTIVE' : 'KILL SWITCH\nSTOP ALL',
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontSize: 12, letterSpacing: 0.5),
                      ),
                    ]),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: GestureDetector(
                  onTap: _toggleAutoTrading,
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    decoration: BoxDecoration(
                      color: _report.autoTrading
                          ? const Color(0xFF7C4DFF).withOpacity(0.12)
                          : Colors.orange.withOpacity(0.1),
                      border: Border.all(
                        color: _report.autoTrading
                            ? const Color(0xFF7C4DFF).withOpacity(0.5)
                            : Colors.orange.withOpacity(0.5),
                      ),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Column(children: [
                      Icon(
                        _report.autoTrading ? Icons.smart_toy_rounded : Icons.smart_toy_outlined,
                        color: _report.autoTrading ? const Color(0xFF7C4DFF) : Colors.orange,
                        size: 32,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        _report.autoTrading ? 'AUTO TRADING\nENABLED' : 'AUTO TRADING\nDISABLED',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: _report.autoTrading ? const Color(0xFF7C4DFF) : Colors.orange,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                          letterSpacing: 0.5,
                        ),
                      ),
                    ]),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.05),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Text(
              '⚠️  Cancel Pending Orders is automatically executed when Kill Switch is activated.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white54, fontSize: 11, height: 1.4),
            ),
          ),
        ],
      ),
    );
  }

  // ── Utilities ─────────────────────────────────────────────────────────────

  String _fmt(double v) {
    if (v >= 100000) return '${(v / 100000).toStringAsFixed(2)}L';
    if (v >= 1000) return '${(v / 1000).toStringAsFixed(1)}K';
    return v.toStringAsFixed(0);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-widgets
// ─────────────────────────────────────────────────────────────────────────────

class _GlassCard extends StatelessWidget {
  final Widget child;
  final Gradient? gradient;

  const _GlassCard({required this.child, this.gradient});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        gradient: gradient,
        color: gradient == null ? const Color(0xFF1A1A2E) : null,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.07)),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.3), blurRadius: 12, offset: const Offset(0, 4))],
      ),
      child: child,
    );
  }
}

class _PillBadge extends StatelessWidget {
  final String label;
  final Color color;
  const _PillBadge({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        border: Border.all(color: color.withOpacity(0.5)),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(label, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.5)),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String label;
  final String value;
  final Color color;
  const _StatItem({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(value, style: TextStyle(color: color, fontSize: 16, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Text(label, style: const TextStyle(color: Colors.white38, fontSize: 11)),
      ],
    );
  }
}

class _PnlStat extends StatelessWidget {
  final String label;
  final double value;
  final double target;
  final bool isGood;
  const _PnlStat({required this.label, required this.value, required this.target, required this.isGood});

  @override
  Widget build(BuildContext context) {
    final pct = (value / target * 100).clamp(0.0, 100.0);
    final color = isGood ? const Color(0xFF00E676) : Colors.redAccent;
    return Column(
      children: [
        Text('₹${_fmt(value)}', style: TextStyle(color: color, fontSize: 16, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Text(label, style: const TextStyle(color: Colors.white54, fontSize: 11)),
        const SizedBox(height: 6),
        Text('${pct.toStringAsFixed(0)}% of target', style: TextStyle(color: Colors.white38, fontSize: 10)),
      ],
    );
  }

  String _fmt(double v) {
    if (v >= 100000) return '${(v / 100000).toStringAsFixed(2)}L';
    if (v >= 1000) return '${(v / 1000).toStringAsFixed(1)}K';
    return v.toStringAsFixed(0);
  }
}

class _LimitTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final int current;
  final int max;
  final bool wideMode;

  const _LimitTile({
    required this.icon,
    required this.label,
    required this.current,
    required this.max,
    this.wideMode = false,
  });

  @override
  Widget build(BuildContext context) {
    final frac = max > 0 ? (current / max).clamp(0.0, 1.0) : 0.0;
    final isWarning = frac >= 0.75;
    final isDanger = frac >= 1.0;
    final color = isDanger ? Colors.red : isWarning ? const Color(0xFFFFAB00) : const Color(0xFF7C4DFF);

    return Container(
      padding: EdgeInsets.symmetric(horizontal: 14, vertical: wideMode ? 14 : 16),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A2E),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: isDanger ? Colors.red.withOpacity(0.5) : Colors.white.withOpacity(0.07)),
      ),
      child: wideMode
          ? Row(children: [
              Icon(icon, color: color, size: 22),
              const SizedBox(width: 12),
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(label, style: const TextStyle(color: Colors.white70, fontSize: 12)),
                  const SizedBox(height: 6),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: frac, minHeight: 6,
                      backgroundColor: Colors.white12,
                      valueColor: AlwaysStoppedAnimation<Color>(color),
                    ),
                  ),
                ]),
              ),
              const SizedBox(width: 12),
              Text('$current / $max', style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 14)),
            ])
          : Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(children: [
                Icon(icon, color: color, size: 18),
                const SizedBox(width: 6),
                Expanded(child: Text(label, style: const TextStyle(color: Colors.white70, fontSize: 11), overflow: TextOverflow.ellipsis)),
              ]),
              const SizedBox(height: 10),
              Text('$current / $max', style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 18)),
              const SizedBox(height: 6),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: frac, minHeight: 6,
                  backgroundColor: Colors.white12,
                  valueColor: AlwaysStoppedAnimation<Color>(color),
                ),
              ),
            ]),
    );
  }
}
