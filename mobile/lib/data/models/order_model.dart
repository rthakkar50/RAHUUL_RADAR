class OrderPreviewModel {
  final String symbol;
  final String exchange;
  final String action;
  final String orderType;
  final String product;
  final int quantity;
  final double price;
  final double triggerPrice;
  final double tradeValue;
  final double estimatedMargin;
  final double brokerage;
  final double taxesAndCharges;
  final double totalCost;
  final String timestamp;

  OrderPreviewModel({
    required this.symbol,
    required this.exchange,
    required this.action,
    required this.orderType,
    required this.product,
    required this.quantity,
    required this.price,
    required this.triggerPrice,
    required this.tradeValue,
    required this.estimatedMargin,
    required this.brokerage,
    required this.taxesAndCharges,
    required this.totalCost,
    required this.timestamp,
  });

  factory OrderPreviewModel.fromJson(Map<String, dynamic> json) {
    return OrderPreviewModel(
      symbol: json['symbol'] ?? '',
      exchange: json['exchange'] ?? 'NSE',
      action: json['action'] ?? 'BUY',
      orderType: json['order_type'] ?? 'MARKET',
      product: json['product'] ?? 'INTRADAY',
      quantity: (json['quantity'] ?? 0) as int,
      price: (json['price'] ?? 0.0).toDouble(),
      triggerPrice: (json['trigger_price'] ?? 0.0).toDouble(),
      tradeValue: (json['trade_value'] ?? 0.0).toDouble(),
      estimatedMargin: (json['estimated_margin'] ?? 0.0).toDouble(),
      brokerage: (json['brokerage'] ?? 0.0).toDouble(),
      taxesAndCharges: (json['taxes_and_charges'] ?? 0.0).toDouble(),
      totalCost: (json['total_cost'] ?? 0.0).toDouble(),
      timestamp: json['timestamp'] ?? '',
    );
  }
}

class OrderExecutionResultModel {
  final bool success;
  final String orderId;
  final String status;
  final String symbol;
  final String action;
  final int quantity;
  final double price;
  final String auditId;
  final double latencyMs;
  final String timestamp;

  OrderExecutionResultModel({
    required this.success,
    required this.orderId,
    required this.status,
    required this.symbol,
    required this.action,
    required this.quantity,
    required this.price,
    required this.auditId,
    required this.latencyMs,
    required this.timestamp,
  });

  factory OrderExecutionResultModel.fromJson(Map<String, dynamic> json) {
    return OrderExecutionResultModel(
      success: json['success'] ?? false,
      orderId: json['order_id'] ?? '',
      status: json['status'] ?? 'OPEN',
      symbol: json['symbol'] ?? '',
      action: json['action'] ?? '',
      quantity: (json['quantity'] ?? 0) as int,
      price: (json['price'] ?? 0.0).toDouble(),
      auditId: json['audit_id'] ?? '',
      latencyMs: (json['latency_ms'] ?? 0.0).toDouble(),
      timestamp: json['timestamp'] ?? '',
    );
  }
}

class OrderBookItemModel {
  final String orderId;
  final String symbol;
  final int quantity;
  final String orderType;
  final double price;
  final double triggerPrice;
  final String status;
  final String timestamp;

  OrderBookItemModel({
    required this.orderId,
    required this.symbol,
    required this.quantity,
    required this.orderType,
    required this.price,
    required this.triggerPrice,
    required this.status,
    required this.timestamp,
  });

  factory OrderBookItemModel.fromJson(Map<String, dynamic> json) {
    return OrderBookItemModel(
      orderId: json['order_id'] ?? '',
      symbol: json['symbol'] ?? '',
      quantity: (json['quantity'] ?? 0) as int,
      orderType: json['order_type'] ?? 'MARKET',
      price: (json['price'] ?? 0.0).toDouble(),
      triggerPrice: (json['trigger_price'] ?? 0.0).toDouble(),
      status: json['status'] ?? 'PENDING',
      timestamp: json['timestamp'] ?? '',
    );
  }
}
