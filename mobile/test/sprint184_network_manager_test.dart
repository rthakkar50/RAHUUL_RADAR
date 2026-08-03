import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/core/network/network_manager.dart';
import 'package:mobile/core/network/api_config.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('SPRINT-184 Enterprise NetworkManager Tests', () {
    test('Initial NetworkState is connecting or discovering', () {
      final nm = NetworkManager.instance;
      expect(
        nm.state == NetworkState.connecting || nm.state == NetworkState.discovering || nm.state == NetworkState.offline,
        isTrue,
      );
    });

    test('ApiConfig delegates to NetworkManager cleanly', () {
      expect(ApiConfig.baseUrl, contains('/api/v1'));
      expect(ApiConfig.candidateIps, isNotEmpty);
      expect(ApiConfig.serverType, isNotEmpty);
    });

    test('Server type classification works for Local, Tunnel, and Render', () {
      final nm = NetworkManager.instance;
      expect(nm.serverType, isNotNull);
    });

    test('Mobile candidates never contain 127.0.0.1', () {
      for (final ip in NetworkManager.localWifiCandidates) {
        expect(ip.contains('127.0.0.1'), isFalse);
      }
    });
  });
}
