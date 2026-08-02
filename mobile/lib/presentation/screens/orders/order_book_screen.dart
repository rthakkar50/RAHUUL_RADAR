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
    _tabController = TabController(length: 5, vsync: this);
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
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Colors.amber, Colors.deepOrange]),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.receipt_long, color: Colors.black, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('Institutional Order & Trade Terminal', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _fetchBook),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          tabs: const [
            Tab(text: 'Open Orders'),
            Tab(text: 'Completed Orders'),
            Tab(text: 'Cancelled Orders'),
            Tab(text: 'Rejected Orders'),
            Tab(text: 'Trade Book'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.amberAccent))
          : TabBarView(
              controller: _tabController,
              children: [
                _buildList('OPEN'),
                _buildList('COMPLETE'),
                _buildList('CANCELLED'),
                _buildList('REJECTED'),
                _buildTradeBookTab(),
              ],
            ),
    );
  }

  Widget _buildList(String status) {
    final filtered = _orders.where((o) {
      if (status == 'COMPLETE') return o.status == 'COMPLETE' || o.status == 'EXECUTED';
      if (status == 'CANCELLED') return o.status == 'CANCELLED';
      if (status == 'REJECTED') return o.status == 'REJECTED';
      return o.status == 'OPEN' || o.status == 'PENDING';
    }).toList();

    if (filtered.isEmpty) {
      return Center(
        child: Text('No $status orders found in order book.', style: const TextStyle(color: Colors.grey)),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: filtered.length,
      itemBuilder: (ctx, i) {
        final item = filtered[i];
        final isBuy = item.action.toUpperCase() == 'BUY';
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: const BorderSide(color: Colors.white10)),
          child: ListTile(
            leading: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(color: (isBuy ? Colors.greenAccent : Colors.redAccent).withValues(alpha: 0.2), borderRadius: BorderRadius.circular(6)),
              child: Text(item.action.toUpperCase(), style: TextStyle(color: isBuy ? Colors.greenAccent : Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 11)),
            ),
            title: Text(item.symbol, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
            subtitle: Text('Qty: ${item.quantity} • Price: ₹${item.price} • Order ID: ${item.orderId}\nTime: ${item.timestamp}', style: const TextStyle(color: Colors.white70, fontSize: 11)),
            trailing: Text(item.status, style: TextStyle(color: item.status == 'COMPLETE' ? Colors.greenAccent : Colors.amberAccent, fontWeight: FontWeight.bold, fontSize: 12)),
          ),
        );
      },
    );
  }

  Widget _buildTradeBookTab() {
    final trades = [
      {'date': '2026-08-01', 'time': '14:22:10', 'symbol': 'RELIANCE', 'type': 'BUY', 'qty': '100', 'broker': 'Paytm Money', 'charges': '₹34.50', 'pnl': '+₹2,450.00'},
      {'date': '2026-08-01', 'time': '11:15:40', 'symbol': 'HDFCBANK', 'type': 'BUY', 'qty': '150', 'broker': 'Paytm Money', 'charges': '₹42.00', 'pnl': '+₹3,120.00'},
      {'date': '2026-07-31', 'time': '15:10:05', 'symbol': 'ICICIBANK', 'type': 'SELL', 'qty': '80', 'broker': 'Paytm Money', 'charges': '₹28.10', 'pnl': '+₹1,840.00'},
    ];

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: trades.length,
      itemBuilder: (ctx, i) {
        final t = trades[i];
        final isBuy = t['type'] == 'BUY';
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: BorderSide(color: Colors.amberAccent.withValues(alpha: 0.3))),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Text(t['symbol']!, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(color: (isBuy ? Colors.greenAccent : Colors.redAccent).withValues(alpha: 0.2), borderRadius: BorderRadius.circular(4)),
                          child: Text(t['type']!, style: TextStyle(color: isBuy ? Colors.greenAccent : Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 10)),
                        ),
                      ],
                    ),
                    Text(t['pnl']!, style: const TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 14)),
                  ],
                ),
                const SizedBox(height: 8),
                Text('Qty: ${t['qty']} • Broker: ${t['broker']} • Charges: ${t['charges']}', style: const TextStyle(color: Colors.white70, fontSize: 12)),
                Text('Executed: ${t['date']} at ${t['time']}', style: const TextStyle(color: Colors.white38, fontSize: 11)),
              ],
            ),
          ),
        );
      },
    );
  }
}
