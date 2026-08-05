import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../../core/network/api_config.dart';

class EconomicEventModel {
  final String date;
  final String event;
  final String country;
  final String impact; // HIGH, MEDIUM, LOW
  final String forecast;
  final String previous;
  final String aiVerdict;

  const EconomicEventModel({
    required this.date,
    required this.event,
    required this.country,
    required this.impact,
    required this.forecast,
    required this.previous,
    required this.aiVerdict,
  });

  factory EconomicEventModel.fromJson(Map<String, dynamic> json) {
    return EconomicEventModel(
      date: json['date'] ?? 'Today',
      event: json['event'] ?? 'Economic Release',
      country: json['country'] ?? 'GLOBAL',
      impact: json['impact'] ?? 'HIGH',
      forecast: json['forecast'] ?? '--',
      previous: json['previous'] ?? '--',
      aiVerdict: json['aiVerdict'] ?? 'MONITOR VOLATILITY',
    );
  }
}

class GlobalMarketTickerModel {
  final String name;
  final String value;
  final String change;
  final bool isPositive;

  const GlobalMarketTickerModel({
    required this.name,
    required this.value,
    required this.change,
    required this.isPositive,
  });

  factory GlobalMarketTickerModel.fromJson(Map<String, dynamic> json) {
    return GlobalMarketTickerModel(
      name: json['name'] ?? 'TICKER',
      value: json['value'] ?? '0.0',
      change: json['change'] ?? '0.00%',
      isPositive: json['isPositive'] ?? true,
    );
  }
}

class GlobalMacroResponseModel {
  final List<GlobalMarketTickerModel> globalIndices;
  final List<GlobalMarketTickerModel> commodities;
  final List<EconomicEventModel> economicCalendar;
  final List<String> dailyBriefing;

  const GlobalMacroResponseModel({
    required this.globalIndices,
    required this.commodities,
    required this.economicCalendar,
    required this.dailyBriefing,
  });
}

class GlobalMacroRepository {
  static final GlobalMacroRepository _instance =
      GlobalMacroRepository._internal();
  factory GlobalMacroRepository() => _instance;
  GlobalMacroRepository._internal();

  Future<GlobalMacroResponseModel> getMacroData() async {
    final url = '${ApiConfig.baseUrl}/macro';
    debugPrint('[RUN-AUDIT] [GlobalMacroRepository] Fetching live Global Macro from: $url');

    try {
      final response = await http
          .get(Uri.parse(url), headers: ApiConfig.defaultHeaders())
          .timeout(const Duration(seconds: ApiConfig.timeoutSeconds));

      debugPrint('[RUN-AUDIT] [GlobalMacroRepository] Response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);

        final rawIndices = data['global_indices'] as List<dynamic>? ?? [];
        final indices = rawIndices
            .map((item) => GlobalMarketTickerModel.fromJson(item as Map<String, dynamic>))
            .toList();

        final rawCommodities = data['commodities'] as List<dynamic>? ?? [];
        final commodities = rawCommodities
            .map((item) => GlobalMarketTickerModel.fromJson(item as Map<String, dynamic>))
            .toList();

        final rawCalendar = data['economic_calendar'] as List<dynamic>? ?? [];
        final calendar = rawCalendar
            .map((item) => EconomicEventModel.fromJson(item as Map<String, dynamic>))
            .toList();

        final rawBriefing = data['daily_briefing'] as List<dynamic>? ?? [];
        final briefing = rawBriefing.map((e) => e.toString()).toList();

        return GlobalMacroResponseModel(
          globalIndices: indices,
          commodities: commodities,
          economicCalendar: calendar,
          dailyBriefing: briefing,
        );
      }
    } catch (e, st) {
      debugPrint('[RUN-AUDIT] [GlobalMacroRepository] EXCEPTION: $e\n$st');
    }

    return GlobalMacroResponseModel(
      globalIndices: getGlobalIndices(),
      commodities: getCommodities(),
      economicCalendar: getEconomicCalendar(),
      dailyBriefing: getDailyBriefing(),
    );
  }

  List<GlobalMarketTickerModel> getGlobalIndices() {
    return const [
      GlobalMarketTickerModel(
        name: 'GIFT NIFTY',
        value: '24,680.0',
        change: '+0.42%',
        isPositive: true,
      ),
      GlobalMarketTickerModel(
        name: 'DOW JONES',
        value: '40,842.5',
        change: '+0.55%',
        isPositive: true,
      ),
      GlobalMarketTickerModel(
        name: 'NASDAQ 100',
        value: '19,850.2',
        change: '+0.88%',
        isPositive: true,
      ),
      GlobalMarketTickerModel(
        name: 'S&P 500',
        value: '5,520.4',
        change: '+0.62%',
        isPositive: true,
      ),
      GlobalMarketTickerModel(
        name: 'NIKKEI 225',
        value: '38,120.0',
        change: '+0.34%',
        isPositive: true,
      ),
      GlobalMarketTickerModel(
        name: 'HANG SENG',
        value: '17,240.5',
        change: '-0.28%',
        isPositive: false,
      ),
    ];
  }

  List<GlobalMarketTickerModel> getCommodities() {
    return const [
      GlobalMarketTickerModel(
        name: 'GOLD (10g)',
        value: '₹72,450',
        change: '+0.15%',
        isPositive: true,
      ),
      GlobalMarketTickerModel(
        name: 'SILVER (1kg)',
        value: '₹84,200',
        change: '+0.45%',
        isPositive: true,
      ),
      GlobalMarketTickerModel(
        name: 'CRUDE OIL (BRENT)',
        value: '\$78.50',
        change: '-1.20%',
        isPositive: false,
      ),
      GlobalMarketTickerModel(
        name: 'NATURAL GAS',
        value: '\$2.15',
        change: '+1.40%',
        isPositive: true,
      ),
      GlobalMarketTickerModel(
        name: 'USD / INR',
        value: '₹83.72',
        change: '-0.05%',
        isPositive: true,
      ),
    ];
  }

  List<EconomicEventModel> getEconomicCalendar() {
    return const [
      EconomicEventModel(
        date: '14:30 Today',
        event: 'RBI Monetary Policy Decision',
        country: 'INDIA',
        impact: 'HIGH',
        forecast: '6.50%',
        previous: '6.50%',
        aiVerdict: 'NEUTRAL TO BULLISH (Repo rate status quo expected)',
      ),
      EconomicEventModel(
        date: '18:30 Today',
        event: 'US Fed Interest Rate Decision',
        country: 'USA',
        impact: 'HIGH',
        forecast: '5.25%',
        previous: '5.50%',
        aiVerdict: 'BULLISH (25bps rate cut priced in)',
      ),
      EconomicEventModel(
        date: 'Tomorrow',
        event: 'India Inflation CPI YoY',
        country: 'INDIA',
        impact: 'HIGH',
        forecast: '4.80%',
        previous: '5.10%',
        aiVerdict: 'BULLISH (Inflation easing towards 4.5% target)',
      ),
    ];
  }

  List<String> getDailyBriefing() {
    return const [
      'MORNING BIAS: Strong Bullish setup with GIFT NIFTY indicating +80 points gap-up open.',
      'GLOBAL CONTEXT: Wall Street closed in green (NASDAQ +0.88%) led by tech earnings rally.',
      'KEY EVENTS TODAY: RBI & US Fed rate decisions scheduled. Maintain strict Stop Loss boundaries.',
      'COMMODITY IMPACT: Brent Crude cooling down to \$78.50 is positive for Paint, Tire & Auto stocks.',
    ];
  }
}
