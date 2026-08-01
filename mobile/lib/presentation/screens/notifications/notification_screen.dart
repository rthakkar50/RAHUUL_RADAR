import 'package:flutter/material.dart';

class NotificationItem {
  final String title;
  final String message;
  final String time;
  final String type; // AI, BUY, SELL, TARGET, SL, BROKER, RISK
  final Color color;

  const NotificationItem({
    required this.title,
    required this.message,
    required this.time,
    required this.type,
    required this.color,
  });
}

class NotificationScreen extends StatefulWidget {
  const NotificationScreen({super.key});

  @override
  State<NotificationScreen> createState() => _NotificationScreenState();
}

class _NotificationScreenState extends State<NotificationScreen> {
  String _filter = 'ALL';

  final List<NotificationItem> _notifications = const [
    NotificationItem(
      title: 'Target 1 Reached — DIVISLAB',
      message:
          'DIVISLAB hit Target 1 at ₹9,673.00 (+20.78%). AI trailing stop activated.',
      time: '10 mins ago',
      type: 'TARGET',
      color: Colors.greenAccent,
    ),
    NotificationItem(
      title: 'AI High Confidence BUY — TVSMOTOR',
      message:
          'AI Engine V2 registered A-Grade BUY Signal on TVSMOTOR (Confidence 93.4%).',
      time: '25 mins ago',
      type: 'BUY',
      color: Colors.cyanAccent,
    ),
    NotificationItem(
      title: 'Paytm Money API Connected',
      message:
          'Broker WebSocket feed connected successfully. Zero order latency detected.',
      time: '1 hour ago',
      type: 'BROKER',
      color: Colors.blueAccent,
    ),
    NotificationItem(
      title: 'Risk Engine Circuit Breaker Safe',
      message:
          'Live risk limits validated. Portfolio exposure is 0.69% (Limit 1.0%).',
      time: '2 hours ago',
      type: 'RISK',
      color: Colors.purpleAccent,
    ),
    NotificationItem(
      title: 'Stop Loss Alert — DRREDDY',
      message:
          'DRREDDY hit trailing Stop Loss at ₹1,249.10. Position closed with controlled loss.',
      time: '3 hours ago',
      type: 'SL',
      color: Colors.redAccent,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final filtered = _notifications.where((n) {
      if (_filter == 'ALL') return true;
      return n.type == _filter;
    }).toList();

    return Scaffold(
      backgroundColor: const Color(0xFF0B0E14),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B0E14),
        title: const Text(
          'Notification Center',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
      ),
      body: Column(
        children: [
          _buildFilterChips(),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: filtered.length,
              itemBuilder: (ctx, i) => _buildCard(filtered[i]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChips() {
    final filters = ['ALL', 'BUY', 'SELL', 'TARGET', 'SL', 'RISK', 'BROKER'];
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: filters.map((f) {
          final isSel = _filter == f;
          return Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: ChoiceChip(
              label: Text(f),
              selected: isSel,
              selectedColor: Colors.blueAccent,
              backgroundColor: const Color(0xFF161B22),
              labelStyle: TextStyle(
                color: isSel ? Colors.white : Colors.white70,
                fontSize: 11,
              ),
              onSelected: (val) {
                if (val) setState(() => _filter = f);
              },
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildCard(NotificationItem item) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: item.color.withValues(alpha: 0.3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: item.color.withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.notifications_active,
              color: item.color,
              size: 18,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        item.title,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ),
                    Text(
                      item.time,
                      style: const TextStyle(color: Colors.grey, fontSize: 10),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  item.message,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 11,
                    height: 1.3,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
