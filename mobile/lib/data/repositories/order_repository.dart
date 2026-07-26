import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../core/network/api_config.dart';
import '../models/order_model.dart';

class OrderRepository {
  Future<OrderPreviewModel> getOrderPreview({
    required String symbol,
    required String action,
    required int quantity,
    required String orderType,
    double price = 0.0,
    double triggerPrice = 0.0,
    String product = 'I',
  }) async {
    final baseUrl = ApiConfig.baseUrl;
    final url = Uri.parse('$baseUrl/api/v1/orders/preview');

    final body = jsonEncode({
      'symbol': symbol,
      'action': action,
      'quantity': quantity,
      'order_type': orderType,
      'price': price,
      'trigger_price': triggerPrice,
      'product': product,
    });

    final response = await http
        .post(url, headers: {'Content-Type': 'application/json'}, body: body)
        .timeout(Duration(seconds: ApiConfig.timeoutSeconds));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return OrderPreviewModel.fromJson(data);
    } else {
      final err = jsonDecode(response.body);
      throw Exception(err['detail'] ?? 'Failed to generate order preview');
    }
  }

  Future<OrderExecutionResultModel> executeOrder({
    required String symbol,
    required String action,
    required int quantity,
    required String orderType,
    double price = 0.0,
    double triggerPrice = 0.0,
    String product = 'I',
    bool confirmed = true,
  }) async {
    final baseUrl = ApiConfig.baseUrl;
    final url = Uri.parse('$baseUrl/api/v1/orders/execute');

    final body = jsonEncode({
      'symbol': symbol,
      'action': action,
      'quantity': quantity,
      'order_type': orderType,
      'price': price,
      'trigger_price': triggerPrice,
      'product': product,
      'confirmed': confirmed,
    });

    final response = await http
        .post(url, headers: {'Content-Type': 'application/json'}, body: body)
        .timeout(Duration(seconds: ApiConfig.timeoutSeconds));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return OrderExecutionResultModel.fromJson(data);
    } else {
      final err = jsonDecode(response.body);
      throw Exception(err['detail'] ?? 'Order execution rejected');
    }
  }

  Future<List<OrderBookItemModel>> fetchOrderBook() async {
    final baseUrl = ApiConfig.baseUrl;
    final url = Uri.parse('$baseUrl/api/v1/orders/book');

    final response = await http
        .get(url)
        .timeout(Duration(seconds: ApiConfig.timeoutSeconds));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List list = data['orders'] ?? [];
      return list.map((item) => OrderBookItemModel.fromJson(item)).toList();
    } else {
      throw Exception('Failed to fetch order book: ${response.body}');
    }
  }

  Future<bool> cancelOrder(String orderId) async {
    final baseUrl = ApiConfig.baseUrl;
    final url = Uri.parse('$baseUrl/api/v1/orders/cancel/$orderId');

    final response = await http
        .post(url)
        .timeout(Duration(seconds: ApiConfig.timeoutSeconds));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['success'] ?? false;
    } else {
      throw Exception('Failed to cancel order: ${response.body}');
    }
  }
}
