class SentinelOpportunityModel {
  final String symbol;
  final String company;
  final String sector;
  final double priorityScore; // 0 - 100
  final String signal;
  final double entryPrice;
  final double stopLoss;
  final double target1;
  final double target2;
  final double target3;
  final double expectedReturnPct;
  final int recommendedQty;
  final double capitalRequired;
  final String confidencePct;
  final String holdingPeriod;
  final String aiRationale;

  const SentinelOpportunityModel({
    required this.symbol,
    required this.company,
    required this.sector,
    required this.priorityScore,
    required this.signal,
    required this.entryPrice,
    required this.stopLoss,
    required this.target1,
    required this.target2,
    required this.target3,
    required this.expectedReturnPct,
    required this.recommendedQty,
    required this.capitalRequired,
    required this.confidencePct,
    required this.holdingPeriod,
    required this.aiRationale,
  });
}

class MarketSentinelMoodModel {
  final String overallMood; // BULLISH, BEARISH, NEUTRAL
  final double confidencePct;
  final double indiaVix;
  final double pcr;
  final String fiiFlow;
  final String diiFlow;
  final String marketBreadth;

  const MarketSentinelMoodModel({
    required this.overallMood,
    required this.confidencePct,
    required this.indiaVix,
    required this.pcr,
    required this.fiiFlow,
    required this.diiFlow,
    required this.marketBreadth,
  });
}

class AiSentinelRepository {
  static final AiSentinelRepository _instance =
      AiSentinelRepository._internal();
  factory AiSentinelRepository() => _instance;
  AiSentinelRepository._internal();

  MarketSentinelMoodModel getMarketMood() {
    return const MarketSentinelMoodModel(
      overallMood: 'STRONG BULLISH',
      confidencePct: 92.0,
      indiaVix: 13.82,
      pcr: 1.28,
      fiiFlow: '+₹2,140 Cr (Net Buy)',
      diiFlow: '+₹2,250 Cr (Net Buy)',
      marketBreadth: '3.4 : 1 (Advances / Declines)',
    );
  }

  List<SentinelOpportunityModel> getRankedOpportunities() {
    return const [
      SentinelOpportunityModel(
        symbol: 'DIVISLAB',
        company: 'Divi\'s Laboratories Ltd.',
        sector: 'PHARMA',
        priorityScore: 96.5,
        signal: 'STRONG BUY',
        entryPrice: 4850.0,
        stopLoss: 4720.0,
        target1: 4980.0,
        target2: 5100.0,
        target3: 5250.0,
        expectedReturnPct: 5.8,
        recommendedQty: 25,
        capitalRequired: 121250.0,
        confidencePct: '94.2%',
        holdingPeriod: '2 - 3 Days',
        aiRationale:
            'FDA approval catalyst paired with 2.8x volume breakout above 20-day EMA.',
      ),
      SentinelOpportunityModel(
        symbol: 'DIXON',
        company: 'Dixon Technologies Ltd.',
        sector: 'CONSUMER',
        priorityScore: 91.0,
        signal: 'BUY',
        entryPrice: 12450.0,
        stopLoss: 12100.0,
        target1: 12850.0,
        target2: 13100.0,
        target3: 13500.0,
        expectedReturnPct: 5.2,
        recommendedQty: 10,
        capitalRequired: 124500.0,
        confidencePct: '89.5%',
        holdingPeriod: '3 - 5 Days',
        aiRationale:
            'Electronics PLI manufacturing expansion & strong quarterly margin guidance.',
      ),
    ];
  }

  List<String> getDailyMission() {
    return const [
      'MORNING BRIEF: Gap-up open confirmed (+80 pts on GIFT NIFTY). Look for long swing setups in Pharma & IT.',
      'MID-DAY REVIEW: NIFTY consolidating near 24,650 resistance. All open positions trailing SL active.',
      'CLOSING SUMMARY: Portfolio equity gained +0.85% today. Zero risk breaches logged.',
      'TOMORROW WATCHLIST: Track RELIANCE near ₹3,120 support and TCS ahead of US macro data.',
    ];
  }
}
