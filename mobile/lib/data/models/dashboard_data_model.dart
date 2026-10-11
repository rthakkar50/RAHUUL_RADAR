import 'scan_result_model.dart';

class DashboardDataModel {
  final String serverStatus;
  final String marketStatus;
  final String lastScanTime;
  final String cacheAgeDisplay;
  final bool isStale;
  final String provider;
  final String providerHealth;
  final bool fallbackUsed;
  final bool paytmAuthenticated;
  final String brokerStatusLabel;
  final String actualBrokerFundsLabel;
  final String virtualRiskCapitalLabel;
  final String paperEquityLabel;
  final String paperAvailableCashLabel;
  final String paperUsedMarginLabel;
  final String paperPnlLabel;
  final String paperOpenPositionsLabel;
  final int totalScanned;
  final int qualifiedSignals;
  final String marketQuality;
  final bool isOnline;
  final List<ScanResultModel> qualifiedResults;
  final ScanResultModel? topPick;

  const DashboardDataModel({
    required this.serverStatus,
    required this.marketStatus,
    required this.lastScanTime,
    this.cacheAgeDisplay = 'UNKNOWN',
    this.isStale = true,
    this.provider = 'UNKNOWN',
    this.providerHealth = 'UNKNOWN',
    this.fallbackUsed = false,
    this.paytmAuthenticated = false,
    this.brokerStatusLabel = 'Broker: Status Unknown',
    this.actualBrokerFundsLabel = 'UNAVAILABLE',
    this.virtualRiskCapitalLabel = 'UNAVAILABLE',
    this.paperEquityLabel = 'UNAVAILABLE',
    this.paperAvailableCashLabel = 'UNAVAILABLE',
    this.paperUsedMarginLabel = 'UNAVAILABLE',
    this.paperPnlLabel = 'UNAVAILABLE',
    this.paperOpenPositionsLabel = 'UNAVAILABLE',
    required this.totalScanned,
    required this.qualifiedSignals,
    required this.marketQuality,
    required this.isOnline,
    this.qualifiedResults = const [],
    this.topPick,
  });

  factory DashboardDataModel.empty({
    String serverStatus = 'OFFLINE',
    String lastScan = 'UNAVAILABLE',
    bool online = false,
  }) {
    return DashboardDataModel(
      serverStatus: serverStatus,
      marketStatus: 'CLOSED',
      lastScanTime: lastScan,
      cacheAgeDisplay: 'UNAVAILABLE',
      isStale: true,
      provider: 'UNAVAILABLE',
      providerHealth: 'UNKNOWN',
      fallbackUsed: false,
      paytmAuthenticated: false,
      brokerStatusLabel: 'Broker: Unreachable',
      actualBrokerFundsLabel: 'UNAVAILABLE',
      virtualRiskCapitalLabel: 'UNAVAILABLE',
      paperEquityLabel: 'UNAVAILABLE',
      paperAvailableCashLabel: 'UNAVAILABLE',
      paperUsedMarginLabel: 'UNAVAILABLE',
      paperPnlLabel: 'UNAVAILABLE',
      paperOpenPositionsLabel: 'UNAVAILABLE',
      totalScanned: 0,
      qualifiedSignals: 0,
      marketQuality: 'UNAVAILABLE',
      isOnline: online,
      qualifiedResults: const [],
      topPick: null,
    );
  }
}
