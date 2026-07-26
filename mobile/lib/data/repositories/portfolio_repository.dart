import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;
import '../../core/network/api_config.dart';
import '../models/portfolio_model.dart';

class PortfolioRepository {
  Future<PortfolioResponseModel> getPortfolio() async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}/portfolio'),
      ).timeout(const Duration(seconds: ApiConfig.timeoutSeconds));

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        return PortfolioResponseModel.fromJson(data);
      } else {
        throw Exception('Failed to load portfolio. Status: ${response.statusCode}');
      }
    } on TimeoutException {
      throw Exception('Portfolio request timed out. Please check server status.');
    } catch (e) {
      throw Exception('Network error fetching portfolio: $e');
    }
  }
}
