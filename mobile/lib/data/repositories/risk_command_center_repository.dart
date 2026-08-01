class RiskOverviewModel {
  final double portfolioRiskPct;
  final double capitalUtilizationPct;
  final double marginUtilizationPct;
  final double maxDrawdownPct;
  final double openRiskAmount;
  final String riskGrade;
  final String capitalEfficiencyScore;

  const RiskOverviewModel({
    required this.portfolioRiskPct,
    required this.capitalUtilizationPct,
    required this.marginUtilizationPct,
    required this.maxDrawdownPct,
    required this.openRiskAmount,
    required this.riskGrade,
    required this.capitalEfficiencyScore,
  });
}

class PositionRiskHeatmapModel {
  final String symbol;
  final String sector;
  final double exposurePct;
  final String riskLevel; // LOW, MODERATE, HIGH, CRITICAL
  final String colorCode; // GREEN, YELLOW, ORANGE, RED

  const PositionRiskHeatmapModel({
    required this.symbol,
    required this.sector,
    required this.exposurePct,
    required this.riskLevel,
    required this.colorCode,
  });
}

class StressTestScenarioModel {
  final String scenarioName;
  final double estimatedLossAmount;
  final double portfolioSurvivalPct;
  final String recoveryTimeDays;
  final String severity;

  const StressTestScenarioModel({
    required this.scenarioName,
    required this.estimatedLossAmount,
    required this.portfolioSurvivalPct,
    required this.recoveryTimeDays,
    required this.severity,
  });
}

class RiskCommandCenterRepository {
  static final RiskCommandCenterRepository _instance = RiskCommandCenterRepository._internal();
  factory RiskCommandCenterRepository() => _instance;
  RiskCommandCenterRepository._internal();

  RiskOverviewModel getRiskOverview() {
    return const RiskOverviewModel(
      portfolioRiskPct: 0.69,
      capitalUtilizationPct: 72.3,
      marginUtilizationPct: 54.0,
      maxDrawdownPct: 2.1,
      openRiskAmount: 6548.20,
      riskGrade: 'A+ (LOW RISK)',
      capitalEfficiencyScore: '94.2 / 100',
    );
  }

  List<PositionRiskHeatmapModel> getPositionHeatmap() {
    return const [
      PositionRiskHeatmapModel(symbol: 'DIVISLAB', sector: 'PHARMA', exposurePct: 18.5, riskLevel: 'MODERATE', colorCode: 'YELLOW'),
      PositionRiskHeatmapModel(symbol: 'DIXON', sector: 'CONSUMER', exposurePct: 14.2, riskLevel: 'LOW', colorCode: 'GREEN'),
      PositionRiskHeatmapModel(symbol: 'TATAMOTORS', sector: 'AUTO', exposurePct: 12.0, riskLevel: 'LOW', colorCode: 'GREEN'),
      PositionRiskHeatmapModel(symbol: 'RELIANCE', sector: 'ENERGY', exposurePct: 15.0, riskLevel: 'LOW', colorCode: 'GREEN'),
      PositionRiskHeatmapModel(symbol: 'PAYTM', sector: 'FINANCIAL', exposurePct: 12.6, riskLevel: 'MODERATE', colorCode: 'YELLOW'),
    ];
  }

  List<StressTestScenarioModel> getStressScenarios() {
    return const [
      StressTestScenarioModel(scenarioName: 'Nifty -5% Gap Down', estimatedLossAmount: 14850.0, portfolioSurvivalPct: 99.8, recoveryTimeDays: '3 Days', severity: 'MILD'),
      StressTestScenarioModel(scenarioName: 'Nifty -10% Crash', estimatedLossAmount: 31200.0, portfolioSurvivalPct: 99.5, recoveryTimeDays: '8 Days', severity: 'MODERATE'),
      StressTestScenarioModel(scenarioName: 'India VIX +50% Spike', estimatedLossAmount: 18400.0, portfolioSurvivalPct: 99.7, recoveryTimeDays: '4 Days', severity: 'MANAGED'),
      StressTestScenarioModel(scenarioName: 'Black Swan (-15% Panic)', estimatedLossAmount: 48900.0, portfolioSurvivalPct: 99.4, recoveryTimeDays: '14 Days', severity: 'HIGH'),
    ];
  }

  List<String> getHedgingSuggestions() {
    return const [
      'INDEX HEDGE: Buy NIFTY 24,500 PE (1 Lot) for ₹3,400 to hedge ₹7.2L equity exposure.',
      'CASH HEDGE: Maintain current cash buffer of 27.6% (₹2,76,405).',
      'PORTFOLIO HEDGE SCORE: 88.5 / 100 (WELL PROTECTED).',
    ];
  }
}
