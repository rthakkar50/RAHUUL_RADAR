import 'package:flutter/foundation.dart';
import '../../data/models/scan_result_model.dart';

class PaytmFundsModel {
  final double availableCash;
  final double usedMargin;
  final double buyingPower;
  final double collateral;

  PaytmFundsModel({
    required this.availableCash,
    required this.usedMargin,
    required this.buyingPower,
    required this.collateral,
  });
}

class PaytmHoldingModel {
  final String symbol;
  final int quantity;
  final double averagePrice;
  final double currentPrice;
  final double pnl;
  final double dayChangePct;

  PaytmHoldingModel({
    required this.symbol,
    required this.quantity,
    required this.averagePrice,
    required this.currentPrice,
    required this.pnl,
    required this.dayChangePct,
  });
}

class PaytmOrderPreviewModel {
  final String symbol;
  final String exchange;
  final String product; // CNC, MIS, MTF
  final String orderType; // LIMIT, MARKET, SL-M
  final String side; // BUY, SELL
  final int quantity;
  final double price;
  final double stopLoss;
  final double target;
  final double requiredMargin;
  final double estimatedCharges;
  final double maxExpectedRisk;

  PaytmOrderPreviewModel({
    required this.symbol,
    required this.exchange,
    required this.product,
    required this.orderType,
    required this.side,
    required this.quantity,
    required this.price,
    required this.stopLoss,
    required this.target,
    required this.requiredMargin,
    required this.estimatedCharges,
    required this.maxExpectedRisk,
  });
}

class PaytmBrokerAdapter extends ChangeNotifier {
  static final PaytmBrokerAdapter _instance = PaytmBrokerAdapter._internal();
  static PaytmBrokerAdapter get instance => _instance;

  PaytmBrokerAdapter._internal();

  bool isConnected = true;
  String tokenExpiry = '23:59 IST';
  String healthStatus = '🟢 HEALTHY - READ ONLY';

  Future<PaytmFundsModel> fetchFunds() async {
    return PaytmFundsModel(
      availableCash: 75000.0,
      usedMargin: 25000.0,
      buyingPower: 150000.0,
      collateral: 0.0,
    );
  }

  Future<List<PaytmHoldingModel>> fetchHoldings() async {
    return [
      PaytmHoldingModel(
        symbol: 'RELIANCE.NS',
        quantity: 15,
        averagePrice: 2420.0,
        currentPrice: 2500.0,
        pnl: 1200.0,
        dayChangePct: 1.8,
      ),
      PaytmHoldingModel(
        symbol: 'INFY.NS',
        quantity: 25,
        averagePrice: 1440.0,
        currentPrice: 1480.0,
        pnl: 1000.0,
        dayChangePct: 1.2,
      ),
    ];
  }

  Future<List<Map<String, dynamic>>> fetchPositions() async {
    return [
      {
        'symbol': 'TVSMOTOR.NS',
        'type': 'INTRADAY (MIS)',
        'qty': 10,
        'entry': 1980.0,
        'cmp': 2000.0,
        'pnl': 200.0,
      }
    ];
  }

  Future<List<Map<String, dynamic>>> fetchOrders() async {
    return [
      {
        'order_id': 'ORD_PAYTM_9921',
        'symbol': 'RELIANCE.NS',
        'side': 'BUY',
        'qty': 15,
        'price': 2420.0,
        'status': 'COMPLETED',
        'time': '09:32 AM',
      }
    ];
  }

  PaytmOrderPreviewModel generateOrderPreview({
    required ScanResultModel item,
    required int quantity,
  }) {
    final side = item.signal.toUpperCase().contains('SELL') ? 'SELL' : 'BUY';
    final product = item.signal.toUpperCase().contains('INTRADAY') ? 'MIS' : 'CNC';
    final reqMargin = item.entry * quantity;
    final estimatedBrokerage = 20.0;
    final estimatedStt = reqMargin * 0.001;
    final charges = estimatedBrokerage + estimatedStt + 5.50;
    final maxRisk = (item.entry - item.stopLoss).abs() * quantity;

    return PaytmOrderPreviewModel(
      symbol: item.symbol,
      exchange: 'NSE',
      product: product,
      orderType: 'LIMIT',
      side: side,
      quantity: quantity,
      price: item.entry,
      stopLoss: item.stopLoss,
      target: item.target1,
      requiredMargin: reqMargin,
      estimatedCharges: charges,
      maxExpectedRisk: maxRisk,
    );
  }
}
