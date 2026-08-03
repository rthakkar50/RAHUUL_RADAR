import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/scan_response_model.dart';
import '../../core/network/api_config.dart';
import '../../core/network/network_manager.dart';

class ScannerRepository {
  Future<void> _checkHealth() async {
    debugPrint(
      '[RUN-AUDIT] [ScannerRepository] Initiating NetworkManager health check for: ${NetworkManager.instance.baseUrl}',
    );

    final isHealthy = await NetworkManager.instance.checkServerHealth();

    if (!isHealthy) {
      if (NetworkManager.instance.serverType == 'Render') {
        throw Exception(
          'Starting Cloud Server... Render is waking up. Estimated wait 20–60 seconds. Retrying automatically...',
        );
      }
      throw Exception(
        'Local server not running. Please ensure backend is running or connect to the same Wi-Fi. (${NetworkManager.instance.baseUrl})',
      );
    }
  }

  Future<ScanResponseModel> getSwingScans() async {
    debugPrint('[RUN-AUDIT] [ScannerRepository] Initiating getSwingScans()');
    await _checkHealth();

    final scanUrl = '${NetworkManager.instance.baseUrl}/scanner/swing';
    debugPrint(
      '[RUN-AUDIT] [ScannerRepository] Calling URL: $scanUrl | Method: GET',
    );

    try {
      final response = await http
          .get(Uri.parse(scanUrl), headers: NetworkManager.instance.defaultHeaders())
          .timeout(
            const Duration(seconds: ApiConfig.timeoutSeconds),
            onTimeout: () {
              throw TimeoutException(
                'The scanner took too long to respond. The server might be processing heavy AI loads.',
              );
            },
          );

      debugPrint(
        '[RUN-AUDIT] [ScannerRepository] HTTP Status Code: ${response.statusCode}',
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        return ScanResponseModel.fromJson(data);
      } else {
        throw Exception(
          'Failed to load swing scans. Status: ${response.statusCode}',
        );
      }
    } on TimeoutException catch (e) {
      throw Exception(e.message);
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  Future<ScanResponseModel> getIntradayScans() async {
    debugPrint('[RUN-AUDIT] [ScannerRepository] Initiating getIntradayScans()');
    await _checkHealth();

    final scanUrl = '${NetworkManager.instance.baseUrl}/scanner/intraday';
    debugPrint(
      '[RUN-AUDIT] [ScannerRepository] Calling URL: $scanUrl | Method: GET',
    );

    try {
      final response = await http
          .get(Uri.parse(scanUrl), headers: NetworkManager.instance.defaultHeaders())
          .timeout(
            const Duration(seconds: ApiConfig.timeoutSeconds),
            onTimeout: () {
              throw TimeoutException(
                'The scanner took too long to respond. The server might be processing heavy AI loads.',
              );
            },
          );

      debugPrint(
        '[RUN-AUDIT] [ScannerRepository] HTTP Status Code: ${response.statusCode}',
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        return ScanResponseModel.fromJson(data);
      } else {
        throw Exception(
          'Failed to load intraday scans. Status: ${response.statusCode}',
        );
      }
    } on TimeoutException catch (e) {
      throw Exception(e.message);
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}
