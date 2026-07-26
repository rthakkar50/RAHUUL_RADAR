import 'package:shared_preferences/shared_preferences.dart';

class ApiConfig {
  static const String keyIp = 'api_ip';
  static const String keyPort = 'api_port';
  static const String keyEnv = 'api_env';

  static String _localIp = '137.23.34.223'; // Default to Production API
  static String _port = '8000';
  static String _env = 'Production';

  static const int timeoutSeconds = 60; // Scanner can take a few seconds
  static const int healthTimeoutSeconds = 3; // Fast fail for health check

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
    return 'http://$_localIp:$_port/api/v1';
  }

  static Future<void> saveSettings(String ip, String p, String environment) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(keyIp, ip);
    await prefs.setString(keyPort, p);
    await prefs.setString(keyEnv, environment);
    
    _localIp = ip;
    _port = p;
    _env = environment;
  }
}
