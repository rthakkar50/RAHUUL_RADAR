import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/scan_response_model.dart';
import '../../core/network/api_config.dart';

class ScannerRepository {
  Future<void> _checkHealth() async {
    final healthUrl = '${ApiConfig.baseUrl}/health';
    debugPrint('[RUN-AUDIT] [ScannerRepository] Checking health URL: $healthUrl');
    debugPrint('[RUN-AUDIT] [ScannerRepository] Timeout: ${ApiConfig.healthTimeoutSeconds}s');
    try {
      final response = await http.get(
        Uri.parse(healthUrl),
        headers: ApiConfig.defaultHeaders(),
      ).timeout(const Duration(seconds: ApiConfig.healthTimeoutSeconds));
      
      debugPrint('[RUN-AUDIT] [ScannerRepository] Health check HTTP Status: ${response.statusCode}');
      debugPrint('[RUN-AUDIT] [ScannerRepository] Health check Response Body: ${response.body}');

      if (response.statusCode != 200) {
        throw Exception('Server health check failed with status: ${response.statusCode}');
      }
    } catch (e, st) {
      debugPrint('[RUN-AUDIT] [ScannerRepository] Health Check EXCEPTION: $e');
      debugPrint('[RUN-AUDIT] [ScannerRepository] Health Check STACKTRACE:\n$st');
      throw Exception('Server is unreachable. Please check your API Settings or Network connection. (${ApiConfig.baseUrl})');
    }
  }

  Future<ScanResponseModel> getSwingScans() async {
    debugPrint('[RUN-AUDIT] [ScannerRepository] Initiating getSwingScans()');
    await _checkHealth();

    final scanUrl = '${ApiConfig.baseUrl}/scanner/swing';
    debugPrint('[RUN-AUDIT] [ScannerRepository] Calling URL: $scanUrl | Method: GET');
    debugPrint('[RUN-AUDIT] [ScannerRepository] Timeout: ${ApiConfig.timeoutSeconds}s');

    try {
      final response = await http.get(
        Uri.parse(scanUrl),
        headers: ApiConfig.defaultHeaders(),
      ).timeout(
        const Duration(seconds: ApiConfig.timeoutSeconds),
        onTimeout: () {
          throw TimeoutException('The scanner took too long to respond. The server might be processing heavy AI loads.');
        },
      );

      debugPrint('[RUN-AUDIT] [ScannerRepository] HTTP Status Code: ${response.statusCode}');
      debugPrint('[RUN-AUDIT] [ScannerRepository] Response Headers: ${response.headers}');
      debugPrint('[RUN-AUDIT] [ScannerRepository] Response Body (first 300 chars): ${response.body.length > 300 ? response.body.substring(0, 300) : response.body}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        debugPrint('[RUN-AUDIT] [ScannerRepository] Decoded JSON successfully. Key count: ${data.keys.length}');
        return ScanResponseModel.fromJson(data);
      } else {
        throw Exception('Failed to load swing scans. Status: ${response.statusCode}');
      }
    } on TimeoutException catch (e, st) {
      debugPrint('[RUN-AUDIT] [ScannerRepository] TimeoutException caught: ${e.message}');
      debugPrint('[RUN-AUDIT] [ScannerRepository] STACKTRACE:\n$st');
      throw Exception(e.message);
    } catch (e, st) {
      debugPrint('[RUN-AUDIT] [ScannerRepository] EXCEPTION CAUGHT: $e');
      debugPrint('[RUN-AUDIT] [ScannerRepository] STACKTRACE:\n$st');
      throw Exception('Network error: $e');
    }
  }
}
