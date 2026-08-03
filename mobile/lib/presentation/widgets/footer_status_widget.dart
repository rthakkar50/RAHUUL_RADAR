import 'package:flutter/material.dart';
import '../../core/network/network_manager.dart';

class FooterStatusWidget extends StatelessWidget {
  const FooterStatusWidget({super.key});

  @override
  Widget build(BuildContext context) {
    final nm = NetworkManager.instance;
    final isOnline = nm.state != NetworkState.offline && nm.state != NetworkState.error;
    final statusColor = isOnline ? Colors.greenAccent : Colors.redAccent;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      color: const Color(0xFF0B0E14),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Flexible(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: statusColor,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
                const Flexible(
                  child: Text(
                    'Provider: Paytm Money (Live)',
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(color: Colors.grey, fontSize: 10),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              'Status: ${nm.marketStatus} • Latency: ${nm.latencyMs}ms • v6.7.0',
              overflow: TextOverflow.ellipsis,
              textAlign: TextAlign.right,
              style: const TextStyle(color: Colors.white70, fontSize: 10),
            ),
          ),
        ],
      ),
    );
  }
}
