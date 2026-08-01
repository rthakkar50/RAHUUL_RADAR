class NewsItemModel {
  final String id;
  final String title;
  final String source;
  final String timeAgo;
  final String category; // BREAKING, HIGH IMPACT, MEDIUM, LOW
  final String
  sentiment; // VERY BULLISH, BULLISH, NEUTRAL, BEARISH, VERY BEARISH
  final double confidencePct;
  final String affectedSymbol;
  final String sector;
  final String summary;
  final List<String> keyPoints;
  final String tradingImpact;
  final String suggestedAction;

  const NewsItemModel({
    required this.id,
    required this.title,
    required this.source,
    required this.timeAgo,
    required this.category,
    required this.sentiment,
    required this.confidencePct,
    required this.affectedSymbol,
    required this.sector,
    required this.summary,
    required this.keyPoints,
    required this.tradingImpact,
    required this.suggestedAction,
  });
}

class NewsRepository {
  static final NewsRepository _instance = NewsRepository._internal();
  factory NewsRepository() => _instance;
  NewsRepository._internal();

  List<NewsItemModel> getLatestNews() {
    return const [
      NewsItemModel(
        id: 'NEWS-101',
        title:
            'Divi\'s Laboratories Receives US FDA Approval for Generic Active Ingredient',
        source: 'CNBC-TV18 / Exchange Filing',
        timeAgo: '12 mins ago',
        category: 'BREAKING',
        sentiment: 'VERY BULLISH',
        confidencePct: 96.5,
        affectedSymbol: 'DIVISLAB',
        sector: 'PHARMA',
        summary:
            'FDA approves key oncology drug master file without any inspection observations.',
        keyPoints: [
          'Unconditional approval received for Vizag manufacturing unit 2.',
          'Expected revenue accretion of \$45M annually from Q3.',
        ],
        tradingImpact: 'POSITIVE (Target +4.5% intraday surge expected)',
        suggestedAction: 'HOLD LONG / ADD ON DIP (Portfolio Holding Match)',
      ),
      NewsItemModel(
        id: 'NEWS-102',
        title:
            'Reliance Industries Partners with Global Tech Giant for AI Data Center Expansion',
        source: 'Economic Times',
        timeAgo: '45 mins ago',
        category: 'HIGH IMPACT',
        sentiment: 'BULLISH',
        confidencePct: 91.0,
        affectedSymbol: 'RELIANCE',
        sector: 'ENERGY',
        summary:
            'Strategic 50:50 joint venture announced for 1GW green data center infrastructure.',
        keyPoints: [
          'Investment commitment of ₹25,000 Cr over 3 years.',
          'Zero net debt expansion due to partner equity contribution.',
        ],
        tradingImpact: 'POSITIVE (Long-term valuation rerating)',
        suggestedAction: 'ACCUMULATE SWING',
      ),
      NewsItemModel(
        id: 'NEWS-103',
        title:
            'US Fed Signals Rate Cut Expectations as Inflation Cools to 2.8%',
        source: 'Bloomberg',
        timeAgo: '2 hours ago',
        category: 'HIGH IMPACT',
        sentiment: 'BULLISH',
        confidencePct: 88.0,
        affectedSymbol: 'NIFTY50',
        sector: 'MACRO',
        summary:
            'Federal Reserve Chairman Powell hints at policy easing in upcoming September meeting.',
        keyPoints: [
          'Cooling labor market and lower PCE deflator support 25bps cut.',
          'Emerging market capital inflows expected to surge.',
        ],
        tradingImpact: 'VERY BULLISH (Broad market gap-up support)',
        suggestedAction: 'MAINTAIN LONG BIAS',
      ),
    ];
  }
}
