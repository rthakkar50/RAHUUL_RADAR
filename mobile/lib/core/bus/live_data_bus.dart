import 'dart:async';

enum LiveEventType {
  marketTick,
  scannerUpdate,
  portfolioUpdate,
  orderUpdate,
  riskAlert,
  telegramSync,
}

class LiveEvent {
  final LiveEventType type;
  final String symbol;
  final Map<String, dynamic> payload;
  final DateTime timestamp;

  LiveEvent({
    required this.type,
    this.symbol = '',
    required this.payload,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}

class LiveDataBus {
  static final LiveDataBus _instance = LiveDataBus._internal();
  factory LiveDataBus() => _instance;
  LiveDataBus._internal();

  final StreamController<LiveEvent> _eventController =
      StreamController<LiveEvent>.broadcast();

  Stream<LiveEvent> get stream => _eventController.stream;

  Stream<LiveEvent> streamForType(LiveEventType type) {
    return _eventController.stream.where((event) => event.type == type);
  }

  void publish(LiveEvent event) {
    if (!_eventController.isClosed) {
      _eventController.add(event);
    }
  }

  void publishMarketTick({
    required String symbol,
    required double price,
    required double changePct,
  }) {
    publish(
      LiveEvent(
        type: LiveEventType.marketTick,
        symbol: symbol,
        payload: {'price': price, 'change_pct': changePct},
      ),
    );
  }

  void publishPortfolioUpdate({
    required double totalEquity,
    required double pnl,
    required double usedMargin,
  }) {
    publish(
      LiveEvent(
        type: LiveEventType.portfolioUpdate,
        payload: {'total_equity': totalEquity, 'pnl': pnl, 'used_margin': usedMargin},
      ),
    );
  }

  void publishOrderUpdate({
    required String orderId,
    required String symbol,
    required String status,
  }) {
    publish(
      LiveEvent(
        type: LiveEventType.orderUpdate,
        symbol: symbol,
        payload: {'order_id': orderId, 'status': status},
      ),
    );
  }

  void publishRiskAlert({
    required String level,
    required String message,
  }) {
    publish(
      LiveEvent(
        type: LiveEventType.riskAlert,
        payload: {'level': level, 'message': message},
      ),
    );
  }

  void dispose() {
    _eventController.close();
  }
}
