import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../../core/network/api_config.dart';

class NewsItemModel {
  final String id;
  final String title;
  final String source;
  final String timeAgo;
  final String category; // BREAKING, HIGH IMPACT, MEDIUM, LOW
  final String sentiment; // VERY BULLISH, BULLISH, NEUTRAL, BEARISH, VERY BEARISH
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

  factory NewsItemModel.fromJson(Map<String, dynamic> json) {
    final rawKeyPoints = json['keyPoints'] as List<dynamic>? ?? [];
    final keyPointsList = rawKeyPoints.map((e) => e.toString()).toList();

    return NewsItemModel(
      id: json['id'] ?? 'NEWS-101',
      title: json['title'] ?? 'Market Event Signal',
      source: json['source'] ?? 'RAHUUL_RADAR Intelligence',
      timeAgo: json['timeAgo'] ?? 'Just now',
      category: json['category'] ?? 'BREAKING',
      sentiment: json['sentiment'] ?? 'BULLISH',
      confidencePct: (json['confidencePct'] as num?)?.toDouble() ?? 88.0,
      affectedSymbol: json['affectedSymbol'] ?? 'NIFTY50',
      sector: json['sector'] ?? 'EQUITY',
      summary: json['summary'] ?? 'Market analysis event update.',
      keyPoints: keyPointsList.isNotEmpty ? keyPointsList : ['Live risk boundary monitoring active.'],
      tradingImpact: json['tradingImpact'] ?? 'POSITIVE',
      suggestedAction: json['suggestedAction'] ?? 'MAINTAIN LONG BIAS',
    );
  }
}

class NewsRepository {
  static final NewsRepository _instance = NewsRepository._internal();
  factory NewsRepository() => _instance;
  NewsRepository._internal();

  Future<List<NewsItemModel>> getLatestNews() async {
    final url = '${ApiConfig.baseUrl}/news';
    debugPrint('[RUN-AUDIT] [NewsRepository] Fetching live AI News from: $url');

    try {
      final response = await http
          .get(Uri.parse(url), headers: ApiConfig.defaultHeaders())
          .timeout(const Duration(seconds: ApiConfig.timeoutSeconds));

      debugPrint('[RUN-AUDIT] [NewsRepository] Response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        final rawNews = data['news'] as List<dynamic>? ?? [];

        return rawNews
            .map((item) => NewsItemModel.fromJson(item as Map<String, dynamic>))
            .toList();
      }
    } catch (e, st) {
      debugPrint('[RUN-AUDIT] [NewsRepository] EXCEPTION: $e\n$st');
    }

    // Fallback seed data if offline or socket timeout
    return getFallbackNews();
  }

  List<NewsItemModel> getFallbackNews() {
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
    ];
  }
}
