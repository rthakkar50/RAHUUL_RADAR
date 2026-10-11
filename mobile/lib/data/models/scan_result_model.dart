class ScanResultModel {
  final String symbol;
  final String company;
  final String sector;
  final double price;
  final String signal;
  final String entryDecision;
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
  final double target3;
  final String tradeGrade;
  final String riskGrade;
  final String timestamp;
  final List<String> whySelected;
  final List<String> reasons;
  final Map<String, dynamic> scores;
  final Map<String, dynamic> indicators;

  String get displaySignal {
    if (entryDecision.isNotEmpty && entryDecision.toUpperCase() != signal.toUpperCase()) {
      return '$entryDecision | $signal';
    }
    return signal;
  }

  ScanResultModel({
    required this.symbol,
    required this.company,
    required this.sector,
    required this.price,
    required this.signal,
    this.entryDecision = '',
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
    required this.target3,
    required this.tradeGrade,
    required this.riskGrade,
    required this.timestamp,
    this.whySelected = const [],
    this.reasons = const [],
    this.scores = const {},
    this.indicators = const {},
  });

  factory ScanResultModel.fromJson(Map<String, dynamic> json) {
    final p = (json['Price'] ?? json['price'] as num?)?.toDouble() ?? 0.0;
    String rawSignal = (json['Signal'] ?? json['signal'])?.toString() ?? 'WATCH';
    String entryDec = (json['Entry Decision'] ?? json['entry_decision'])?.toString() ?? '';

    // Backward compatibility: normalize legacy concatenated strings ("RETEST FIRST | BUY")
    if (rawSignal.contains(' | ')) {
      final parts = rawSignal.split(' | ');
      if (entryDec.isEmpty) {
        entryDec = parts[0].trim();
      }
      rawSignal = parts[1].trim();
    }
    final sig = rawSignal.toUpperCase();
    final entryVal = (json['Entry'] ?? json['entry'] as num?)?.toDouble() ?? p;
    
    double slVal = (json['Stop Loss'] ?? json['sl'] as num?)?.toDouble() ?? 0.0;
    double t1Val = (json['Target 1'] ?? json['target_1'] as num?)?.toDouble() ?? 0.0;
    double t2Val = (json['Target 2'] ?? json['target_2'] as num?)?.toDouble() ?? 0.0;
    double t3Val = (json['Target 3'] ?? json['target_3'] as num?)?.toDouble() ?? 0.0;

    final whyRaw = json['_why_selected'] ?? json['why_selected'];
    final List<String> whyList = (whyRaw is List)
        ? whyRaw.map((e) => e.toString()).toList()
        : <String>[];

    final reaRaw = json['_reasons'] ?? json['reasons'];
    final List<String> reaList = (reaRaw is List)
        ? reaRaw.map((e) => e.toString()).toList()
        : <String>[];

    final rawTs = (json['Timestamp'] ?? json['timestamp'])?.toString().trim() ?? '';

    return ScanResultModel(
      symbol: (json['Symbol'] ?? json['symbol'])?.toString() ?? '',
      company: (json['Company'] ?? json['company'])?.toString() ?? '',
      sector: (json['Sector'] ?? json['sector'])?.toString() ?? 'GENERAL',
      price: p,
      signal: sig,
      entryDecision: entryDec,
      score: (json['Score'] ?? json['score'] as num?)?.toDouble() ?? 0.0,
      rawScore: (json['Raw Score'] ?? json['raw_score'] as num?)?.toDouble() ?? 0.0,
      confidence: (json['Confidence'] ?? json['confidence'] as num?)?.toDouble() ?? 0.0,
      trend: (json['Trend'] ?? json['trend'])?.toString() ?? 'NEUTRAL',
      volume: (json['Volume'] ?? json['volume'])?.toString() ?? 'N/A',
      riskReward: (json['Risk Reward'] ?? json['risk_reward'])?.toString() ?? 'N/A',
      rsScore: (json['RS Score'] ?? json['rs_score'] as num?)?.toDouble() ?? 0.0,
      entry: entryVal,
      stopLoss: slVal,
      target1: t1Val,
      target2: t2Val,
      target3: t3Val,
      tradeGrade: (json['Trade Grade'] ?? json['trade_grade'])?.toString() ?? 'N/A',
      riskGrade: (json['Risk Grade'] ?? json['risk_grade'])?.toString() ?? 'UNKNOWN',
      timestamp: rawTs.isNotEmpty ? rawTs : 'UNAVAILABLE',
      whySelected: whyList,
      reasons: reaList,
      scores: Map<String, dynamic>.from(json['scores'] as Map? ?? {}),
      indicators: Map<String, dynamic>.from(json['indicators'] as Map? ?? {}),
    );
  }
}
