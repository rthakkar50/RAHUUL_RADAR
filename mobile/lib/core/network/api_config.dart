import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiConfig {
  static const String keyIp = 'api_ip';
  static const String keyPort = 'api_port';
  static const String keyEnv = 'api_env';

  static String _localIp = '137.23.34.223'; // Default to Production API
  static String _port = '8000';
  static String _env = 'Production';

  static const int timeoutSeconds = 60; // Scanner can take a few seconds
  static const int healthTimeoutSeconds = 8; // Resilient health check timeout

  static Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _localIp = prefs.getString(keyIp) ?? '137.23.34.223';
    _port = prefs.getString(keyPort) ?? '8000';
    _env = prefs.getString(keyEnv) ?? 'Production';
  }

  static String get localIp => _localIp;
  static String get port => _port;
  static String get env => _env;

  static String get baseUrl {
    validateConfig();
    return 'http://$_localIp:$_port/api/v1';
  }

  static bool validateConfig() {
    if (_localIp.trim().isEmpty || _port.trim().isEmpty) {
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
    _port = p.trim();
    _env = environment.trim();
    logProductionEvent('INFO', 'Configuration updated: IP=$_localIp, Port=$_port, Env=$_env');
  }
}
