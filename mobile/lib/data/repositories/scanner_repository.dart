import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:async';
import '../models/scan_response_model.dart';
import '../../core/network/api_config.dart';

class ScannerRepository {
  Future<void> _checkHealth() async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}/health'),
      ).timeout(const Duration(seconds: ApiConfig.healthTimeoutSeconds));
      
      if (response.statusCode != 200) {
        throw Exception('Server health check failed');
      }
    } catch (e) {
      throw Exception('Server is unreachable. Please check your API Settings or Network connection. (${ApiConfig.baseUrl})');
    }
  }

  Future<ScanResponseModel> getSwingScans() async {
    await _checkHealth();

    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}/scanner/swing'),
      ).timeout(
        const Duration(seconds: ApiConfig.timeoutSeconds),
        onTimeout: () {
          throw TimeoutException('The scanner took too long to respond. The server might be processing heavy AI loads.');
        },
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        return ScanResponseModel.fromJson(data);
      } else {
        throw Exception('Failed to load swing scans. Status: ${response.statusCode}');
      }
    } on TimeoutException catch (e) {
      throw Exception(e.message);
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}
