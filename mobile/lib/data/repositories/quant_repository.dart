import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../../core/network/api_config.dart';

class QuantMetricsModel {
  final double winRate;
  final double profitFactor;
  final double sharpeRatio;
  final double sortinoRatio;
  final int totalTrades;

  const QuantMetricsModel({
    required this.winRate,
    required this.profitFactor,
    required this.sharpeRatio,
    required this.sortinoRatio,
    required this.totalTrades,
  });

  factory QuantMetricsModel.fromJson(Map<String, dynamic> json) {
    return QuantMetricsModel(
      winRate: (json['winRate'] as num?)?.toDouble() ?? 0.0,
      profitFactor: (json['profitFactor'] as num?)?.toDouble() ?? 0.0,
      sharpeRatio: (json['sharpeRatio'] as num?)?.toDouble() ?? 0.0,
      sortinoRatio: (json['sortinoRatio'] as num?)?.toDouble() ?? 0.0,
      totalTrades: (json['totalTrades'] as num?)?.toInt() ?? 0,
    );
  }
}

class ConfidenceBucketModel {
  final String bucket;
  final double winRatePct;
  final double ratio;

  const ConfidenceBucketModel({
    required this.bucket,
    required this.winRatePct,
    required this.ratio,
  });

  factory ConfidenceBucketModel.fromJson(Map<String, dynamic> json) {
    return ConfidenceBucketModel(
      bucket: json['bucket'] ?? 'Confidence',
      winRatePct: (json['winRatePct'] as num?)?.toDouble() ?? 0.0,
      ratio: (json['ratio'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class ScannerRankingModel {
  final int rank;
  final String scanner;
  final double winRatePct;
  final String avgRr;

  const ScannerRankingModel({
    required this.rank,
    required this.scanner,
    required this.winRatePct,
    required this.avgRr,
  });

  factory ScannerRankingModel.fromJson(Map<String, dynamic> json) {
    return ScannerRankingModel(
      rank: (json['rank'] as num?)?.toInt() ?? 1,
      scanner: json['scanner'] ?? 'Scanner',
      winRatePct: (json['winRatePct'] as num?)?.toDouble() ?? 0.0,
      avgRr: json['avgRr'] ?? '1:2.0',
    );
  }
}

class TradeReplayItemModel {
  final String type; // WIN or LOSS
  final String title;
  final String analysis;

  const TradeReplayItemModel({
    required this.type,
    required this.title,
    required this.analysis,
  });

  factory TradeReplayItemModel.fromJson(Map<String, dynamic> json) {
    return TradeReplayItemModel(
      type: json['type'] ?? 'WIN',
      title: json['title'] ?? 'Trade Replay',
      analysis: json['analysis'] ?? 'Trade replay breakdown.',
    );
  }
}

class QuantResponseModel {
  final QuantMetricsModel metrics;
  final List<ConfidenceBucketModel> confidenceBuckets;
  final List<ScannerRankingModel> scannerRankings;
  final List<String> aiRecommendations;
  final List<TradeReplayItemModel> replays;

  const QuantResponseModel({
    required this.metrics,
    required this.confidenceBuckets,
    required this.scannerRankings,
    required this.aiRecommendations,
    required this.replays,
  });
}

class QuantRepository {
  static final QuantRepository _instance = QuantRepository._internal();
  factory QuantRepository() => _instance;
  QuantRepository._internal();

  Future<QuantResponseModel> getQuantBacktestData() async {
    final url = '${ApiConfig.baseUrl}/quant/backtest';
    debugPrint('[RUN-AUDIT] [QuantRepository] Fetching live Quant Backtest from: $url');

    try {
      final response = await http
          .get(Uri.parse(url), headers: ApiConfig.defaultHeaders())
          .timeout(const Duration(seconds: ApiConfig.timeoutSeconds));

      debugPrint('[RUN-AUDIT] [QuantRepository] Response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);

        final metrics = QuantMetricsModel.fromJson(
          data['metrics'] as Map<String, dynamic>? ?? {},
        );

        final rawBuckets = data['confidence_buckets'] as List<dynamic>? ?? [];
        final buckets = rawBuckets
            .map((item) => ConfidenceBucketModel.fromJson(item as Map<String, dynamic>))
            .toList();

        final rawRankings = data['scanner_rankings'] as List<dynamic>? ?? [];
        final rankings = rawRankings
            .map((item) => ScannerRankingModel.fromJson(item as Map<String, dynamic>))
            .toList();

        final rawRecs = data['ai_recommendations'] as List<dynamic>? ?? [];
        final recs = rawRecs.map((e) => e.toString()).toList();

        final rawReplays = data['replays'] as List<dynamic>? ?? [];
        final replays = rawReplays
            .map((item) => TradeReplayItemModel.fromJson(item as Map<String, dynamic>))
            .toList();

        return QuantResponseModel(
          metrics: metrics,
          confidenceBuckets: buckets,
          scannerRankings: rankings,
          aiRecommendations: recs,
          replays: replays,
        );
      }
    } catch (e, st) {
      debugPrint('[RUN-AUDIT] [QuantRepository] EXCEPTION: $e\n$st');
    }

    return getFallbackData();
  }

  QuantResponseModel getFallbackData() {
    return const QuantResponseModel(
      metrics: QuantMetricsModel(
        winRate: 0.0,
        profitFactor: 0.0,
        sharpeRatio: 0.0,
        sortinoRatio: 0.0,
        totalTrades: 0,
      ),
      confidenceBuckets: [],
      scannerRankings: [],
      aiRecommendations: [
        'Zero completed trades recorded in journal.',
        'Execute trades via paper trading or live broker to run quant backtest analytics.'
      ],
      replays: [],
    );
  }
}
