import 'package:flutter/foundation.dart';
import '../models/broker_connector_model.dart';

class BrokerOrchestrator {
  static final BrokerOrchestrator _instance = BrokerOrchestrator._internal();
  factory BrokerOrchestrator() => _instance;
  BrokerOrchestrator._internal();

  BrokerType _activeBroker = BrokerType.paytmMoney;
  BrokerType _secondaryBroker = BrokerType.zerodhaKite;

  final List<BrokerAuditLogModel> _auditLogs = [
    BrokerAuditLogModel(timestamp: DateTime.now().subtract(const Duration(minutes: 10)).toIso8601String(), brokerName: 'Paytm Money', action: 'CONNECT', details: 'OAuth2 Session Authorized', status: 'SUCCESS'),
    BrokerAuditLogModel(timestamp: DateTime.now().subtract(const Duration(minutes: 5)).toIso8601String(), brokerName: 'Paytm Money', action: 'HEARTBEAT', details: 'Latency 18ms', status: 'SUCCESS'),
  ];

  BrokerType get activeBroker => _activeBroker;
  BrokerType get secondaryBroker => _secondaryBroker;

  List<BrokerInfoModel> getAvailableBrokers() {
    return [
      BrokerInfoModel(
        type: BrokerType.paytmMoney,
        name: 'Paytm Money API v2',
        logoUrl: 'assets/brokers/paytm.png',
        isActive: true,
        isDefault: _activeBroker == BrokerType.paytmMoney,
        status: BrokerConnectionStatus.connected,
        apiHealth: 'ONLINE',
        latencyMs: 18,
        tokenExpiry: '24 Hours Remaining',
        lastSync: 'Just Now',
      ),
      BrokerInfoModel(
        type: BrokerType.zerodhaKite,
        name: 'Zerodha Kite Connect v3',
        logoUrl: 'assets/brokers/zerodha.png',
        isActive: false,
        isDefault: _activeBroker == BrokerType.zerodhaKite,
        status: BrokerConnectionStatus.disconnected,
        apiHealth: 'READY (INACTIVE)',
        latencyMs: 0,
        tokenExpiry: 'Not Authenticated',
        lastSync: 'N/A',
      ),
      BrokerInfoModel(
        type: BrokerType.angelOne,
        name: 'Angel One SmartAPI',
        logoUrl: 'assets/brokers/angel.png',
        isActive: false,
        isDefault: _activeBroker == BrokerType.angelOne,
        status: BrokerConnectionStatus.disconnected,
        apiHealth: 'READY (INACTIVE)',
        latencyMs: 0,
        tokenExpiry: 'Not Authenticated',
        lastSync: 'N/A',
      ),
      BrokerInfoModel(
        type: BrokerType.dhan,
        name: 'Dhan HQ API',
        logoUrl: 'assets/brokers/dhan.png',
        isActive: false,
        isDefault: _activeBroker == BrokerType.dhan,
        status: BrokerConnectionStatus.disconnected,
        apiHealth: 'READY (INACTIVE)',
        latencyMs: 0,
        tokenExpiry: 'Not Authenticated',
        lastSync: 'N/A',
      ),
      BrokerInfoModel(
        type: BrokerType.upstox,
        name: 'Upstox Developer API v2',
        logoUrl: 'assets/brokers/upstox.png',
        isActive: false,
        isDefault: _activeBroker == BrokerType.upstox,
        status: BrokerConnectionStatus.disconnected,
        apiHealth: 'READY (INACTIVE)',
        latencyMs: 0,
        tokenExpiry: 'Not Authenticated',
        lastSync: 'N/A',
      ),
    ];
  }

  List<BrokerAuditLogModel> getAuditLogs() => List.unmodifiable(_auditLogs);

  void logAction(String brokerName, String action, String details, String status) {
    _auditLogs.insert(0, BrokerAuditLogModel(
      timestamp: DateTime.now().toIso8601String(),
      brokerName: brokerName,
      action: action,
      details: details,
      status: status,
    ));
    debugPrint('[BROKER-ORCHESTRATOR] [$action] $brokerName: $details ($status)');
  }

  void switchActiveBroker(BrokerType newBroker) {
    _activeBroker = newBroker;
    logAction(newBroker.name, 'SWITCH_BROKER', 'Active broker switched to ${newBroker.name}', 'SUCCESS');
  }
}
