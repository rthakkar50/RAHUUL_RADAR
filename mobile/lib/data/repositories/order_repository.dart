import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../core/network/api_config.dart';
import '../models/order_model.dart';

class TradeBookItemModel {
  final String tradeNo;
  final String orderNo;
  final String symbol;
  final String txnType;
  final int quantity;
  final double tradePrice;
  final String tradeTime;

  TradeBookItemModel({
    required this.tradeNo,
    required this.orderNo,
    required this.symbol,
    required this.txnType,
    required this.quantity,
    required this.tradePrice,
    required this.tradeTime,
  });

  factory TradeBookItemModel.fromJson(Map<String, dynamic> json) {
    return TradeBookItemModel(
      tradeNo: json['trade_no']?.toString() ?? '',
      orderNo: json['order_no']?.toString() ?? '',
      symbol: json['symbol']?.toString() ?? '',
      txnType: json['txn_type']?.toString() ?? 'BUY',
      quantity: (json['quantity'] as num?)?.toInt() ?? 0,
      tradePrice: (json['trade_price'] as num?)?.toDouble() ?? 0.0,
      tradeTime: json['trade_time']?.toString() ?? '',
    );
  }
}

class TradeBookResponseModel {
  final List<TradeBookItemModel> trades;
  final bool brokerConnected;
  final String status;
  final String providerHealth;
  final String? message;

  TradeBookResponseModel({
    required this.trades,
    required this.brokerConnected,
    required this.status,
    required this.providerHealth,
    this.message,
  });

  bool get isBrokerUnconfigured => status == 'BROKER_UNCONFIGURED';
  bool get isBrokerAuthError => status == 'BROKER_AUTH_ERROR';
  bool get isBrokerError => !brokerConnected || status != 'OK';

  factory TradeBookResponseModel.fromJson(Map<String, dynamic> json) {
    final List list = (json['trades'] as List?) ?? const [];
    final statusStr = json['status']?.toString() ?? 'OK';
    final connected = json['broker_connected'] as bool? ?? (statusStr == 'OK');
    return TradeBookResponseModel(
      trades: list
          .whereType<Map<String, dynamic>>()
          .map(TradeBookItemModel.fromJson)
          .toList(),
      brokerConnected: connected,
      status: statusStr,
      providerHealth: json['provider_health']?.toString() ??
          (connected ? 'HEALTHY' : 'DEGRADED'),
      message: json['message']?.toString(),
    );
  }
}

class OrderRepository {
  final http.Client? client;

  OrderRepository({this.client});

  Future<http.Response> _get(Uri url, {Map<String, String>? headers}) {
    final c = client;
    if (c != null) {
      return c.get(url, headers: headers);
    }
    return http.get(url, headers: headers);
  }

  Future<http.Response> _post(
    Uri url, {
    Map<String, String>? headers,
    Object? body,
  }) {
    final c = client;
    if (c != null) {
      return c.post(url, headers: headers, body: body);
    }
    return http.post(url, headers: headers, body: body);
  }

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
    final url = Uri.parse('$baseUrl/orders/preview');

    final body = jsonEncode({
      'symbol': symbol,
      'action': action,
      'quantity': quantity,
      'order_type': orderType,
      'price': price,
      'trigger_price': triggerPrice,
      'product': product,
    });

    final response = await _post(
          url,
          headers: ApiConfig.defaultHeaders(
            extraHeaders: {'Content-Type': 'application/json'},
          ),
          body: body,
        )
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
    final url = Uri.parse('$baseUrl/orders/execute');

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

    final response = await _post(
          url,
          headers: ApiConfig.defaultHeaders(
            extraHeaders: {'Content-Type': 'application/json'},
          ),
          body: body,
        )
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
    final url = Uri.parse('$baseUrl/orders/book');

    final response = await _get(url, headers: ApiConfig.defaultHeaders())
        .timeout(Duration(seconds: ApiConfig.timeoutSeconds));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List list = data['orders'] ?? [];
      return list.map((item) => OrderBookItemModel.fromJson(item)).toList();
    } else {
      throw Exception('Failed to fetch order book: ${response.body}');
    }
  }

  Future<TradeBookResponseModel> fetchTradeBook() async {
    final baseUrl = ApiConfig.baseUrl;
    final url = Uri.parse('$baseUrl/orders/trades');

    final response = await _get(url, headers: ApiConfig.defaultHeaders())
        .timeout(Duration(seconds: ApiConfig.timeoutSeconds));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return TradeBookResponseModel.fromJson(data);
    } else {
      throw Exception('Failed to fetch trade book: ${response.body}');
    }
  }

  Future<bool> cancelOrder(String orderId) async {
    final baseUrl = ApiConfig.baseUrl;
    final url = Uri.parse('$baseUrl/orders/cancel/$orderId');

    final response = await _post(url, headers: ApiConfig.defaultHeaders())
        .timeout(Duration(seconds: ApiConfig.timeoutSeconds));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['success'] ?? false;
    } else {
      throw Exception('Failed to cancel order: ${response.body}');
    }
  }
}
