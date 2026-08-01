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
}

class PortfolioOptimizerRepository {
  static final PortfolioOptimizerRepository _instance =
      PortfolioOptimizerRepository._internal();
  factory PortfolioOptimizerRepository() => _instance;
  PortfolioOptimizerRepository._internal();

  PortfolioHealthModel getPortfolioHealth() {
    return const PortfolioHealthModel(
      overallScore: 91.5,
      diversificationScore: 88.0,
      sectorBalanceScore: 85.0,
      cashPositionScore: 94.0,
      riskUsageScore: 95.0,
      drawdownScore: 92.0,
      statusGrade: 'EXCELLENT (HEALTHY)',
    );
  }

  CapitalAllocationModel getCapitalAllocation() {
    return const CapitalAllocationModel(
      cashPct: 27.6,
      equityPct: 42.4,
      fnoPct: 30.0,
      swingPct: 50.0,
      intradayPct: 20.0,
    );
  }

  List<StressTestResultModel> getStressTestSimulations() {
    return const [
      StressTestResultModel(
        crashPct: 5.0,
        estimatedLoss: 14850.0,
        portfolioEquityAfterCrash: 978251.13,
        estimatedRecoveryTime: '3 - 5 Days',
        riskGrade: 'LOW RISK',
      ),
      StressTestResultModel(
        crashPct: 10.0,
        estimatedLoss: 31200.0,
        portfolioEquityAfterCrash: 961901.13,
        estimatedRecoveryTime: '7 - 10 Days',
        riskGrade: 'MODERATE RISK',
      ),
      StressTestResultModel(
        crashPct: 15.0,
        estimatedLoss: 48900.0,
        portfolioEquityAfterCrash: 944201.13,
        estimatedRecoveryTime: '12 - 18 Days',
        riskGrade: 'MANAGED RISK',
      ),
    ];
  }

  List<String> getRebalancingSuggestions() {
    return const [
      'REDUCE PHARMA: Concentration exceeds 30% limit (Current 35%). Trim DIVISLAB by 10%.',
      'INCREASE IT: Underweight tier (Current 12%). Add TCS or INFY on dip.',
      'ADD BANKING: Sector momentum index high. Allocate 5% to HDFCBANK.',
      'MAINTAIN CASH: Current cash buffer of 27.6% (₹2,76,405) provides optimal buying power.',
    ];
  }
}
