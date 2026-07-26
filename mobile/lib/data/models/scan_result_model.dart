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
    return ScanResultModel(
      symbol: json['Symbol']?.toString() ?? '',
      company: json['Company']?.toString() ?? '',
      sector: json['Sector']?.toString() ?? '',
      price: (json['Price'] as num?)?.toDouble() ?? 0.0,
      signal: json['Signal']?.toString() ?? 'WATCH',
      score: (json['Score'] as num?)?.toDouble() ?? 0.0,
      rawScore: (json['Raw Score'] as num?)?.toDouble() ?? 0.0,
      confidence: (json['Confidence'] as num?)?.toDouble() ?? 0.0,
      trend: json['Trend']?.toString() ?? '',
      volume: json['Volume']?.toString() ?? '0',
      riskReward: json['Risk Reward']?.toString() ?? '',
      rsScore: (json['RS Score'] as num?)?.toDouble() ?? 0.0,
      entry: (json['Entry'] as num?)?.toDouble() ?? 0.0,
      stopLoss: (json['Stop Loss'] as num?)?.toDouble() ?? 0.0,
      target1: (json['Target 1'] as num?)?.toDouble() ?? 0.0,
      target2: (json['Target 2'] as num?)?.toDouble() ?? 0.0,
      tradeGrade: json['Trade Grade']?.toString() ?? '',
      riskGrade: json['Risk Grade']?.toString() ?? '',
      timestamp: json['Timestamp']?.toString() ?? '',
    );
  }
}
