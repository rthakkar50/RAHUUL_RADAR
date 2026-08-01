import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiConfig {
  static const String keyIp = 'api_ip';
  static const String keyPort = 'api_port';
  static const String keyEnv = 'api_env';

  static String _localIp = 'https://rahuul-radar.onrender.com';
  static String _activeIp = 'https://rahuul-radar.onrender.com';
  static String _port = '443';
  static String _env = 'Production';

  static const int timeoutSeconds = 60;
  static const int healthTimeoutSeconds = 8;

  // Candidate endpoints for multi-network auto-failover (Production Cloud, Localtunnel, Local Fallback)
  static final List<String> _candidateIps = [
    'https://rahuul-radar.onrender.com',
    'odd-vans-shave.loca.lt',
    '140.238.161.80',
    '10.0.2.2',
    '127.0.0.1'
  ];
  static List<String> get candidateIps => _candidateIps;

  static Map<String, String> defaultHeaders({Map<String, String>? extraHeaders}) {
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
    _port = prefs.getString(keyPort) ?? '443';
    _env = prefs.getString(keyEnv) ?? 'Production';
    _activeIp = _localIp;

    // Trigger instant parallel multi-network auto-discovery in background
    unawaited(autoDiscoverReachableServer());
  }

  static Future<String> autoDiscoverReachableServer() async {
    final candidates = [
      _localIp,
      'https://rahuul-radar.onrender.com',
      'odd-vans-shave.loca.lt',
      '140.238.161.80',
      '10.0.2.2',
      '127.0.0.1'
    ].where((ip) => ip.trim().isNotEmpty).toSet().toList();

    final completer = Completer<String>();

    for (final ip in candidates) {
      unawaited(() async {
        try {
          final isHttps = ip.startsWith('https://');
          final isTunnel = isHttps || ip.contains('loca.lt') || ip.contains('ngrok') || ip.contains('lhr.life') || ip.contains('onrender.com');
          final scheme = isTunnel ? 'https' : 'http';
          var cleanIp = ip.replaceFirst(RegExp(r'https?://'), '');
          if (cleanIp.endsWith('/')) cleanIp = cleanIp.substring(0, cleanIp.length - 1);
          final portStr = isTunnel ? '' : ':$_port';
          final uri = Uri.parse('$scheme://$cleanIp$portStr/api/v1/health');

          final response = await http.get(
            uri,
            headers: {
              'Bypass-Tunnel-Remainder': 'true',
              'User-Agent': 'FlutterApp',
              'Accept': 'application/json'
            },
          ).timeout(const Duration(milliseconds: 1800));

          if (response.statusCode == 200 && !completer.isCompleted) {
            _activeIp = ip;
            logProductionEvent('INFO', 'Auto-discovered working active server: $_activeIp');
            completer.complete(_activeIp);
          }
        } catch (_) {}
      }());
    }

    try {
      return await completer.future.timeout(const Duration(milliseconds: 2000));
    } catch (_) {
      return _activeIp;
    }
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
    final isTunnel = target.contains('loca.lt') || target.contains('ngrok') || target.contains('lhr.life') || target.contains('onrender.com');
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

  static Future<void> saveSettings(String ip, String p, String environment) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(keyIp, ip);
    await prefs.setString(keyPort, p);
    await prefs.setString(keyEnv, environment);

    _localIp = ip.trim();
    _activeIp = ip.trim();
    _port = p.trim();
    _env = environment.trim();
    logProductionEvent('INFO', 'Configuration updated: IP=$_localIp, Port=$_port, Env=$_env');

    // Auto-verify reachable candidate
    unawaited(autoDiscoverReachableServer());
  }
}
