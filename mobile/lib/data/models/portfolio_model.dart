class PortfolioSummaryModel {
  final double startingCapital;
  final double totalCapital;
  final double availableCash;
  final double usedMargin;
  final double unrealizedPnl;
  final double realizedPnl;
  final double todayPnl;
  final double totalEquity;
  final double overallReturnPct;

  const PortfolioSummaryModel({
    required this.startingCapital,
    required this.totalCapital,
    required this.availableCash,
    required this.usedMargin,
    required this.unrealizedPnl,
    required this.realizedPnl,
    required this.todayPnl,
    required this.totalEquity,
    required this.overallReturnPct,
  });

  factory PortfolioSummaryModel.fromJson(Map<String, dynamic> j) =>
      PortfolioSummaryModel(
        startingCapital:  (j['starting_capital']  as num?)?.toDouble() ?? 1000000.0,
        totalCapital:     (j['total_capital']      as num?)?.toDouble() ?? 1000000.0,
        availableCash:    (j['available_cash']     as num?)?.toDouble() ?? 1000000.0,
        usedMargin:       (j['used_margin']        as num?)?.toDouble() ?? 0.0,
        unrealizedPnl:    (j['unrealized_pnl']     as num?)?.toDouble() ?? 0.0,
        realizedPnl:      (j['realized_pnl']       as num?)?.toDouble() ?? 0.0,
        todayPnl:         (j['today_pnl']          as num?)?.toDouble() ?? 0.0,
        totalEquity:      (j['total_equity']       as num?)?.toDouble() ?? 1000000.0,
        overallReturnPct: (j['overall_return_pct'] as num?)?.toDouble() ?? 0.0,
      );

  double get buyingPower => availableCash;
}

class PositionModel {
  final String id;
  final String symbol;
  final String direction;
  final String exchange;
  final int qty;
  final double entryPrice;
  final double cmp;
  final double sl;
  final double target;
  final double unrealizedPnl;
  final double usedMargin;
  final String entryTime;
  final String riskReward;
  final String status;

  const PositionModel({
    required this.id,
    required this.symbol,
    required this.direction,
    required this.exchange,
    required this.qty,
    required this.entryPrice,
    required this.cmp,
    required this.sl,
    required this.target,
    required this.unrealizedPnl,
    required this.usedMargin,
    required this.entryTime,
    required this.riskReward,
    required this.status,
  });

  factory PositionModel.fromJson(Map<String, dynamic> j) => PositionModel(
        id:            j['id']?.toString()        ?? '',
        symbol:        j['symbol']?.toString()    ?? '',
        direction:     j['direction']?.toString() ?? 'BUY',
        exchange:      j['exchange']?.toString()  ?? 'NSE',
        qty:           (j['qty'] as num?)?.toInt() ?? 0,
        entryPrice:    (j['entry_price'] as num?)?.toDouble() ?? 0.0,
        cmp:           (j['cmp']         as num?)?.toDouble() ?? 0.0,
        sl:            (j['sl']          as num?)?.toDouble() ?? 0.0,
        target:        (j['target']      as num?)?.toDouble() ?? 0.0,
        unrealizedPnl: (j['unrealized_pnl'] as num?)?.toDouble() ?? 0.0,
        usedMargin:    (j['used_margin']    as num?)?.toDouble() ?? 0.0,
        entryTime:     j['entry_time']?.toString() ?? '',
        riskReward:    j['risk_reward']?.toString() ?? 'N/A',
        status:        j['status']?.toString() ?? 'OPEN',
      );

  double get pnlPct =>
      entryPrice > 0 ? (unrealizedPnl / (entryPrice * qty) * 100) : 0.0;
}

class ClosedPositionModel {
  final String id;
  final String symbol;
  final String direction;
  final double entryPrice;
  final double exitPrice;
  final double pnl;
  final String entryTime;
  final String exitTime;
  final double returnPct;

  const ClosedPositionModel({
    required this.id,
    required this.symbol,
    required this.direction,
    required this.entryPrice,
    required this.exitPrice,
    required this.pnl,
    required this.entryTime,
    required this.exitTime,
    required this.returnPct,
  });

  factory ClosedPositionModel.fromJson(Map<String, dynamic> j) =>
      ClosedPositionModel(
        id:         j['id']?.toString()        ?? '',
        symbol:     j['symbol']?.toString()    ?? '',
        direction:  j['direction']?.toString() ?? 'BUY',
        entryPrice: (j['entry_price'] as num?)?.toDouble() ?? 0.0,
        exitPrice:  (j['exit_price']  as num?)?.toDouble() ?? 0.0,
        pnl:        (j['pnl']         as num?)?.toDouble() ?? 0.0,
        entryTime:  j['entry_time']?.toString() ?? '',
        exitTime:   j['exit_time']?.toString()  ?? '',
        returnPct:  (j['return_pct'] as num?)?.toDouble() ?? 0.0,
      );

  String get holdingDays {
    try {
      if (entryTime.isEmpty || exitTime.isEmpty) return 'N/A';
      final d1 = DateTime.parse(entryTime.split('.').first);
      final d2 = DateTime.parse(exitTime.split('.').first);
      final diff = d2.difference(d1);
      if (diff.inHours < 24) return 'Intraday';
      return '${diff.inDays} Days';
    } catch (_) {
      return 'N/A';
    }
  }
}

class InsightItemModel {
  final String symbol;
  final double value;
  const InsightItemModel({required this.symbol, required this.value});

  factory InsightItemModel.fromJson(Map<String, dynamic>? j, String valueKey) {
    if (j == null) return const InsightItemModel(symbol: '--', value: 0.0);
    return InsightItemModel(
      symbol: j['symbol']?.toString() ?? '--',
      value:  (j[valueKey] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class PortfolioInsightsModel {
  final InsightItemModel topWinner;
  final InsightItemModel topLoser;
  final InsightItemModel largestPosition;
  final InsightItemModel highestProfit;
  final InsightItemModel highestLoss;

  const PortfolioInsightsModel({
    required this.topWinner,
    required this.topLoser,
    required this.largestPosition,
    required this.highestProfit,
    required this.highestLoss,
  });

  factory PortfolioInsightsModel.fromJson(Map<String, dynamic> j) =>
      PortfolioInsightsModel(
        topWinner:       InsightItemModel.fromJson(j['top_winner']       as Map<String, dynamic>?, 'pnl'),
        topLoser:        InsightItemModel.fromJson(j['top_loser']        as Map<String, dynamic>?, 'pnl'),
        largestPosition: InsightItemModel.fromJson(j['largest_position'] as Map<String, dynamic>?, 'margin'),
        highestProfit:   InsightItemModel.fromJson(j['highest_profit']   as Map<String, dynamic>?, 'pnl'),
        highestLoss:     InsightItemModel.fromJson(j['highest_loss']     as Map<String, dynamic>?, 'pnl'),
      );
}

class PortfolioResponseModel {
  final PortfolioSummaryModel summary;
  final List<PositionModel> openPositions;
  final List<ClosedPositionModel> closedPositions;
  final PortfolioInsightsModel insights;

  const PortfolioResponseModel({
    required this.summary,
    required this.openPositions,
    required this.closedPositions,
    required this.insights,
  });

  factory PortfolioResponseModel.fromJson(Map<String, dynamic> j) =>
      PortfolioResponseModel(
        summary: PortfolioSummaryModel.fromJson(
            (j['summary'] as Map<String, dynamic>?) ?? {}),
        openPositions: ((j['open_positions'] as List?) ?? [])
            .map((e) => PositionModel.fromJson(e as Map<String, dynamic>))
            .toList(),
        closedPositions: ((j['closed_positions'] as List?) ?? [])
            .map((e) => ClosedPositionModel.fromJson(e as Map<String, dynamic>))
            .toList(),
        insights: PortfolioInsightsModel.fromJson(
            (j['insights'] as Map<String, dynamic>?) ?? {}),
      );
}
