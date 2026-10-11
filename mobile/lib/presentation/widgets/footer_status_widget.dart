import 'package:flutter/material.dart';
import '../../core/network/network_manager.dart';

class FooterStatusWidget extends StatelessWidget {
  final String? provider;
  final String? providerHealth;
  final bool? fallbackUsed;
  final String? marketStatus;

  const FooterStatusWidget({
    super.key,
    this.provider,
    this.providerHealth,
    this.fallbackUsed,
    this.marketStatus,
  });

  @override
  Widget build(BuildContext context) {
    final nm = NetworkManager.instance;
    final isOnline = nm.state != NetworkState.offline && nm.state != NetworkState.error;
    final resolvedProvider = (provider != null && provider!.trim().isNotEmpty)
        ? provider!.trim()
        : nm.provider;
    final resolvedHealth = (providerHealth != null && providerHealth!.trim().isNotEmpty)
        ? providerHealth!.trim().toUpperCase()
        : nm.providerHealth.toUpperCase();
    final resolvedFallback = fallbackUsed ?? nm.fallbackUsed;
    final resolvedMarket = (marketStatus != null && marketStatus!.trim().isNotEmpty)
        ? marketStatus!.trim()
        : nm.marketStatus;

    Color statusColor;
    if (!isOnline) {
      statusColor = Colors.redAccent;
    } else if (resolvedFallback || resolvedHealth == 'DEGRADED' || !nm.paytmAuthenticated) {
      statusColor = Colors.amberAccent;
    } else if (resolvedHealth == 'HEALTHY') {
      statusColor = Colors.greenAccent;
    } else {
      statusColor = Colors.grey;
    }

    String providerDisplay = resolvedProvider;
    if (resolvedFallback && !providerDisplay.toLowerCase().contains('fallback')) {
      providerDisplay = '$providerDisplay (Fallback)';
    }
    if (resolvedHealth.isNotEmpty && resolvedHealth != 'UNKNOWN') {
      providerDisplay = '$providerDisplay [$resolvedHealth]';
    }

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
                Flexible(
                  child: Text(
                    'Provider: $providerDisplay',
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(color: Colors.grey, fontSize: 10),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              'Market: $resolvedMarket • Latency: ${nm.latencyMs}ms • v${nm.serverVersion}',
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
