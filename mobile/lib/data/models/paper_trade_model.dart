enum PaperTradeStatus {
  open,
  target1Hit,
  target2Hit,
  stopLossHit,
  closed,
  cancelled,
}

class PaperTradeModel {
  final String id;
  final String symbol;
  final String signal; // BUY or SELL
  final String sector;
  final double entryPrice;
  double currentPrice;
  double? exitPrice;
  final int quantity;
  final double stopLoss;
  final double target1;
  final double target2;
  final double riskReward;
  final String strategy;
  final DateTime entryTime;
  DateTime? exitTime;
  PaperTradeStatus status;
  String notes;

  PaperTradeModel({
    required this.id,
    required this.symbol,
    required this.signal,
    required this.sector,
    required this.entryPrice,
    required this.currentPrice,
    this.exitPrice,
    required this.quantity,
    required this.stopLoss,
    required this.target1,
    required this.target2,
    required this.riskReward,
    required this.strategy,
    required this.entryTime,
    this.exitTime,
    this.status = PaperTradeStatus.open,
    this.notes = '',
  });

  double get capitalUsed => entryPrice * quantity;

  double get unrealizedPnL {
    if (signal.toUpperCase().contains('BUY')) {
      return (currentPrice - entryPrice) * quantity;
    } else {
      return (entryPrice - currentPrice) * quantity;
    }
  }

  double get realizedPnL {
    if (exitPrice == null) return 0.0;
    if (signal.toUpperCase().contains('BUY')) {
      return (exitPrice! - entryPrice) * quantity;
    } else {
      return (entryPrice - exitPrice!) * quantity;
    }
  }

  double get virtualCharges => (capitalUsed * 0.0003); // 0.03% virtual brokerage

  double get netPnL => realizedPnL - virtualCharges;

  double get returnPct {
    if (capitalUsed == 0) return 0.0;
    return (realizedPnL / capitalUsed) * 100;
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'symbol': symbol,
      'signal': signal,
      'sector': sector,
      'entryPrice': entryPrice,
      'currentPrice': currentPrice,
      'exitPrice': exitPrice,
      'quantity': quantity,
      'stopLoss': stopLoss,
      'target1': target1,
      'target2': target2,
      'riskReward': riskReward,
      'strategy': strategy,
      'entryTime': entryTime.toIso8601String(),
      'exitTime': exitTime?.toIso8601String(),
      'status': status.name,
      'notes': notes,
    };
  }

  factory PaperTradeModel.fromJson(Map<String, dynamic> json) {
    return PaperTradeModel(
      id: json['id'] ?? '',
      symbol: json['symbol'] ?? '',
      signal: json['signal'] ?? 'BUY',
      sector: json['sector'] ?? 'General',
      entryPrice: (json['entryPrice'] as num).toDouble(),
      currentPrice: (json['currentPrice'] as num).toDouble(),
      exitPrice: json['exitPrice'] != null ? (json['exitPrice'] as num).toDouble() : null,
      quantity: (json['quantity'] as num).toInt(),
      stopLoss: (json['stopLoss'] as num).toDouble(),
      target1: (json['target1'] as num).toDouble(),
      target2: (json['target2'] as num).toDouble(),
      riskReward: (json['riskReward'] as num).toDouble(),
      strategy: json['strategy'] ?? 'Swing',
      entryTime: DateTime.parse(json['entryTime']),
      exitTime: json['exitTime'] != null ? DateTime.parse(json['exitTime']) : null,
      status: PaperTradeStatus.values.firstWhere(
        (e) => e.name == json['status'],
        orElse: () => PaperTradeStatus.open,
      ),
      notes: json['notes'] ?? '',
    );
  }
}
