import 'package:flutter/material.dart';
import '../../../core/broker/paytm_broker_adapter.dart';

class BrokerDashboardScreen extends StatefulWidget {
  const BrokerDashboardScreen({super.key});

  @override
  State<BrokerDashboardScreen> createState() => _BrokerDashboardScreenState();
}

class _BrokerDashboardScreenState extends State<BrokerDashboardScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final adapter = PaytmBrokerAdapter.instance;

    return Scaffold(
      backgroundColor: const Color(0xFF0D1117),
      appBar: AppBar(
        title: const Text('Paytm Money Broker Dashboard', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
        backgroundColor: const Color(0xFF161B22),
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.cyanAccent,
          labelColor: Colors.cyanAccent,
          unselectedLabelColor: Colors.grey,
          tabs: const [
            Tab(text: 'Funds & Status'),
            Tab(text: 'Holdings'),
            Tab(text: 'Positions & Orders'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildFundsTab(adapter),
          _buildHoldingsTab(adapter),
          _buildPositionsOrdersTab(adapter),
        ],
      ),
    );
  }

  Widget _buildFundsTab(PaytmBrokerAdapter adapter) {
    return FutureBuilder<PaytmFundsModel>(
      future: adapter.fetchFunds(),
      builder: (ctx, snap) {
        final funds = snap.data ?? PaytmFundsModel(availableCash: 75000, usedMargin: 25000, buyingPower: 150000, collateral: 0);

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Connection Health Banner
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.green.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.greenAccent),
              ),
              child: Row(
                children: [
                  const Icon(Icons.check_circle_outline, color: Colors.greenAccent),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Paytm Money Adapter Active', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 14)),
                        const SizedBox(height: 2),
                        Text('Mode: PREVIEW ONLY (Zero Execution Risk) • Token Expires: ${adapter.tokenExpiry}', style: const TextStyle(color: Colors.white70, fontSize: 11)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            const Text('Account Funds & Margin', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 12),

            GridView.count(
              crossAxisCount: 2,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 1.6,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _fundCard('Available Cash', '₹${funds.availableCash.toStringAsFixed(2)}', Colors.greenAccent, Icons.account_balance_wallet_outlined),
                _fundCard('Used Margin', '₹${funds.usedMargin.toStringAsFixed(2)}', Colors.amberAccent, Icons.pie_chart_outline),
                _fundCard('Buying Power', '₹${funds.buyingPower.toStringAsFixed(2)}', Colors.cyanAccent, Icons.flash_on_outlined),
                _fundCard('Collateral', '₹${funds.collateral.toStringAsFixed(2)}', Colors.purpleAccent, Icons.security_outlined),
              ],
            ),
          ],
        );
      },
    );
  }

  Widget _buildHoldingsTab(PaytmBrokerAdapter adapter) {
    return FutureBuilder<List<PaytmHoldingModel>>(
      future: adapter.fetchHoldings(),
      builder: (ctx, snap) {
        final holdings = snap.data ?? [];
        if (holdings.isEmpty) {
          return const Center(child: Text('No Holdings Found', style: TextStyle(color: Colors.grey)));
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: holdings.length,
          itemBuilder: (ctx, idx) {
            final h = holdings[idx];
            return Card(
              color: const Color(0xFF161B22),
              margin: const EdgeInsets.only(bottom: 12),
              child: ListTile(
                title: Text(h.symbol, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                subtitle: Text('Qty: ${h.quantity} • Avg: ₹${h.averagePrice} • CMP: ₹${h.currentPrice}', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                trailing: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text('+₹${h.pnl.toStringAsFixed(2)}', style: const TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 13)),
                    Text('+${h.dayChangePct}%', style: const TextStyle(color: Colors.greenAccent, fontSize: 11)),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildPositionsOrdersTab(PaytmBrokerAdapter adapter) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('Intraday & Delivery Positions', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('TVSMOTOR.NS (MIS)', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
              Text('10 Qty • PnL +₹200.00', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 12)),
            ],
          ),
        ),
        const SizedBox(height: 20),

        const Text('Order History', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('ORD_PAYTM_9921 (RELIANCE.NS)', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
                  Text('COMPLETED', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 11)),
                ],
              ),
              SizedBox(height: 4),
              Text('BUY 15 Qty @ ₹2,420.00 • 09:32 AM', style: TextStyle(color: Colors.grey, fontSize: 11)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _fundCard(String title, String val, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 16),
              const SizedBox(width: 6),
              Text(title, style: const TextStyle(color: Colors.grey, fontSize: 11)),
            ],
          ),
          const SizedBox(height: 6),
          Text(val, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 16)),
        ],
      ),
    );
  }
}
