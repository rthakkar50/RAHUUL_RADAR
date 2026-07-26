class JournalTradeModel {
  final String id;
  final String symbol;
  final String signal;
  final double entryPrice;
  final double exitPrice;
  final double sl;
  final double target;
  final int qty;
  final double pnl;
  final double pnlPct;
  final String rMultiple;
  final String tradeDate;
  final String duration;
  final String result; // WIN, LOSS, OPEN
  final String exitReason;
  final double aiScore;
  final double confidence;
  final String trend;
  final String momentum;
  final String volume;
  final String structure;

  JournalTradeModel({
    required this.id,
    required this.symbol,
    required this.signal,
    required this.entryPrice,
    required this.exitPrice,
    required this.sl,
    required this.target,
    required this.qty,
    required this.pnl,
    required this.pnlPct,
    required this.rMultiple,
    required this.tradeDate,
    required this.duration,
    required this.result,
    required this.exitReason,
    required this.aiScore,
    required this.confidence,
    required this.trend,
    required this.momentum,
    required this.volume,
    required this.structure,
  });

  factory JournalTradeModel.fromJson(Map<String, dynamic> json) {
    return JournalTradeModel(
      id: json['id']?.toString() ?? '',
      symbol: json['symbol']?.toString() ?? '',
      signal: json['signal']?.toString() ?? 'BUY',
      entryPrice: (json['entry_price'] as num?)?.toDouble() ?? 0.0,
      exitPrice: (json['exit_price'] as num?)?.toDouble() ?? 0.0,
      sl: (json['sl'] as num?)?.toDouble() ?? 0.0,
      target: (json['target'] as num?)?.toDouble() ?? 0.0,
      qty: (json['qty'] as num?)?.toInt() ?? 0,
      pnl: (json['pnl'] as num?)?.toDouble() ?? 0.0,
      pnlPct: (json['pnl_pct'] as num?)?.toDouble() ?? 0.0,
      rMultiple: json['r_multiple']?.toString() ?? '0.0R',
      tradeDate: json['trade_date']?.toString() ?? '',
      duration: json['duration']?.toString() ?? '',
      result: json['result']?.toString() ?? 'UNKNOWN',
      exitReason: json['exit_reason']?.toString() ?? '',
      aiScore: (json['ai_score'] as num?)?.toDouble() ?? 0.0,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      trend: json['trend']?.toString() ?? '',
      momentum: json['momentum']?.toString() ?? '',
      volume: json['volume']?.toString() ?? '',
      structure: json['structure']?.toString() ?? '',
    );
  }
}

class DailyPnlPoint {
  final String date;
  final double pnl;

  DailyPnlPoint({required this.date, required this.pnl});

  factory DailyPnlPoint.fromJson(Map<String, dynamic> json) {
    return DailyPnlPoint(
      date: json['date']?.toString() ?? '',
      pnl: (json['pnl'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class MonthlyPnlPoint {
  final String month;
  final double pnl;

  MonthlyPnlPoint({required this.month, required this.pnl});

  factory MonthlyPnlPoint.fromJson(Map<String, dynamic> json) {
    return MonthlyPnlPoint(
      month: json['month']?.toString() ?? '',
      pnl: (json['pnl'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class JournalAnalyticsModel {
  final int totalTrades;
  final int winningTrades;
  final int losingTrades;
  final double winRate;
  final double averageProfit;
  final double averageLoss;
  final double profitFactor;
  final String averageHoldTime;
  final List<DailyPnlPoint> dailyPnl;
  final List<MonthlyPnlPoint> monthlyPnl;

  JournalAnalyticsModel({
    required this.totalTrades,
    required this.winningTrades,
    required this.losingTrades,
    required this.winRate,
    required this.averageProfit,
    required this.averageLoss,
    required this.profitFactor,
    required this.averageHoldTime,
    required this.dailyPnl,
    required this.monthlyPnl,
  });

  factory JournalAnalyticsModel.fromJson(Map<String, dynamic> json) {
    return JournalAnalyticsModel(
      totalTrades: (json['total_trades'] as num?)?.toInt() ?? 0,
      winningTrades: (json['winning_trades'] as num?)?.toInt() ?? 0,
      losingTrades: (json['losing_trades'] as num?)?.toInt() ?? 0,
      winRate: (json['win_rate'] as num?)?.toDouble() ?? 0.0,
      averageProfit: (json['average_profit'] as num?)?.toDouble() ?? 0.0,
      averageLoss: (json['average_loss'] as num?)?.toDouble() ?? 0.0,
      profitFactor: (json['profit_factor'] as num?)?.toDouble() ?? 0.0,
      averageHoldTime: json['average_hold_time']?.toString() ?? 'N/A',
      dailyPnl: (json['daily_pnl'] as List<dynamic>?)
              ?.map((e) => DailyPnlPoint.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      monthlyPnl: (json['monthly_pnl'] as List<dynamic>?)
              ?.map((e) => MonthlyPnlPoint.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }
}

class JournalResponseModel {
  final List<JournalTradeModel> trades;
  final JournalAnalyticsModel analytics;
  final double timestamp;

  JournalResponseModel({
    required this.trades,
    required this.analytics,
    required this.timestamp,
  });

  factory JournalResponseModel.fromJson(Map<String, dynamic> json) {
    return JournalResponseModel(
      trades: (json['trades'] as List<dynamic>?)
              ?.map((e) => JournalTradeModel.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      analytics: JournalAnalyticsModel.fromJson(
          json['analytics'] as Map<String, dynamic>? ?? {}),
      timestamp: (json['timestamp'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
