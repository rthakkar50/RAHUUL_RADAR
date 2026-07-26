import 'package:flutter/material.dart';
import '../../../data/models/dashboard_data_model.dart';
import '../../../data/repositories/dashboard_repository.dart';

class DashboardScreen extends StatefulWidget {
  final void Function(int index)? onNavigate;

  const DashboardScreen({super.key, this.onNavigate});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final DashboardRepository _repository = DashboardRepository();
  DashboardDataModel? _data;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _refreshDashboard();
  }

  Future<void> _refreshDashboard() async {
    setState(() => _isLoading = true);
    final data = await _repository.getDashboardData();
    if (mounted) {
      setState(() {
        _data = data;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('RAHUUL RADAR PRO'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh Dashboard',
            onPressed: _isLoading ? null : _refreshDashboard,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refreshDashboard,
        child: _isLoading && _data == null
            ? const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text('Connecting to Production API...'),
                  ],
                ),
              )
            : SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildStatusSection(),
                    const SizedBox(height: 20),
                    _buildScannerMetricsCard(),
                    const SizedBox(height: 24),
                    const Text(
                      'Quick Actions',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    _buildQuickActions(),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _buildStatusSection() {
    final serverStatus = _data?.serverStatus ?? 'UNKNOWN';
    final isOnline = _data?.isOnline ?? false;
    final marketStatus = _data?.marketStatus ?? 'UNKNOWN';

    return Row(
      children: [
        Expanded(
          child: _buildStatusCard(
            title: 'Server Status',
            value: serverStatus,
            icon: Icons.cloud,
            color: isOnline ? Colors.green : Colors.redAccent,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatusCard(
            title: 'Market Status',
            value: marketStatus,
            icon: Icons.access_time_filled,
            color: marketStatus.contains('OPEN') ? Colors.green : Colors.orangeAccent,
          ),
        ),
      ],
    );
  }

  Widget _buildStatusCard({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.4), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 18, color: color),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildScannerMetricsCard() {
    final marketQuality = _data?.marketQuality ?? 'N/A';
    final totalScanned = _data?.totalScanned ?? 0;
    final qualifiedSignals = _data?.qualifiedSignals ?? 0;
    final lastScan = _data?.lastScanTime ?? 'Never';

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.2),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(Icons.radar, color: Colors.blueAccent),
                  SizedBox(width: 8),
                  Text(
                    'Live AI Scanner Metrics',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: _getQualityColor(marketQuality).withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: _getQualityColor(marketQuality)),
                ),
                child: Text(
                  marketQuality,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    color: _getQualityColor(marketQuality),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Divider(height: 1),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildMetricItem('Total Scanned', '$totalScanned', Icons.bar_chart),
              _buildMetricItem('Qualified Signals', '$qualifiedSignals', Icons.verified, color: Colors.amber),
            ],
          ),
          const SizedBox(height: 16),
          const Divider(height: 1),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              const Icon(Icons.history, size: 14, color: Colors.grey),
              const SizedBox(width: 4),
              Text(
                'Last Scan Time: $lastScan',
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetricItem(String label, String value, IconData icon, {Color color = Colors.white}) {
    return Column(
      children: [
        Icon(icon, size: 24, color: color != Colors.white ? color : Colors.blueAccent),
        const SizedBox(height: 6),
        Text(
          value,
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: color),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(fontSize: 12, color: Colors.grey),
        ),
      ],
    );
  }

  Widget _buildQuickActions() {
    return Column(
      children: [
        _buildActionTile(
          icon: Icons.radar,
          title: 'Launch Live Scanner',
          subtitle: 'Explore high-probability swing trading signals',
          color: Colors.blueAccent,
          onTap: () => widget.onNavigate?.call(1),
        ),
        const SizedBox(height: 12),
        _buildActionTile(
          icon: Icons.pie_chart,
          title: 'View Portfolio',
          subtitle: 'Track simulated positions and unrealized P/L',
          color: Colors.greenAccent,
          onTap: () => widget.onNavigate?.call(2),
        ),
        const SizedBox(height: 12),
        _buildActionTile(
          icon: Icons.menu_book,
          title: 'Trading Journal',
          subtitle: 'Review historical executions and AI decision audit logs',
          color: Colors.purpleAccent,
          onTap: () => widget.onNavigate?.call(3),
        ),
      ],
    );
  }

  Widget _buildActionTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.withValues(alpha: 0.2)),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.15),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey),
          ],
        ),
      ),
    );
  }

  Color _getQualityColor(String quality) {
    final q = quality.toUpperCase();
    if (q.contains('BULL') || q.contains('OPTIM') || q == 'GOOD' || q == 'HIGH') {
      return Colors.greenAccent;
    } else if (q.contains('BEAR') || q.contains('POOR') || q.contains('OFFLINE')) {
      return Colors.redAccent;
    } else if (q.contains('NEUT') || q.contains('SCAN') || q.contains('WAIT')) {
      return Colors.orangeAccent;
    }
    return Colors.blueAccent;
  }
}
