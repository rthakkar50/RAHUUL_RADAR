class TradeForensicRecordModel {
  final String tradeId;
  final String symbol;
  final String signal;
  final double entryPrice;
  final double exitPrice;
  final double pnl;
  final double pnlPct;
  final String rMultiple;
  final String duration;
  final String strategy;
  final String sector;
  final String marketRegime;
  final double aiConfidence;
  final double masterAiScore;
  final String outcome; // WIN, LOSS, BREAKEVEN
  final String failureRootCause; // None, False Breakout, Sector Weakness, etc.
  final String lessonLearned;

  const TradeForensicRecordModel({
    required this.tradeId,
    required this.symbol,
    required this.signal,
    required this.entryPrice,
    required this.exitPrice,
    required this.pnl,
    required this.pnlPct,
    required this.rMultiple,
    required this.duration,
    required this.strategy,
    required this.sector,
    required this.marketRegime,
    required this.aiConfidence,
    required this.masterAiScore,
    required this.outcome,
    required this.failureRootCause,
    required this.lessonLearned,
  });
}

class AiEvolutionMetricsModel {
  final String version;
  final double accuracyPct;
  final double profitFactor;
  final double maxDrawdownPct;
  final int avgLatencyMs;

  const AiEvolutionMetricsModel({
    required this.version,
    required this.accuracyPct,
    required this.profitFactor,
    required this.maxDrawdownPct,
    required this.avgLatencyMs,
  });
}

class TradeForensicsRepository {
  static final TradeForensicsRepository _instance =
      TradeForensicsRepository._internal();
  factory TradeForensicsRepository() => _instance;
  TradeForensicsRepository._internal();

  List<TradeForensicRecordModel> getForensicHistory() {
    return const [
      TradeForensicRecordModel(
        tradeId: 'PAYTM-33',
        symbol: 'PAYTM',
        signal: 'BUY',
        entryPrice: 850.0,
        exitPrice: 900.0,
        pnl: 1450.0,
        pnlPct: 5.88,
        rMultiple: '+2.5R',
        duration: '2 Days',
        strategy: 'Breakout Momentum',
        sector: 'FINANCIAL',
        marketRegime: 'BULLISH TREND',
        aiConfidence: 94.2,
        masterAiScore: 92.5,
        outcome: 'WIN',
        failureRootCause: 'None (Perfect Target Hit)',
        lessonLearned:
            'Volume confirmation > 1.5x increases swing win rate to 88%.',
      ),
      TradeForensicRecordModel(
        tradeId: 'TATAMOTORS-14',
        symbol: 'TATAMOTORS',
        signal: 'BUY',
        entryPrice: 980.0,
        exitPrice: 995.0,
        pnl: 375.0,
        pnlPct: 1.53,
        rMultiple: '+1.0R',
        duration: '1 Day',
        strategy: 'EMA Crossover',
        sector: 'AUTO',
        marketRegime: 'CONSOLIDATION',
        aiConfidence: 81.0,
        masterAiScore: 82.0,
        outcome: 'WIN',
        failureRootCause: 'None (Partial Exit)',
        lessonLearned:
            'Trailing SL preserved 1.0R profit prior to sector pull-back.',
      ),
      TradeForensicRecordModel(
        tradeId: 'INFY-88',
        symbol: 'INFY',
        signal: 'BUY',
        entryPrice: 1820.0,
        exitPrice: 1795.0,
        pnl: -625.0,
        pnlPct: -1.37,
        rMultiple: '-1.0R',
        duration: '1 Day',
        strategy: 'Pullback Support',
        sector: 'IT',
        marketRegime: 'HIGH VOLATILITY',
        aiConfidence: 76.5,
        masterAiScore: 74.0,
        outcome: 'LOSS',
        failureRootCause: 'Market Regime Mismatch (High VIX Whipsaw)',
        lessonLearned:
            'Reduce position allocation by 50% when India VIX > 16.5.',
      ),
    ];
  }

  List<AiEvolutionMetricsModel> getEvolutionTimeline() {
    return const [
      AiEvolutionMetricsModel(
        version: 'AI Engine v1.0',
        accuracyPct: 62.4,
        profitFactor: 1.45,
        maxDrawdownPct: 8.2,
        avgLatencyMs: 42,
      ),
      AiEvolutionMetricsModel(
        version: 'AI Engine v2.0',
        accuracyPct: 74.2,
        profitFactor: 1.88,
        maxDrawdownPct: 5.4,
        avgLatencyMs: 18,
      ),
      AiEvolutionMetricsModel(
        version: 'AI Engine v3.0',
        accuracyPct: 82.5,
        profitFactor: 2.15,
        maxDrawdownPct: 3.8,
        avgLatencyMs: 8,
      ),
      AiEvolutionMetricsModel(
        version: 'AI Engine v3.2 (AMD)',
        accuracyPct: 88.4,
        profitFactor: 2.45,
        maxDrawdownPct: 2.1,
        avgLatencyMs: 2,
      ),
    ];
  }
}
