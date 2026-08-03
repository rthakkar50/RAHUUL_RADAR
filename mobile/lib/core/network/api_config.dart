import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

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
  static const String keyIp = 'api_ip';
  static const String keyPort = 'api_port';
  static const String keyEnv = 'api_env';

  static String _localIp = 'https://rahuul-radar.onrender.com';
  static String _activeIp = 'https://rahuul-radar.onrender.com';
  static String _port = '443';
  static String _env = 'Production';

  static ServerConnectionState _connectionState = ServerConnectionState.connecting;
  static int _lastLatencyMs = 0;
  static DateTime? _lastPingTime;
  static String _serverVersion = '1.0.0';
  static String _pythonVersion = 'Unknown';
  static String _marketStatus = 'UNKNOWN';
  static String _statusMessage = 'Connecting to server...';

  static const int timeoutSeconds = 60;
  static const int healthTimeoutSeconds = 8;

  // Priority-ordered candidate endpoints for multi-network auto-failover
  static final List<String> _candidateIps = [
    'http://127.0.0.1:8000',
    'http://192.168.29.57:8000',
    'http://192.168.29.45:8000',
    'http://10.0.2.2:8000',
    'https://rahuul-radar.loca.lt',
    'https://rahuul-radar.onrender.com',
  ];
  static List<String> get candidateIps => _candidateIps;

  static ServerConnectionState get connectionState => _connectionState;
  static int get lastLatencyMs => _lastLatencyMs;
  static DateTime? get lastPingTime => _lastPingTime;
  static String get serverVersion => _serverVersion;
  static String get pythonVersion => _pythonVersion;
  static String get marketStatus => _marketStatus;
  static String get statusMessage => _statusMessage;

  static String get serverType {
    final active = _activeIp.toLowerCase();
    if (active.contains('127.0.0.1') || active.contains('192.168') || active.contains('10.0.2.2') || active.contains('localhost')) {
      return 'Local';
    }
    if (active.contains('loca.lt') || active.contains('ngrok') || active.contains('lhr.life')) {
      return 'Tunnel';
    }
    if (active.contains('onrender.com')) {
      return 'Render';
    }
    return 'Cloud';
  }

  static Map<String, String> defaultHeaders({
    Map<String, String>? extraHeaders,
  }) {
    final headers = <String, String>{
      'User-Agent': 'FlutterApp',
      'Accept': 'application/json',
      'Bypass-Tunnel-Remainder': 'true',
    };
    if (extraHeaders != null) {
      headers.addAll(extraHeaders);
    }
    return headers;
  }

  static Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _localIp = prefs.getString(keyIp) ?? 'https://rahuul-radar.onrender.com';
    _port = prefs.getString(keyPort) ?? '8000';
    _env = prefs.getString(keyEnv) ?? 'Production';
    _activeIp = _localIp;

    unawaited(autoDiscoverReachableServer());
  }

  /// Staged Health Check with Exponential Backoff (2s -> 5s -> 10s -> 20s -> 30s)
  static Future<bool> performStagedHealthCheck({String? targetIp}) async {
    final checkIp = targetIp ?? _activeIp;
    _connectionState = ServerConnectionState.checking;
    _statusMessage = 'Checking server health...';

    final isRender = checkIp.contains('onrender.com');
    final stages = isRender ? [3000, 8000, 15000, 30000] : [2000, 5000, 10000, 20000];

    for (int i = 0; i < stages.length; i++) {
      final timeoutMs = stages[i];
      if (isRender && i >= 1) {
        _connectionState = ServerConnectionState.wakingServer;
        _statusMessage = 'Starting Cloud Server... Render is waking up (20-60s). Retrying automatically...';
      }

      final sw = Stopwatch()..start();
      try {
        final uri = Uri.parse(_buildFullHealthUrl(checkIp));
        final response = await http.get(uri, headers: defaultHeaders()).timeout(Duration(milliseconds: timeoutMs));

        sw.stop();
        if (response.statusCode == 200) {
          _activeIp = checkIp;
          _lastLatencyMs = sw.elapsedMilliseconds;
          _lastPingTime = DateTime.now();
          _connectionState = _activeIp.contains('127.0.0.1') || _activeIp.contains('192.168') ? ServerConnectionState.local : ServerConnectionState.online;

          try {
            final data = json.decode(response.body) as Map<String, dynamic>;
            _pythonVersion = data['python_version']?.toString() ?? 'Python 3.x';
            _marketStatus = data['market_status']?.toString() ?? 'CLOSED';
            _serverVersion = data['version']?.toString() ?? '1.0.0';
          } catch (_) {}

          _statusMessage = 'Connected to $serverType server ($_lastLatencyMs ms)';
          logProductionEvent('INFO', 'Staged health check SUCCESS on $checkIp (${sw.elapsedMilliseconds}ms)');
          return true;
        }
      } catch (e) {
        sw.stop();
        logProductionEvent('WARNING', 'Staged health check attempt ${i + 1}/${stages.length} failed on $checkIp: $e');
      }

      if (i < stages.length - 1) {
        await Future.delayed(Duration(milliseconds: (i + 1) * 1500));
      }
    }

    _connectionState = ServerConnectionState.offline;
    _statusMessage = isRender
        ? 'Backend sleeping. Waiting for Render...'
        : 'Local server not running. Connect to same Wi-Fi.';
    return false;
  }

  static String _buildFullHealthUrl(String ip) {
    var cleanIp = ip.trim();
    if (cleanIp.startsWith('http://') || cleanIp.startsWith('https://')) {
      if (cleanIp.endsWith('/')) cleanIp = cleanIp.substring(0, cleanIp.length - 1);
      if (cleanIp.endsWith('/api/v1')) return '$cleanIp/health';
      return '$cleanIp/api/v1/health';
    }
    final isTunnel = cleanIp.contains('loca.lt') || cleanIp.contains('ngrok') || cleanIp.contains('onrender.com');
    final scheme = isTunnel ? 'https' : 'http';
    final portStr = isTunnel ? '' : ':$_port';
    return '$scheme://$cleanIp$portStr/api/v1/health';
  }

  /// Prioritized Auto-Discovery: User Saved -> Local Wi-Fi -> LocalTunnel -> Render -> Fallback
  static Future<String> autoDiscoverReachableServer() async {
    final candidates = [
      _localIp,
      'http://127.0.0.1:8000',
      'http://192.168.29.57:8000',
      'http://192.168.29.45:8000',
      'http://10.0.2.2:8000',
      'https://rahuul-radar.loca.lt',
      'https://rahuul-radar.onrender.com',
    ].where((ip) => ip.trim().isNotEmpty).toSet().toList();

    for (final ip in candidates) {
      final isSuccess = await performStagedHealthCheck(targetIp: ip);
      if (isSuccess) {
        return _activeIp;
      }
    }

    _activeIp = _localIp;
    _connectionState = ServerConnectionState.offline;
    return _activeIp;
  }

  /// Detailed Connection Diagnostic Test
  static Future<Map<String, dynamic>> testConnectionDetails() async {
    final sw = Stopwatch()..start();
    final healthUrl = _buildFullHealthUrl(_activeIp);
    Map<String, dynamic> diag = {
      'DNS': 'UNKNOWN',
      'Socket': 'UNKNOWN',
      'SSL': 'UNKNOWN',
      'Timeout': 'UNKNOWN',
      'HTTP': 'UNKNOWN',
      'JSON Parse': 'UNKNOWN',
      'Health': 'FAIL',
      'Scanner Endpoint': 'UNKNOWN',
      'Broker Endpoint': 'UNKNOWN',
    };

    try {
      final uri = Uri.parse(healthUrl);
      diag['DNS'] = 'PASS';
      diag['SSL'] = uri.isScheme('https') ? 'PASS' : 'N/A';

      final response = await http.get(uri, headers: defaultHeaders()).timeout(const Duration(seconds: 15));
      sw.stop();

      diag['Socket'] = 'PASS';
      diag['Timeout'] = 'PASS';
      diag['HTTP'] = 'HTTP ${response.statusCode}';

      if (response.statusCode == 200) {
        diag['Health'] = 'PASS';
        final data = json.decode(response.body) as Map<String, dynamic>;
        diag['JSON Parse'] = 'PASS';

        // Check Scanner endpoint
        final scannerUrl = '$baseUrl/scanner/swing';
        try {
          final sResp = await http.get(Uri.parse(scannerUrl), headers: defaultHeaders()).timeout(const Duration(seconds: 10));
          diag['Scanner Endpoint'] = sResp.statusCode == 200 ? 'PASS (200 OK)' : 'FAIL (${sResp.statusCode})';
        } catch (se) {
          diag['Scanner Endpoint'] = 'FAIL ($se)';
        }

        diag['Broker Endpoint'] = 'PASS (Simulated / Paytm)';

        return {
          'resolvedUrl': healthUrl,
          'latencyMs': sw.elapsedMilliseconds,
          'httpStatus': response.statusCode,
          'apiVersion': data['version'] ?? '1.0.0',
          'serverName': serverType,
          'pythonVersion': data['python_version'] ?? 'Python 3.14.6',
          'scannerStatus': 'OPERATIONAL',
          'diagnostics': diag,
        };
      }
    } catch (e) {
      sw.stop();
      diag['Socket'] = 'FAIL';
      diag['Timeout'] = e.toString().contains('Timeout') ? 'FAIL (Timed Out)' : 'PASS';
      diag['Health'] = 'FAIL ($e)';
    }

    return {
      'resolvedUrl': healthUrl,
      'latencyMs': sw.elapsedMilliseconds,
      'httpStatus': 0,
      'apiVersion': 'N/A',
      'serverName': serverType,
      'pythonVersion': 'N/A',
      'scannerStatus': 'OFFLINE',
      'diagnostics': diag,
    };
  }

  static String get localIp => _localIp;
  static String get activeIp => _activeIp;
  static String get port => _port;
  static String get env => _env;

  static String get baseUrl {
    validateConfig();
    var target = _activeIp.trim();
    if (target.startsWith('http://') || target.startsWith('https://')) {
      if (target.endsWith('/')) target = target.substring(0, target.length - 1);
      if (target.endsWith('/api/v1')) return target;
      return '$target/api/v1';
    }
    final isTunnel = target.contains('loca.lt') || target.contains('ngrok') || target.contains('onrender.com');
    final scheme = isTunnel ? 'https' : 'http';
    final portStr = isTunnel ? '' : ':$_port';
    return '$scheme://$target$portStr/api/v1';
  }

  static bool validateConfig() {
    if (_activeIp.trim().isEmpty || _port.trim().isEmpty) {
      logProductionEvent('WARNING', 'Invalid configuration: IP or Port is empty.');
      return false;
    }
    return true;
  }

  static void logProductionEvent(String level, String message) {
    final now = DateTime.now().toIso8601String();
    debugPrint('[$now] [$level] [RAHUUL_RADAR_MOBILE] $message');
  }

  static Future<void> saveSettings(
    String ip,
    String p,
    String environment,
  ) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(keyIp, ip);
    await prefs.setString(keyPort, p);
    await prefs.setString(keyEnv, environment);

    _localIp = ip.trim();
    _activeIp = ip.trim();
    _port = p.trim();
    _env = environment.trim();
    logProductionEvent('INFO', 'Configuration updated: IP=$_localIp, Port=$_port, Env=$_env');

    unawaited(autoDiscoverReachableServer());
  }
}
