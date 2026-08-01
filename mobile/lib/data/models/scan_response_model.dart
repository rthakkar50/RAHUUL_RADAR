import 'scan_result_model.dart';

class ScanResponseModel {
  final int totalScanned;
  final int totalUniverse;
  final int waitCount;
  final int noDataCount;
  final int errorCount;
  final String marketQuality;
  final double execTime;
  final List<ScanResultModel> qualifiedResults;
  final String lastUpdated;

  ScanResponseModel({
    required this.totalScanned,
    required this.totalUniverse,
    required this.waitCount,
    required this.noDataCount,
    required this.errorCount,
    required this.marketQuality,
    required this.execTime,
    required this.qualifiedResults,
    required this.lastUpdated,
  });

  factory ScanResponseModel.fromJson(Map<String, dynamic> json) {
    var list = json['qualified_results'] as List? ?? [];
    List<ScanResultModel> results = list
        .map((i) => ScanResultModel.fromJson(i))
        .toList();

    return ScanResponseModel(
      totalScanned: json['total_scanned'] ?? 0,
      totalUniverse: json['total_universe'] ?? 0,
      waitCount: json['wait_count'] ?? 0,
      noDataCount: json['no_data_count'] ?? 0,
      errorCount: json['error_count'] ?? 0,
      marketQuality: json['market_quality']?.toString() ?? 'Unknown',
      execTime: (json['exec_time'] as num?)?.toDouble() ?? 0.0,
      qualifiedResults: results,
      lastUpdated: DateTime.now()
          .toString(), // Storing client side time of fetch
    );
  }
}
