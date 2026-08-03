import 'dart:async';
import 'network_manager.dart';

enum ServerConnectionState {
  connecting,
  checking,
  wakingServer,
  online,
  offline,
  local,
  cloud,
}

class ApiConfig {
  static const int timeoutSeconds = 60;
  static const int healthTimeoutSeconds = 8;

  static List<String> get candidateIps => NetworkManager.localWifiCandidates;

  static ServerConnectionState get connectionState {
    switch (NetworkManager.instance.state) {
      case NetworkState.connecting:
        return ServerConnectionState.connecting;
      case NetworkState.discovering:
      case NetworkState.checking:
        return ServerConnectionState.checking;
      case NetworkState.local:
        return ServerConnectionState.local;
      case NetworkState.render:
      case NetworkState.tunnel:
      case NetworkState.online:
        return ServerConnectionState.online;
      case NetworkState.offline:
      case NetworkState.error:
        return ServerConnectionState.offline;
    }
  }

  static int get lastLatencyMs => NetworkManager.instance.latencyMs;
  static DateTime? get lastPingTime => NetworkManager.instance.lastPingTime;
  static String get serverVersion => NetworkManager.instance.serverVersion;
  static String get pythonVersion => NetworkManager.instance.pythonVersion;
  static String get marketStatus => NetworkManager.instance.marketStatus;
  static String get statusMessage => 'Connected to ${NetworkManager.instance.serverType} server (${NetworkManager.instance.latencyMs} ms)';

  static String get serverType => NetworkManager.instance.serverType;
  static String get localIp => NetworkManager.instance.userSavedUrl;
  static String get activeIp => NetworkManager.instance.activeUrl;
  static String get port => '8000';
  static String get env => 'Production';

  static String get baseUrl => NetworkManager.instance.baseUrl;

  static Map<String, String> defaultHeaders({Map<String, String>? extraHeaders}) {
    return NetworkManager.instance.defaultHeaders(extraHeaders: extraHeaders);
  }

  static Future<void> init() async {
    await NetworkManager.instance.init();
  }

  static Future<bool> performStagedHealthCheck({String? targetIp}) async {
    return await NetworkManager.instance.checkServerHealth(targetUrl: targetIp);
  }

  static Future<String> autoDiscoverReachableServer() async {
    return await NetworkManager.instance.startPlatformAwareDiscovery();
  }

  static Future<Map<String, dynamic>> testConnectionDetails() async {
    final diagData = await NetworkManager.instance.runFullDiagnostics();
    return {
      'resolvedUrl': diagData['currentUrl'],
      'latencyMs': diagData['latencyMs'],
      'httpStatus': diagData['httpStatus'],
      'apiVersion': diagData['serverVersion'] ?? '1.0.0',
      'serverName': diagData['serverType'],
      'pythonVersion': diagData['pythonVersion'],
      'scannerStatus': 'OPERATIONAL',
      'diagnostics': diagData['diagnostics'],
    };
  }

  static bool validateConfig() => true;

  static void logProductionEvent(String level, String message) {
    NetworkManager.instance.logEvent(level, message);
  }

  static Future<void> saveSettings(String ip, String p, String environment) async {
    await NetworkManager.instance.saveUserSettings(ip, p, environment);
  }
}
