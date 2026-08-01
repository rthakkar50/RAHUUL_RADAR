class OptionGreekModel {
  final double delta;
  final double gamma;
  final double theta;
  final double vega;
  final double rho;

  const OptionGreekModel({
    required this.delta,
    required this.gamma,
    required this.theta,
    required this.vega,
    required this.rho,
  });
}

class OptionChainStrikeModel {
  final double strike;
  final double callPrice;
  final double callOi;
  final double callOiChange;
  final double callIv;
  final OptionGreekModel callGreeks;
  final double putPrice;
  final double putOi;
  final double putOiChange;
  final double putIv;
  final OptionGreekModel putGreeks;
  final String
  buildupType; // Long Build-up, Short Build-up, Short Covering, Long Unwinding

  const OptionChainStrikeModel({
    required this.strike,
    required this.callPrice,
    required this.callOi,
    required this.callOiChange,
    required this.callIv,
    required this.callGreeks,
    required this.putPrice,
    required this.putOi,
    required this.putOiChange,
    required this.putIv,
    required this.putGreeks,
    required this.buildupType,
  });
}

class FnoOverviewModel {
  final String symbol;
  final double spotPrice;
  final double pcr;
  final double maxPain;
  final double ivRank;
  final double ivPercentile;
  final String expiryDate;
  final double marginRequired;
  final List<OptionChainStrikeModel> optionChain;

  const FnoOverviewModel({
    required this.symbol,
    required this.spotPrice,
    required this.pcr,
    required this.maxPain,
    required this.ivRank,
    required this.ivPercentile,
    required this.expiryDate,
    required this.marginRequired,
    required this.optionChain,
  });
}
