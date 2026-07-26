class DashboardDataModel {
  final String serverStatus;
  final String marketStatus;
  final String lastScanTime;
  final int totalScanned;
  final int qualifiedSignals;
  final String marketQuality;
  final bool isOnline;

  const DashboardDataModel({
    required this.serverStatus,
    required this.marketStatus,
    required this.lastScanTime,
    required this.totalScanned,
    required this.qualifiedSignals,
    required this.marketQuality,
    required this.isOnline,
  });

  factory DashboardDataModel.empty({String serverStatus = 'OFFLINE', String lastScan = 'Never', bool online = false}) {
    return DashboardDataModel(
      serverStatus: serverStatus,
      marketStatus: '🔴 CLOSED',
      lastScanTime: lastScan,
      totalScanned: 0,
      qualifiedSignals: 0,
      marketQuality: 'UNAVAILABLE',
      isOnline: online,
    );
  }
}
