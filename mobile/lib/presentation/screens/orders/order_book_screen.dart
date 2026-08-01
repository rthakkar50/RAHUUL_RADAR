import 'package:flutter/material.dart';
import '../../../data/models/order_model.dart';
import '../../../data/repositories/order_repository.dart';

class OrderBookScreen extends StatefulWidget {
  const OrderBookScreen({super.key});

  @override
  State<OrderBookScreen> createState() => _OrderBookScreenState();
}

class _OrderBookScreenState extends State<OrderBookScreen> with SingleTickerProviderStateMixin {
  final OrderRepository _repository = OrderRepository();
  List<OrderBookItemModel> _orders = [];
  bool _isLoading = false;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _fetchBook();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _fetchBook() async {
    setState(() => _isLoading = true);
    try {
      final list = await _repository.fetchOrderBook();
      if (mounted) {
        setState(() {
          _orders = list;
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0E14),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B0E14),
        title: const Text('Live Order Book & Audit Log', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _fetchBook),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Pending'),
            Tab(text: 'Executed'),
            Tab(text: 'Cancelled'),
            Tab(text: 'Audit'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.blueAccent))
          : TabBarView(
              controller: _tabController,
              children: [
                _buildList('PENDING'),
                _buildList('EXECUTED'),
                _buildList('CANCELLED'),
                _buildAuditTab(),
              ],
            ),
    );
  }

  Widget _buildList(String status) {
    final filtered = _orders.where((o) {
      if (status == 'EXECUTED') return o.status == 'COMPLETE' || o.status == 'EXECUTED';
      if (status == 'CANCELLED') return o.status == 'CANCELLED' || o.status == 'REJECTED';
      return o.status == 'OPEN' || o.status == 'PENDING';
    }).toList();

    if (filtered.isEmpty) {
      return Center(
        child: Text('No $status orders in book.', style: const TextStyle(color: Colors.grey)),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: filtered.length,
      itemBuilder: (ctx, i) {
        final item = filtered[i];
        final isBuy = item.action.toUpperCase() == 'BUY';
        final col = isBuy ? Colors.greenAccent : Colors.redAccent;
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 10),
          child: ListTile(
            title: Text('${item.symbol} (${item.action})', style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: Text('Qty: ${item.quantity} • Price: ₹${item.price.toStringAsFixed(2)} • Time: ${item.timestamp}', style: const TextStyle(color: Colors.grey, fontSize: 11)),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(item.status, style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 12)),
                Text(item.orderId, style: const TextStyle(color: Colors.white38, fontSize: 9)),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildAuditTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _auditTile('16:45:02', 'ORDER PLACED', 'DIVISLAB BUY 25 @ ₹4850.00', 'Paytm Money API (Status: 200 OK)'),
        _auditTile('16:45:03', 'ORDER EXECUTED', 'DIVISLAB Filled 25 @ ₹4850.00', 'Broker Order ID: PAYTM-99214'),
        _auditTile('16:30:10', 'SL MODIFIED', 'TVSMOTOR Trailing SL raised to ₹2410', 'Risk Engine V2 Auto-Trigger'),
        _auditTile('15:15:00', 'ORDER CANCELLED', 'DIXON LIMIT 10 @ ₹12400', 'User Manual Cancellation'),
      ],
    );
  }

  Widget _auditTile(String time, String event, String detail, String source) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.white10),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(time, style: const TextStyle(color: Colors.grey, fontSize: 10, fontWeight: FontWeight.bold)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(event, style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 12)),
                const SizedBox(height: 2),
                Text(detail, style: const TextStyle(color: Colors.white, fontSize: 11)),
                Text(source, style: const TextStyle(color: Colors.white38, fontSize: 10)),
              ],
            ),
          )
        ],
      ),
    );
  }
}
