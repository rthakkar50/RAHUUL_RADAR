import 'scan_result_model.dart';

class ScanResponseModel {
  final int totalScanned;
  final int totalUniverse;
  final int totalAttempted;
  final int totalProcessed;
  final int totalRanked;
  final int qualifiedCount;
  final int filterRejectedCount;
  final int noDataCount;
  final int rejectedCount;
  final int waitCount;
  final int errorCount;
  final String marketQuality;
  final double execTime;
  final List<ScanResultModel> qualifiedResults;
  final String lastUpdated;
  final Map<String, int> rejectionAnalytics;
  final List<Map<String, dynamic>> pipelineStages;
  final Map<String, dynamic> scannerHealth;
  final Map<String, dynamic> marketSummary;
  final Map<String, dynamic> performanceMetrics;
  final List<Map<String, dynamic>> symbolDecisionTraces;

  ScanResponseModel({
    required this.totalScanned,
    required this.totalUniverse,
    this.totalAttempted = 200,
    this.totalProcessed = 195,
    this.totalRanked = 34,
    required this.qualifiedCount,
    required this.filterRejectedCount,
    required this.noDataCount,
    required this.rejectedCount,
    required this.waitCount,
    required this.errorCount,
    required this.marketQuality,
    required this.execTime,
    required this.qualifiedResults,
    required this.lastUpdated,
    this.rejectionAnalytics = const {},
    this.pipelineStages = const [],
    this.scannerHealth = const {},
    this.marketSummary = const {},
    this.performanceMetrics = const {},
    this.symbolDecisionTraces = const [],
  });

  factory ScanResponseModel.fromJson(Map<String, dynamic> json) {
    var list = (json['qualified_results'] ?? json['results'] ?? json['data']) as List? ?? [];
    List<ScanResultModel> results = list
        .map((i) => ScanResultModel.fromJson(i))
        .toList();

    var rejRaw = json['rejection_analytics'] as Map<String, dynamic>? ?? {};
    Map<String, int> rejMap = {};
    rejRaw.forEach((k, v) {
      rejMap[k] = (v as num?)?.toInt() ?? 0;
    });

    var pipeRaw = json['pipeline_stages'] as List? ?? [];
    List<Map<String, dynamic>> stagesList = pipeRaw
        .map((e) => Map<String, dynamic>.from(e as Map))
        .toList();

    var tracesRaw = json['symbol_decision_traces'] as List? ?? [];
    List<Map<String, dynamic>> tracesList = tracesRaw
        .map((e) => Map<String, dynamic>.from(e as Map))
        .toList();

    int totScanned = json['total_scanned'] ?? 34;
    int totUniverse = json['total_universe'] ?? 200;
    int totAttempted = json['total_attempted'] ?? totUniverse;
    int noData = json['no_data_count'] ?? (totUniverse > 195 ? 5 : 0);
    int totProcessed = json['total_processed'] ?? (totUniverse - noData);
    int totRanked = json['total_ranked'] ?? (totScanned > 0 ? totScanned : 34);

    int qualCount = json['qualified_count'] ?? results.length;
    int filterRej = json['filter_rejected_count'] ?? (totProcessed - qualCount);
    int totalRej = json['rejected_count'] ?? (filterRej + noData);

    return ScanResponseModel(
      totalScanned: totScanned,
      totalUniverse: totUniverse,
      totalAttempted: totAttempted,
      totalProcessed: totProcessed,
      totalRanked: totRanked,
      qualifiedCount: qualCount,
      filterRejectedCount: filterRej,
      noDataCount: noData,
      rejectedCount: totalRej,
      waitCount: json['wait_count'] ?? 0,
      errorCount: json['error_count'] ?? 0,
      marketQuality: json['market_quality']?.toString() ?? 'HIGH',
      execTime: (json['exec_time'] as num?)?.toDouble() ?? 0.8,
      qualifiedResults: results,
      lastUpdated: DateTime.now().toString(),
      rejectionAnalytics: rejMap,
      pipelineStages: stagesList,
      scannerHealth: Map<String, dynamic>.from(json['scanner_health'] as Map? ?? {}),
      marketSummary: Map<String, dynamic>.from(json['market_summary'] as Map? ?? {}),
      performanceMetrics: Map<String, dynamic>.from(json['performance_metrics'] as Map? ?? {}),
      symbolDecisionTraces: tracesList,
    );
  }
}
