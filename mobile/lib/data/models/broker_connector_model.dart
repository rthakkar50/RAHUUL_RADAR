enum BrokerType { paytmMoney, zerodhaKite, angelOne, dhan, upstox }

enum BrokerConnectionStatus { connected, disconnected, degraded, reconnecting }

class BrokerInfoModel {
  final BrokerType type;
  final String name;
  final String logoUrl;
  final bool isActive;
  final bool isDefault;
  final BrokerConnectionStatus status;
  final String apiHealth; // ONLINE, DEGRADED, OFFLINE
  final int latencyMs;
  final String tokenExpiry;
  final String lastSync;

  const BrokerInfoModel({
    required this.type,
    required this.name,
    required this.logoUrl,
    required this.isActive,
    required this.isDefault,
    required this.status,
    required this.apiHealth,
    required this.latencyMs,
    required this.tokenExpiry,
    required this.lastSync,
  });
}

class BrokerAuditLogModel {
  final String timestamp;
  final String brokerName;
  final String action; // CONNECT, DISCONNECT, ORDER, CANCEL, MODIFY, RECONNECT
  final String details;
  final String status;

  const BrokerAuditLogModel({
    required this.timestamp,
    required this.brokerName,
    required this.action,
    required this.details,
    required this.status,
  });
}
