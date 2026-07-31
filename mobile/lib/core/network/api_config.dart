import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiConfig {
  static const String keyIp = 'api_ip';
  static const String keyPort = 'api_port';
  static const String keyEnv = 'api_env';

  static String _localIp = '140.238.161.80';
  static String _activeIp = '140.238.161.80';
  static String _port = '8000';
  static String _env = 'Production';

  static const int timeoutSeconds = 60;
  static const int healthTimeoutSeconds = 8;

  // Candidate IP endpoints for automatic multi-network failover (Oracle Cloud, Local Wi-Fi, Cloud Tunnel, Localhost)
  static final List<String> _candidateIps = [
    '140.238.161.80',
    '192.168.29.57',
    'odd-vans-shave.loca.lt',
    '10.0.2.2',
    '127.0.0.1'
  ];

  static Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _localIp = prefs.getString(keyIp) ?? '140.238.161.80';
    _port = prefs.getString(keyPort) ?? '8000';
    _env = prefs.getString(keyEnv) ?? 'Production';
    _activeIp = _localIp;

    // Trigger silent multi-network auto-discovery in background
    unawaited(autoDiscoverReachableServer());
  }

  static Future<String> autoDiscoverReachableServer() async {
    final candidates = [_localIp, ..._candidateIps.where((ip) => ip != _localIp)];

    for (final ip in candidates) {
      try {
        final isTunnel = ip.contains('loca.lt') || ip.contains('ngrok');
        final scheme = isTunnel ? 'https' : 'http';
        final portStr = isTunnel ? '' : ':$_port';
        final uri = Uri.parse('$scheme://$ip$portStr/api/v1/health');
        
        final response = await http.get(
          uri, 
          headers: {'Bypass-Tunnel-Remainder': 'true', 'User-Agent': 'FlutterApp'}
        ).timeout(const Duration(seconds: 2));
        
        if (response.statusCode == 200) {
          _activeIp = ip;
          logProductionEvent('INFO', 'Auto-discovered active server IP: $_activeIp');
          return _activeIp;
        }
      } catch (_) {}
    }
    return _activeIp;
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
    final scheme = (target.contains('loca.lt') || target.contains('ngrok')) ? 'https' : 'http';
    final portStr = (target.contains('loca.lt') || target.contains('ngrok')) ? '' : ':$_port';
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
