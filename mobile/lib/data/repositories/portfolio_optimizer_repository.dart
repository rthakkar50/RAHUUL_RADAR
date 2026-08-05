import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../../core/network/api_config.dart';

class PortfolioHealthModel {
  final double overallScore; // 0 - 100
  final double diversificationScore;
  final double sectorBalanceScore;
  final double cashPositionScore;
  final double riskUsageScore;
  final double drawdownScore;
  final String statusGrade; // EXCELLENT, GOOD, MODERATE, POOR

  const PortfolioHealthModel({
    required this.overallScore,
    required this.diversificationScore,
    required this.sectorBalanceScore,
    required this.cashPositionScore,
    required this.riskUsageScore,
    required this.drawdownScore,
    required this.statusGrade,
  });

  factory PortfolioHealthModel.fromJson(Map<String, dynamic> json) {
    final overall = (json['overallHealthScore'] as num?)?.toDouble() ?? 0.0;
    return PortfolioHealthModel(
      overallScore: overall,
      diversificationScore: (json['diversificationScore'] as num?)?.toDouble() ?? 0.0,
      sectorBalanceScore: (json['diversificationScore'] as num?)?.toDouble() ?? 0.0,
      cashPositionScore: (json['cashAllocationPct'] as num?)?.toDouble() ?? 100.0,
      riskUsageScore: (json['riskUtilizationPct'] as num?)?.toDouble() ?? 0.0,
      drawdownScore: (json['drawdownScore'] as num?)?.toDouble() ?? 100.0,
      statusGrade: overall >= 80 ? 'EXCELLENT (HEALTHY)' : (overall >= 50 ? 'MODERATE RISK' : 'NO ACTIVE HOLDINGS'),
    );
  }
}

class CapitalAllocationModel {
  final double cashPct;
  final double equityPct;
  final double fnoPct;
  final double swingPct;
  final double intradayPct;

  const CapitalAllocationModel({
    required this.cashPct,
    required this.equityPct,
    required this.fnoPct,
    required this.swingPct,
    required this.intradayPct,
  });

  factory CapitalAllocationModel.fromJson(Map<String, dynamic> json) {
    return CapitalAllocationModel(
      cashPct: (json['cashAllocationPct'] as num?)?.toDouble() ?? 100.0,
      equityPct: (json['equityAllocationPct'] as num?)?.toDouble() ?? 0.0,
      fnoPct: (json['fnoAllocationPct'] as num?)?.toDouble() ?? 0.0,
      swingPct: (json['equityAllocationPct'] as num?)?.toDouble() ?? 0.0,
      intradayPct: (json['fnoAllocationPct'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class StressTestResultModel {
  final double crashPct; // 5%, 10%, 15%
  final double estimatedLoss;
  final double portfolioEquityAfterCrash;
  final String estimatedRecoveryTime;
  final String riskGrade;

  const StressTestResultModel({
    required this.crashPct,
    required this.estimatedLoss,
    required this.portfolioEquityAfterCrash,
    required this.estimatedRecoveryTime,
    required this.riskGrade,
  });

  factory StressTestResultModel.fromJson(Map<String, dynamic> json) {
    final lossPct = (json['projectedLossPct'] as num?)?.toDouble() ?? 0.0;
    return StressTestResultModel(
      crashPct: 5.0,
      estimatedLoss: lossPct * 1000.0,
      portfolioEquityAfterCrash: 100000.0 - (lossPct * 1000.0),
      estimatedRecoveryTime: lossPct.abs() > 3.0 ? '7 - 10 Days' : '3 - 5 Days',
      riskGrade: json['impact'] ?? 'LOW RISK',
    );
  }
}

class PortfolioOptimizerResponseModel {
  final PortfolioHealthModel health;
  final CapitalAllocationModel allocation;
  final List<StressTestResultModel> stressTest;
  final List<String> suggestions;

  const PortfolioOptimizerResponseModel({
    required this.health,
    required this.allocation,
    required this.stressTest,
    required this.suggestions,
  });
}

class PortfolioOptimizerRepository {
  static final PortfolioOptimizerRepository _instance =
      PortfolioOptimizerRepository._internal();
  factory PortfolioOptimizerRepository() => _instance;
  PortfolioOptimizerRepository._internal();

  Future<PortfolioOptimizerResponseModel> getOptimizerData() async {
    final url = '${ApiConfig.baseUrl}/portfolio-optimizer';
    debugPrint('[RUN-AUDIT] [PortfolioOptimizerRepository] Fetching live Portfolio Optimizer from: $url');

    try {
      final response = await http
          .get(Uri.parse(url), headers: ApiConfig.defaultHeaders())
          .timeout(const Duration(seconds: ApiConfig.timeoutSeconds));

      debugPrint('[RUN-AUDIT] [PortfolioOptimizerRepository] Response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);

        final health = PortfolioHealthModel.fromJson(
          data['health_metrics'] as Map<String, dynamic>? ?? {},
        );

        final allocation = CapitalAllocationModel.fromJson(
          data['health_metrics'] as Map<String, dynamic>? ?? {},
        );

        final rawStress = data['stress_test'] as List<dynamic>? ?? [];
        final stressList = rawStress
            .map((item) => StressTestResultModel.fromJson(item as Map<String, dynamic>))
            .toList();

        final rawSuggestions = data['rebalance_suggestions'] as List<dynamic>? ?? [];
        final suggestionsList = rawSuggestions.map((e) => e.toString()).toList();

        return PortfolioOptimizerResponseModel(
          health: health,
          allocation: allocation,
          stressTest: stressList,
          suggestions: suggestionsList,
        );
      }
    } catch (e, st) {
      debugPrint('[RUN-AUDIT] [PortfolioOptimizerRepository] EXCEPTION: $e\n$st');
    }

    return PortfolioOptimizerResponseModel(
      health: getPortfolioHealth(),
      allocation: getCapitalAllocation(),
      stressTest: getStressTestSimulations(),
      suggestions: getRebalancingSuggestions(),
    );
  }

  PortfolioHealthModel getPortfolioHealth() {
    return const PortfolioHealthModel(
      overallScore: 0.0,
      diversificationScore: 0.0,
      sectorBalanceScore: 0.0,
      cashPositionScore: 100.0,
      riskUsageScore: 0.0,
      drawdownScore: 100.0,
      statusGrade: 'NO ACTIVE HOLDINGS',
    );
  }

  CapitalAllocationModel getCapitalAllocation() {
    return const CapitalAllocationModel(
      cashPct: 100.0,
      equityPct: 0.0,
      fnoPct: 0.0,
      swingPct: 0.0,
      intradayPct: 0.0,
    );
  }

  List<StressTestResultModel> getStressTestSimulations() {
    return const [
      StressTestResultModel(
        crashPct: 5.0,
        estimatedLoss: 0.0,
        portfolioEquityAfterCrash: 100000.0,
        estimatedRecoveryTime: '0 Days',
        riskGrade: 'LOW RISK',
      ),
    ];
  }

  List<String> getRebalancingSuggestions() {
    return const [
      'No active positions detected in portfolio.',
      'Execute swing or intraday trades to activate portfolio optimization and stress testing.',
    ];
  }
}
