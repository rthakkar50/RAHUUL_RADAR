class ScanResultModel {
  final String symbol;
  final String company;
  final String sector;
  final double price;
  final String signal;
  final double score;
  final double rawScore;
  final double confidence;
  final String trend;
  final String volume;
  final String riskReward;
  final double rsScore;
  final double entry;
  final double stopLoss;
  final double target1;
  final double target2;
  final String tradeGrade;
  final String riskGrade;
  final String timestamp;

  ScanResultModel({
    required this.symbol,
    required this.company,
    required this.sector,
    required this.price,
    required this.signal,
    required this.score,
    required this.rawScore,
    required this.confidence,
    required this.trend,
    required this.volume,
    required this.riskReward,
    required this.rsScore,
    required this.entry,
    required this.stopLoss,
    required this.target1,
    required this.target2,
    required this.tradeGrade,
    required this.riskGrade,
    required this.timestamp,
  });

  factory ScanResultModel.fromJson(Map<String, dynamic> json) {
    final p = (json['Price'] ?? json['price'] as num?)?.toDouble() ?? 0.0;
    return ScanResultModel(
      symbol: (json['Symbol'] ?? json['symbol'])?.toString() ?? '',
      company: (json['Company'] ?? json['company'])?.toString() ?? '',
      sector: (json['Sector'] ?? json['sector'])?.toString() ?? 'GENERAL',
      price: p,
      signal: (json['Signal'] ?? json['signal'])?.toString() ?? 'BUY',
      score: (json['Score'] ?? json['score'] as num?)?.toDouble() ?? 80.0,
      rawScore:
          (json['Raw Score'] ?? json['raw_score'] as num?)?.toDouble() ?? 80.0,
      confidence:
          (json['Confidence'] ?? json['confidence'] as num?)?.toDouble() ??
          85.0,
      trend: (json['Trend'] ?? json['trend'])?.toString() ?? 'BULLISH',
      volume: (json['Volume'] ?? json['volume'])?.toString() ?? '1.5x',
      riskReward:
          (json['Risk Reward'] ?? json['risk_reward'])?.toString() ?? '1:2.0',
      rsScore:
          (json['RS Score'] ?? json['rs_score'] as num?)?.toDouble() ?? 75.0,
      entry: (json['Entry'] ?? json['entry'] as num?)?.toDouble() ?? p,
      stopLoss:
          (json['Stop Loss'] ?? json['sl'] as num?)?.toDouble() ??
          (p > 0 ? p * 0.98 : 0.0),
      target1:
          (json['Target 1'] ?? json['target_1'] as num?)?.toDouble() ??
          (p > 0 ? p * 1.04 : 0.0),
      target2:
          (json['Target 2'] ?? json['target_2'] as num?)?.toDouble() ??
          (p > 0 ? p * 1.08 : 0.0),
      tradeGrade:
          (json['Trade Grade'] ?? json['trade_grade'])?.toString() ?? 'A',
      riskGrade:
          (json['Risk Grade'] ?? json['risk_grade'])?.toString() ?? 'LOW',
      timestamp: (json['Timestamp'] ?? json['timestamp'])?.toString() ?? '',
    );
  }
}
