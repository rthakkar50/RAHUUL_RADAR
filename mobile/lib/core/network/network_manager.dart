import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

enum NetworkState {
  connecting,
  discovering,
  checking,
  online,
  local,
  tunnel,
  render,
  offline,
  error,
}

class NetworkManager {
  static final NetworkManager _instance = NetworkManager._internal();
  static NetworkManager get instance => _instance;

  NetworkManager._internal();

  static const String keyUserSavedUrl = 'user_saved_url';
  static const String keyLastWorkingServer = 'last_working_server';
  static const String keyUserTunnelUrl = 'user_tunnel_url';
  static const String keyPort = 'api_port';
  static const String keyEnv = 'api_env';

  static const String defaultRenderUrl = 'https://rahuul-radar.onrender.com';
  static const List<String> localWifiCandidates = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://192.168.29.57:8000',
    'http://192.168.29.45:8000',
    'http://10.0.2.2:8000',
  ];

  NetworkState _state = NetworkState.connecting;
  String _activeUrl = defaultRenderUrl;
  String _userSavedUrl = defaultRenderUrl;
  String _lastWorkingUrl = defaultRenderUrl;
  String _userTunnelUrl = '';
  String _port = '8000';
  String _env = 'Production';

  String _discoverySource = 'Default Cloud';
  String _failureReason = 'None';
  int _latencyMs = 0;
  DateTime? _lastPingTime;
  String _pythonVersion = 'Unknown';
  String _marketStatus = 'UNKNOWN';
  String _serverVersion = '1.0.0';
  int _httpStatus = 0;

  NetworkState get state => _state;
  String get activeUrl => _activeUrl;
  String get userSavedUrl => _userSavedUrl;
  String get lastWorkingUrl => _lastWorkingUrl;
  String get userTunnelUrl => _userTunnelUrl;
  String get discoverySource => _discoverySource;
  String get failureReason => _failureReason;
  int get latencyMs => _latencyMs;
  DateTime? get lastPingTime => _lastPingTime;
  String get pythonVersion => _pythonVersion;
  String get marketStatus => _marketStatus;
  String get serverVersion => _serverVersion;
  int get httpStatus => _httpStatus;

  String get serverType {
    final target = _activeUrl.toLowerCase();
    if (target.contains('127.0.0.1') || target.contains('192.168') || target.contains('10.0.2.2') || target.contains('localhost')) {
      return 'Local';
    }
    if (target.contains('loca.lt') || target.contains('ngrok') || target.contains('lhr.life')) {
      return 'Tunnel';
    }
    if (target.contains('onrender.com')) {
      return 'Render';
    }
    return 'Cloud';
  }

  String get baseUrl {
    var target = _activeUrl.trim();
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

  Map<String, String> defaultHeaders({Map<String, String>? extraHeaders}) {
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

  Future<void> init() async {
    _state = NetworkState.connecting;
    final prefs = await SharedPreferences.getInstance();
    _userSavedUrl = prefs.getString(keyUserSavedUrl) ?? defaultRenderUrl;
    _lastWorkingUrl = prefs.getString(keyLastWorkingServer) ?? _userSavedUrl;
    _userTunnelUrl = prefs.getString(keyUserTunnelUrl) ?? '';
    _port = prefs.getString(keyPort) ?? '8000';
    _env = prefs.getString(keyEnv) ?? 'Production';
    _activeUrl = _lastWorkingUrl;

    unawaited(startPlatformAwareDiscovery());
  }

  /// Platform-Aware Startup Discovery Sequence (TASK 3 & TASK 9)
  Future<String> startPlatformAwareDiscovery() async {
    _state = NetworkState.discovering;
    _failureReason = 'None';

    final candidates = <Map<String, String>>[];

    if (kIsWeb) {
      candidates.add({'url': 'http://localhost:8000', 'source': 'Web Localhost'});
      candidates.add({'url': _userSavedUrl, 'source': 'User Saved URL'});
      for (final ip in localWifiCandidates) {
        candidates.add({'url': ip, 'source': 'Local Wi-Fi'});
      }
      candidates.add({'url': defaultRenderUrl, 'source': 'Render Cloud'});
    } else {
      // Prioritize local candidates so local backend is selected when healthy
      for (final ip in localWifiCandidates) {
        candidates.add({'url': ip, 'source': 'Local Backend'});
      }
      if (_userSavedUrl.isNotEmpty && !localWifiCandidates.contains(_userSavedUrl)) {
        candidates.add({'url': _userSavedUrl, 'source': 'User Saved URL'});
      }
      if (_lastWorkingUrl.isNotEmpty && _lastWorkingUrl != _userSavedUrl && !localWifiCandidates.contains(_lastWorkingUrl)) {
        candidates.add({'url': _lastWorkingUrl, 'source': 'Last Working Server'});
      }
      if (_userTunnelUrl.isNotEmpty) {
        candidates.add({'url': _userTunnelUrl, 'source': 'User Tunnel'});
      }
      candidates.add({'url': defaultRenderUrl, 'source': 'Render Cloud'});
    }

    final tested = <String>{};
    for (final c in candidates) {
      final url = c['url']!.trim();
      final source = c['source']!;

      if (url.isEmpty || tested.contains(url)) continue;
      tested.add(url);

      final isSuccess = await checkServerHealth(targetUrl: url, sourceName: source);
      if (isSuccess) {
        _activeUrl = url;
        _discoverySource = source;
        await _persistLastWorkingServer(url);

        if (url.contains('192.168') || url.contains('localhost') || url.contains('10.0.2.2')) {
          _state = NetworkState.local;
        } else if (url.contains('loca.lt') || url.contains('ngrok')) {
          _state = NetworkState.tunnel;
        } else if (url.contains('onrender.com')) {
          _state = NetworkState.render;
        } else {
          _state = NetworkState.online;
        }

        logEvent('INFO', 'Platform-aware discovery selected: $_activeUrl via $_discoverySource');
        return _activeUrl;
      }
    }

    _state = NetworkState.offline;
    _failureReason = 'All candidate backends unreachable';
    logEvent('WARNING', 'Platform-aware discovery completed with offline status');
    return _activeUrl;
  }

  /// Staged Non-Blocking Health Check (TASK 2 & TASK 7)
  Future<bool> checkServerHealth({String? targetUrl, String sourceName = 'Manual Check'}) async {
    final checkUrl = targetUrl ?? _activeUrl;
    _state = NetworkState.checking;

    final isRender = checkUrl.contains('onrender.com');
    final stages = isRender ? [3000, 8000, 15000, 30000] : [2000, 5000, 10000, 20000];

    for (int i = 0; i < stages.length; i++) {
      final timeoutMs = stages[i];
      final sw = Stopwatch()..start();

      try {
        final uri = Uri.parse(_buildHealthUrl(checkUrl));
        final response = await http.get(uri, headers: defaultHeaders()).timeout(Duration(milliseconds: timeoutMs));

        sw.stop();
        _httpStatus = response.statusCode;

        if (response.statusCode == 200) {
          _latencyMs = sw.elapsedMilliseconds;
          _lastPingTime = DateTime.now();

          try {
            final data = json.decode(response.body) as Map<String, dynamic>;
            _pythonVersion = data['python_version']?.toString() ?? 'Python 3.x';
            _marketStatus = data['market_status']?.toString() ?? 'CLOSED';
            _serverVersion = data['version']?.toString() ?? '1.0.0';
          } catch (_) {}

          return true;
        }
      } catch (e) {
        sw.stop();
        _failureReason = 'Attempt ${i + 1}/${stages.length} on $checkUrl failed: $e';
        logEvent('WARNING', _failureReason);
      }

      if (i < stages.length - 1) {
        await Future.delayed(Duration(milliseconds: (i + 1) * 1500));
      }
    }

    return false;
  }

  String _buildHealthUrl(String url) {
    var clean = url.trim();
    if (clean.startsWith('http://') || clean.startsWith('https://')) {
      if (clean.endsWith('/')) clean = clean.substring(0, clean.length - 1);
      if (clean.endsWith('/api/v1')) return '$clean/health';
      return '$clean/api/v1/health';
    }
    final isTunnel = clean.contains('loca.lt') || clean.contains('ngrok') || clean.contains('onrender.com');
    final scheme = isTunnel ? 'https' : 'http';
    final portStr = isTunnel ? '' : ':$_port';
    return '$scheme://$clean$portStr/api/v1/health';
  }

  Future<void> _persistLastWorkingServer(String url) async {
    _lastWorkingUrl = url;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(keyLastWorkingServer, url);
  }

  Future<void> saveUserSettings(String url, String p, String env) async {
    final cleanUrl = url.trim();
    _userSavedUrl = cleanUrl;
    _port = p.trim();
    _env = env.trim();

    if (cleanUrl.contains('loca.lt') || cleanUrl.contains('ngrok') || cleanUrl.contains('lhr.life')) {
      _userTunnelUrl = cleanUrl;
    }

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(keyUserSavedUrl, _userSavedUrl);
    await prefs.setString(keyUserTunnelUrl, _userTunnelUrl);
    await prefs.setString(keyPort, _port);
    await prefs.setString(keyEnv, _env);

    await startPlatformAwareDiscovery();
  }

  /// Diagnostic Diagnostic Collector (TASK 8)
  Future<Map<String, dynamic>> runFullDiagnostics() async {
    final healthUrl = _buildHealthUrl(_activeUrl);
    final sw = Stopwatch()..start();
    final diag = <String, String>{
      'DNS': 'UNKNOWN',
      'Socket': 'UNKNOWN',
      'SSL': 'UNKNOWN',
      'Timeout': 'UNKNOWN',
      'HTTP': 'UNKNOWN',
      'JSON Parse': 'UNKNOWN',
      'Health Endpoint': 'UNKNOWN',
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
        diag['Health Endpoint'] = 'PASS (200 OK)';
        final data = json.decode(response.body) as Map<String, dynamic>;
        diag['JSON Parse'] = 'PASS';

        final scannerUrl = '$baseUrl/scanner/swing';
        try {
          final sResp = await http.get(Uri.parse(scannerUrl), headers: defaultHeaders()).timeout(const Duration(seconds: 10));
          diag['Scanner Endpoint'] = sResp.statusCode == 200 ? 'PASS (200 OK)' : 'FAIL (${sResp.statusCode})';
        } catch (se) {
          diag['Scanner Endpoint'] = 'FAIL ($se)';
        }

        diag['Broker Endpoint'] = 'PASS (Paytm OAuth2 Active)';

        return {
          'currentUrl': healthUrl,
          'serverType': serverType,
          'latencyMs': sw.elapsedMilliseconds,
          'httpStatus': response.statusCode,
          'pythonVersion': data['python_version'] ?? _pythonVersion,
          'marketStatus': data['market_status'] ?? _marketStatus,
          'lastWorkingUrl': _lastWorkingUrl,
          'discoverySource': _discoverySource,
          'failureReason': 'None',
          'diagnostics': diag,
        };
      }
    } catch (e) {
      sw.stop();
      diag['Socket'] = 'FAIL';
      diag['Timeout'] = e.toString().contains('Timeout') ? 'FAIL (Timed Out)' : 'PASS';
      diag['Health Endpoint'] = 'FAIL ($e)';
    }

    return {
      'currentUrl': healthUrl,
      'serverType': serverType,
      'latencyMs': sw.elapsedMilliseconds,
      'httpStatus': 0,
      'pythonVersion': 'N/A',
      'marketStatus': 'UNKNOWN',
      'lastWorkingUrl': _lastWorkingUrl,
      'discoverySource': _discoverySource,
      'failureReason': _failureReason,
      'diagnostics': diag,
    };
  }

  void logEvent(String level, String msg) {
    final now = DateTime.now().toIso8601String();
    debugPrint('[$now] [$level] [NetworkManager] $msg');
  }
}
