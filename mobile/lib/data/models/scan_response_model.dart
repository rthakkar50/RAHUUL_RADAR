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
  final double? scanTimestamp;
  final double? serverTimestamp;
  final String? dataTimestamp;
  final double? cacheAgeSeconds;
  final bool isStale;
  final bool isScanning;
  final String provider;
  final String providerHealth;
  final bool fallbackUsed;
  final bool paytmAuthenticated;
  final String marketStatus;
  final double? providerLatency;
  final String status;
  final Map<String, int> rejectionAnalytics;
  final List<Map<String, dynamic>> pipelineStages;
  final Map<String, dynamic> scannerHealth;
  final Map<String, dynamic> marketSummary;
  final Map<String, dynamic> performanceMetrics;
  final List<Map<String, dynamic>> symbolDecisionTraces;

  ScanResponseModel({
    required this.totalScanned,
    required this.totalUniverse,
    this.totalAttempted = 0,
    this.totalProcessed = 0,
    this.totalRanked = 0,
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
    this.scanTimestamp,
    this.serverTimestamp,
    this.dataTimestamp,
    this.cacheAgeSeconds,
    this.isStale = true,
    this.isScanning = false,
    this.provider = 'UNKNOWN',
    this.providerHealth = 'UNKNOWN',
    this.fallbackUsed = false,
    this.paytmAuthenticated = false,
    this.marketStatus = 'UNKNOWN',
    this.providerLatency,
    this.status = 'UNKNOWN',
    this.rejectionAnalytics = const {},
    this.pipelineStages = const [],
    this.scannerHealth = const {},
    this.marketSummary = const {},
    this.performanceMetrics = const {},
    this.symbolDecisionTraces = const [],
  });

  String get timestamp => lastUpdated;

  String get formattedCacheAge {
    final age = cacheAgeSeconds;
    if (age == null || !age.isFinite || age < 0) return 'UNKNOWN';
    if (age < 60) return '${age.toStringAsFixed(0)}s';
    if (age < 3600) return '${(age / 60).toStringAsFixed(1)}m';
    return '${(age / 3600).toStringAsFixed(1)}h';
  }

  static double? _parseEpochSeconds(dynamic raw) {
    if (raw == null) return null;
    if (raw is num) {
      final val = raw.toDouble();
      if (!val.isFinite || val <= 0) return null;
      // Handle millisecond timestamps if > 1e11
      return val > 100000000000 ? val / 1000.0 : val;
    }
    if (raw is String) {
      final trimmed = raw.trim();
      if (trimmed.isEmpty) return null;
      final numVal = double.tryParse(trimmed);
      if (numVal != null && numVal.isFinite && numVal > 0) {
        return numVal > 100000000000 ? numVal / 1000.0 : numVal;
      }
      final parsedDt = DateTime.tryParse(trimmed);
      if (parsedDt != null) {
        return parsedDt.millisecondsSinceEpoch / 1000.0;
      }
    }
    return null;
  }

  static String _formatIstEpoch(double epochSeconds) {
    try {
      final utc = DateTime.fromMillisecondsSinceEpoch(
        (epochSeconds * 1000).round(),
        isUtc: true,
      );
      final ist = utc.add(const Duration(hours: 5, minutes: 30));
      final y = ist.year.toString().padLeft(4, '0');
      final m = ist.month.toString().padLeft(2, '0');
      final d = ist.day.toString().padLeft(2, '0');
      final hh = ist.hour.toString().padLeft(2, '0');
      final mm = ist.minute.toString().padLeft(2, '0');
      final ss = ist.second.toString().padLeft(2, '0');
      return '$y-$m-$d $hh:$mm:$ss IST';
    } catch (_) {
      return 'UNAVAILABLE';
    }
  }

  factory ScanResponseModel.fromJson(Map<String, dynamic> json) {
    var list = (json['qualified_results'] ?? json['results'] ?? json['data']) as List? ?? [];
    List<ScanResultModel> results = list
        .whereType<Map>()
        .map((i) => ScanResultModel.fromJson(Map<String, dynamic>.from(i)))
        .toList();

    var rejRaw = json['rejection_analytics'] as Map<String, dynamic>? ?? {};
    Map<String, int> rejMap = {};
    rejRaw.forEach((k, v) {
      rejMap[k] = (v as num?)?.toInt() ?? 0;
    });

    var pipeRaw = json['pipeline_stages'] as List? ?? [];
    List<Map<String, dynamic>> stagesList = pipeRaw
        .whereType<Map>()
        .map((e) => Map<String, dynamic>.from(e))
        .toList();

    var tracesRaw = json['symbol_decision_traces'] as List? ?? [];
    List<Map<String, dynamic>> tracesList = tracesRaw
        .whereType<Map>()
        .map((e) => Map<String, dynamic>.from(e))
        .toList();

    int totScanned = (json['total_scanned'] as num?)?.toInt() ?? 0;
    int totUniverse = (json['total_universe'] as num?)?.toInt() ?? 0;
    int totAttempted = (json['total_attempted'] as num?)?.toInt() ?? totScanned;
    int noData = (json['no_data_count'] as num?)?.toInt() ?? 0;
    int totProcessed = (json['total_processed'] as num?)?.toInt() ?? totScanned;
    int totRanked = (json['total_ranked'] as num?)?.toInt() ?? totScanned;

    int qualCount = (json['qualified_count'] as num?)?.toInt() ?? results.length;
    int filterRej = (json['filter_rejected_count'] as num?)?.toInt() ??
        (totProcessed >= qualCount ? (totProcessed - qualCount) : 0);
    int totalRej = (json['rejected_count'] as num?)?.toInt() ?? (filterRej + noData);

    final double? serverTs = _parseEpochSeconds(json['server_timestamp']);
    double? scanTs = _parseEpochSeconds(json['scan_timestamp']) ??
        _parseEpochSeconds(json['cache_timestamp']);
    if (scanTs == null &&
        !json.containsKey('scan_timestamp') &&
        !json.containsKey('cache_timestamp')) {
      final rawTs = _parseEpochSeconds(json['timestamp']);
      if (rawTs != null && (serverTs == null || (rawTs - serverTs).abs() > 0.001)) {
        scanTs = rawTs;
      }
    }

    String? dataTs = json['data_timestamp']?.toString().trim();
    if (dataTs != null && (dataTs.isEmpty || dataTs.toUpperCase() == 'LIVE')) {
      dataTs = null;
    }
    if (dataTs == null && results.isNotEmpty) {
      for (final r in results) {
        final rawItemTs = r.timestamp.split(' | ').first.trim();
        if (rawItemTs.isNotEmpty &&
            rawItemTs.toUpperCase() != 'LIVE' &&
            rawItemTs.toUpperCase() != 'UNAVAILABLE') {
          if (dataTs == null || rawItemTs.compareTo(dataTs) > 0) {
            dataTs = rawItemTs;
          }
        }
      }
    }

    double? cacheAge = (json['cache_age_seconds'] as num?)?.toDouble();
    if (cacheAge != null && (!cacheAge.isFinite || cacheAge < 0)) {
      cacheAge = null;
    }
    if (cacheAge == null && scanTs != null && serverTs != null && serverTs >= scanTs) {
      cacheAge = serverTs - scanTs;
    }

    final bool isScanning = (json['is_scanning'] == true) ||
        (json['status']?.toString().toUpperCase() == 'SCANNING');

    final bool isStale = (json['is_stale'] is bool)
        ? (json['is_stale'] as bool)
        : (scanTs == null || cacheAge == null || cacheAge > 300.0);

    String formattedLastUpdated = 'UNAVAILABLE';
    if (scanTs != null) {
      formattedLastUpdated = _formatIstEpoch(scanTs);
    } else if (dataTs != null && dataTs.isNotEmpty) {
      formattedLastUpdated = dataTs;
    }

    final String provider = (json['provider']?.toString().trim().isNotEmpty ?? false)
        ? json['provider'].toString().trim()
        : 'UNKNOWN';
    final String providerHealth = (json['provider_health']?.toString().trim().isNotEmpty ?? false)
        ? json['provider_health'].toString().trim().toUpperCase()
        : 'UNKNOWN';
    final bool fallbackUsed = json['fallback_used'] == true ||
        provider.toUpperCase().contains('FALLBACK') ||
        provider.toUpperCase().contains('YAHOO');
    final bool paytmAuthenticated = json['paytm_authenticated'] == true;
    final String marketStatus = (json['market_status']?.toString().trim().isNotEmpty ?? false)
        ? json['market_status'].toString().trim().toUpperCase()
        : 'UNKNOWN';
    final double? providerLatency = (json['provider_latency'] as num?)?.toDouble();
    final String status = (json['status']?.toString().trim().isNotEmpty ?? false)
        ? json['status'].toString().trim().toUpperCase()
        : 'UNKNOWN';

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
      waitCount: (json['wait_count'] as num?)?.toInt() ?? 0,
      errorCount: (json['error_count'] as num?)?.toInt() ?? 0,
      marketQuality: json['market_quality']?.toString() ?? 'UNAVAILABLE',
      execTime: (json['exec_time'] as num?)?.toDouble() ?? 0.0,
      qualifiedResults: results,
      lastUpdated: formattedLastUpdated,
      scanTimestamp: scanTs,
      serverTimestamp: serverTs,
      dataTimestamp: dataTs,
      cacheAgeSeconds: cacheAge,
      isStale: isStale,
      isScanning: isScanning,
      provider: provider,
      providerHealth: providerHealth,
      fallbackUsed: fallbackUsed,
      paytmAuthenticated: paytmAuthenticated,
      marketStatus: marketStatus,
      providerLatency: providerLatency,
      status: status,
      rejectionAnalytics: rejMap,
      pipelineStages: stagesList,
      scannerHealth: Map<String, dynamic>.from(json['scanner_health'] as Map? ?? {}),
      marketSummary: Map<String, dynamic>.from(json['market_summary'] as Map? ?? {}),
      performanceMetrics: Map<String, dynamic>.from(json['performance_metrics'] as Map? ?? {}),
      symbolDecisionTraces: tracesList,
    );
  }
}
