import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../data/models/paper_trade_model.dart';
import '../../data/models/scan_result_model.dart';

class PaperTradingEngine extends ChangeNotifier {
  static final PaperTradingEngine _instance = PaperTradingEngine._internal();
  static PaperTradingEngine get instance => _instance;

  PaperTradingEngine._internal();

  static const String keyStartingCapital = 'paper_starting_capital';
  static const String keyOpenTrades = 'paper_open_trades_v2';
  static const String keyClosedTrades = 'paper_closed_trades_v2';

  double _startingCapital = 100000.0; // ₹100,000 default virtual capital
  double _availableCash = 100000.0;
  List<PaperTradeModel> _openTrades = [];
  List<PaperTradeModel> _closedTrades = [];

  double get startingCapital => _startingCapital;
  double get availableCash => _availableCash;
  List<PaperTradeModel> get openTrades => List.unmodifiable(_openTrades);
  List<PaperTradeModel> get closedTrades => List.unmodifiable(_closedTrades);

  double get usedCapital => _openTrades.fold(0.0, (sum, t) => sum + t.capitalUsed);
  double get totalUnrealizedPnL => _openTrades.fold(0.0, (sum, t) => sum + t.unrealizedPnL);
  double get totalRealizedPnL => _closedTrades.fold(0.0, (sum, t) => sum + t.netPnL);

  double get totalPortfolioValue => _availableCash + usedCapital + totalUnrealizedPnL;
  double get totalReturnPct => _startingCapital == 0 ? 0.0 : ((totalPortfolioValue - _startingCapital) / _startingCapital) * 100;

  int get totalTradesCount => _closedTrades.length;
  int get winningTradesCount => _closedTrades.where((t) => t.netPnL > 0).length;
  int get losingTradesCount => _closedTrades.where((t) => t.netPnL < 0).length;
  double get winRatePct => totalTradesCount == 0 ? 0.0 : (winningTradesCount / totalTradesCount) * 100;

  double get profitFactor {
    final grossProfit = _closedTrades.where((t) => t.netPnL > 0).fold(0.0, (sum, t) => sum + t.netPnL);
    final grossLoss = _closedTrades.where((t) => t.netPnL < 0).fold(0.0, (sum, t) => sum + t.netPnL.abs());
    if (grossLoss == 0) return grossProfit > 0 ? 99.9 : 0.0;
    return grossProfit / grossLoss;
  }

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _startingCapital = prefs.getDouble(keyStartingCapital) ?? 100000.0;
    _availableCash = _startingCapital;

    final openJsonStr = prefs.getString(keyOpenTrades);
    if (openJsonStr != null) {
      try {
        final List list = json.decode(openJsonStr);
        _openTrades = list.map((e) => PaperTradeModel.fromJson(e)).toList();
      } catch (e) {
        debugPrint('[PaperTradingEngine] Error loading open trades: $e');
      }
    }

    final closedJsonStr = prefs.getString(keyClosedTrades);
    if (closedJsonStr != null) {
      try {
        final List list = json.decode(closedJsonStr);
        _closedTrades = list.map((e) => PaperTradeModel.fromJson(e)).toList();
      } catch (e) {
        debugPrint('[PaperTradingEngine] Error loading closed trades: $e');
      }
    }

    _recalculateCash();
    notifyListeners();
  }

  void _recalculateCash() {
    final used = usedCapital;
    _availableCash = _startingCapital + totalRealizedPnL - used;
  }

  Future<bool> executePaperTradeFromScanner(
    ScanResultModel scannerItem, {
    int? requestedQty,
    double? riskAllocationPct,
    String notes = '',
  }) async {
    final qty = requestedQty ?? _calculateRecommendedQty(scannerItem, allocationPct: riskAllocationPct ?? 0.10);
    final capitalRequired = scannerItem.entry * qty;

    if (capitalRequired > _availableCash) {
      debugPrint('[PaperTradingEngine] Insufficient cash for trade: ₹$capitalRequired required, ₹$_availableCash available');
      return false;
    }

    final trade = PaperTradeModel(
      id: 'PT_${DateTime.now().millisecondsSinceEpoch}',
      symbol: scannerItem.symbol,
      signal: scannerItem.signal,
      sector: scannerItem.sector,
      entryPrice: scannerItem.entry,
      currentPrice: scannerItem.entry,
      quantity: qty,
      stopLoss: scannerItem.stopLoss,
      target1: scannerItem.target1,
      target2: scannerItem.target2,
      riskReward: double.tryParse(scannerItem.riskReward.replaceAll(RegExp(r'[^0-9.]'), '')) ?? 2.0,
      strategy: 'Scanner Automation',
      entryTime: DateTime.now(),
      notes: notes,
    );

    _openTrades.add(trade);
    _recalculateCash();
    await _saveState();
    notifyListeners();
    return true;
  }

  int _calculateRecommendedQty(ScanResultModel item, {double allocationPct = 0.10}) {
    final targetCapital = _startingCapital * allocationPct;
    final qty = (targetCapital / item.entry).floor();
    return qty > 0 ? qty : 1;
  }

  Future<void> closePosition(String tradeId, {double? customExitPrice}) async {
    final idx = _openTrades.indexWhere((t) => t.id == tradeId);
    if (idx == -1) return;

    final trade = _openTrades[idx];
    trade.exitPrice = customExitPrice ?? trade.currentPrice;
    trade.exitTime = DateTime.now();
    trade.status = PaperTradeStatus.closed;

    _openTrades.removeAt(idx);
    _closedTrades.insert(0, trade);

    _recalculateCash();
    await _saveState();
    notifyListeners();
  }

  Future<void> updateMarketPrices(Map<String, double> latestPrices) async {
    bool updated = false;
    for (final trade in _openTrades) {
      if (latestPrices.containsKey(trade.symbol)) {
        trade.currentPrice = latestPrices[trade.symbol]!;
        updated = true;
      }
    }
    if (updated) {
      _recalculateCash();
      await _saveState();
      notifyListeners();
    }
  }

  Future<void> resetVirtualAccount({double capital = 100000.0}) async {
    _startingCapital = capital;
    _availableCash = capital;
    _openTrades.clear();
    _closedTrades.clear();

    final prefs = await SharedPreferences.getInstance();
    await prefs.setDouble(keyStartingCapital, capital);
    await prefs.remove(keyOpenTrades);
    await prefs.remove(keyClosedTrades);

    notifyListeners();
  }

  Future<void> _saveState() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(keyOpenTrades, json.encode(_openTrades.map((t) => t.toJson()).toList()));
    await prefs.setString(keyClosedTrades, json.encode(_closedTrades.map((t) => t.toJson()).toList()));
  }
}
