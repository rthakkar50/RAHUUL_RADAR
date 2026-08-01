import 'dart:convert';
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../../core/network/api_config.dart';
import '../models/portfolio_model.dart';

class PortfolioRepository {
  Future<PortfolioResponseModel> getPortfolio() async {
    final portfolioUrl = '${ApiConfig.baseUrl}/portfolio';
    debugPrint('[RUN-AUDIT] [PortfolioRepository] Calling URL: $portfolioUrl | Method: GET');
    debugPrint('[RUN-AUDIT] [PortfolioRepository] Timeout: ${ApiConfig.timeoutSeconds}s');

    try {
      final response = await http.get(
        Uri.parse(portfolioUrl),
        headers: ApiConfig.defaultHeaders(),
      ).timeout(const Duration(seconds: ApiConfig.timeoutSeconds));

      debugPrint('[RUN-AUDIT] [PortfolioRepository] HTTP Status Code: ${response.statusCode}');
      debugPrint('[RUN-AUDIT] [PortfolioRepository] Response Headers: ${response.headers}');
      debugPrint('[RUN-AUDIT] [PortfolioRepository] Response Body (first 300 chars): ${response.body.length > 300 ? response.body.substring(0, 300) : response.body}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        debugPrint('[RUN-AUDIT] [PortfolioRepository] Decoded JSON successfully. Key count: ${data.keys.length}');
        return PortfolioResponseModel.fromJson(data);
      } else {
        throw Exception('Failed to load portfolio. Status: ${response.statusCode}');
      }
    } on TimeoutException catch (e, st) {
      debugPrint('[RUN-AUDIT] [PortfolioRepository] TimeoutException caught: $e');
      debugPrint('[RUN-AUDIT] [PortfolioRepository] STACKTRACE:\n$st');
      throw Exception('Portfolio request timed out. Please check server status.');
    } catch (e, st) {
      debugPrint('[RUN-AUDIT] [PortfolioRepository] EXCEPTION CAUGHT: $e');
      debugPrint('[RUN-AUDIT] [PortfolioRepository] STACKTRACE:\n$st');
      throw Exception('Network error fetching portfolio: $e');
    }
  }
}
