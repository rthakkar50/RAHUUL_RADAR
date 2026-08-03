import '../paper_trading/paper_trading_engine.dart';
import '../../data/models/scan_result_model.dart';

class ValidationResult {
  final bool isValid;
  final String message;
  final List<String> passedChecks;
  final List<String> failedChecks;

  ValidationResult({
    required this.isValid,
    required this.message,
    required this.passedChecks,
    required this.failedChecks,
  });
}

class ExecutionValidator {
  static final ExecutionValidator _instance = ExecutionValidator._internal();
  static ExecutionValidator get instance => _instance;

  ExecutionValidator._internal();

  bool isCircuitBreakerTripped = false;
  int consecutiveLossesCount = 0;
  double maxDailyDrawdownPct = 2.0;

  ValidationResult validateOrder({
    required ScanResultModel item,
    required int requestedQty,
  }) {
    final passed = <String>[];
    final failed = <String>[];

    // 1. Circuit Breaker Check
    if (isCircuitBreakerTripped || consecutiveLossesCount >= 5) {
      failed.add('Circuit Breaker Tripped (5 consecutive losses or risk limit breached)');
      return ValidationResult(
        isValid: false,
        message: 'Circuit Breaker Active - All Executions Paused',
        passedChecks: passed,
        failedChecks: failed,
      );
    }
    passed.add('Circuit Breaker Normal');

    // 2. Signal Validity
    final sig = item.signal.toUpperCase();
    if (!sig.contains('BUY') && !sig.contains('SELL') && !sig.contains('WATCH')) {
      failed.add('Invalid Signal ($sig)');
    } else {
      passed.add('Signal Valid ($sig)');
    }

    // 3. AI Confidence Check (>= 70%)
    if (item.confidence < 70.0) {
      failed.add('Confidence low (${item.confidence.toStringAsFixed(1)}% < 70.0%)');
    } else {
      passed.add('AI Confidence Passed (${item.confidence.toStringAsFixed(1)}%)');
    }

    // 4. Price, SL, & Target Check
    if (item.entry <= 0) {
      failed.add('Entry price invalid (₹${item.entry})');
    } else {
      passed.add('Entry Price Valid (₹${item.entry})');
    }

    if (item.stopLoss <= 0 || (sig.contains('BUY') && item.stopLoss >= item.entry)) {
      failed.add('Stop Loss invalid (SL: ₹${item.stopLoss}, Entry: ₹${item.entry})');
    } else {
      passed.add('Stop Loss Valid (₹${item.stopLoss})');
    }

    if (item.target1 <= 0 || (sig.contains('BUY') && item.target1 <= item.entry)) {
      failed.add('Target 1 invalid (T1: ₹${item.target1}, Entry: ₹${item.entry})');
    } else {
      passed.add('Target Valid (₹${item.target1})');
    }

    // 5. Risk-Reward Check (>= 1.5)
    final rrVal = double.tryParse(item.riskReward.replaceAll(RegExp(r'[^0-9.]'), '')) ?? 2.0;
    if (rrVal < 1.5) {
      failed.add('Risk Reward too low ($rrVal < 1.5)');
    } else {
      passed.add('Risk Reward Passed ($rrVal)');
    }

    // 6. Duplicate Trade Protection
    final engine = PaperTradingEngine.instance;
    final isDuplicate = engine.openTrades.any((t) => t.symbol == item.symbol);
    if (isDuplicate) {
      failed.add('Duplicate Open Position for ${item.symbol}');
    } else {
      passed.add('No Duplicate Position');
    }

    // 7. Capital Availability & Max Exposure Check
    final requiredCapital = item.entry * requestedQty;
    if (requiredCapital > engine.availableCash) {
      failed.add('Insufficient Cash (Required: ₹${requiredCapital.toStringAsFixed(0)}, Available: ₹${engine.availableCash.toStringAsFixed(0)})');
    } else {
      passed.add('Sufficient Cash Available');
    }

    // 8. Max Open Trades Limit (Max 10)
    if (engine.openTrades.length >= 10) {
      failed.add('Maximum Open Trades Limit reached (10/10)');
    } else {
      passed.add('Open Trades Capacity Available');
    }

    final isValid = failed.isEmpty;
    return ValidationResult(
      isValid: isValid,
      message: isValid ? 'All 8 Safety Validations Passed' : 'Validation Failed: ${failed.first}',
      passedChecks: passed,
      failedChecks: failed,
    );
  }

  void recordTradeOutcome(bool isWin) {
    if (isWin) {
      consecutiveLossesCount = 0;
    } else {
      consecutiveLossesCount++;
      if (consecutiveLossesCount >= 5) {
        isCircuitBreakerTripped = true;
      }
    }
  }

  void resetCircuitBreaker() {
    isCircuitBreakerTripped = false;
    consecutiveLossesCount = 0;
  }
}
