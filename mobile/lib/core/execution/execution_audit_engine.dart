import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ExecutionAuditRecord {
  final String id;
  final String symbol;
  final String signal;
  final double entry;
  final int quantity;
  final bool validationPassed;
  final String validationMessage;
  final String userAction; // 'CONFIRMED', 'CANCELLED', 'REJECTED'
  final DateTime timestamp;

  ExecutionAuditRecord({
    required this.id,
    required this.symbol,
    required this.signal,
    required this.entry,
    required this.quantity,
    required this.validationPassed,
    required this.validationMessage,
    required this.userAction,
    required this.timestamp,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'symbol': symbol,
      'signal': signal,
      'entry': entry,
      'quantity': quantity,
      'validationPassed': validationPassed,
      'validationMessage': validationMessage,
      'userAction': userAction,
      'timestamp': timestamp.toIso8601String(),
    };
  }

  factory ExecutionAuditRecord.fromJson(Map<String, dynamic> json) {
    return ExecutionAuditRecord(
      id: json['id'] ?? '',
      symbol: json['symbol'] ?? '',
      signal: json['signal'] ?? 'BUY',
      entry: (json['entry'] as num).toDouble(),
      quantity: (json['quantity'] as num).toInt(),
      validationPassed: json['validationPassed'] ?? true,
      validationMessage: json['validationMessage'] ?? '',
      userAction: json['userAction'] ?? 'CONFIRMED',
      timestamp: DateTime.parse(json['timestamp']),
    );
  }
}

class ExecutionAuditEngine extends ChangeNotifier {
  static final ExecutionAuditEngine _instance = ExecutionAuditEngine._internal();
  static ExecutionAuditEngine get instance => _instance;

  ExecutionAuditEngine._internal();

  static const String keyAuditRecords = 'execution_audit_records_v1';
  List<ExecutionAuditRecord> _auditRecords = [];

  List<ExecutionAuditRecord> get auditRecords => List.unmodifiable(_auditRecords);

  int get totalValidationsCount => _auditRecords.length;
  int get confirmedExecutionsCount => _auditRecords.where((r) => r.userAction == 'CONFIRMED').length;
  int get cancelledExecutionsCount => _auditRecords.where((r) => r.userAction == 'CANCELLED').length;
  int get rejectedExecutionsCount => _auditRecords.where((r) => r.userAction == 'REJECTED').length;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    final str = prefs.getString(keyAuditRecords);
    if (str != null) {
      try {
        final List list = json.decode(str);
        _auditRecords = list.map((e) => ExecutionAuditRecord.fromJson(e)).toList();
      } catch (e) {
        debugPrint('[ExecutionAuditEngine] Error loading audit records: $e');
      }
    }
    notifyListeners();
  }

  Future<void> recordAudit({
    required String symbol,
    required String signal,
    required double entry,
    required int quantity,
    required bool validationPassed,
    required String validationMessage,
    required String userAction,
  }) async {
    final record = ExecutionAuditRecord(
      id: 'AUD_${DateTime.now().millisecondsSinceEpoch}',
      symbol: symbol,
      signal: signal,
      entry: entry,
      quantity: quantity,
      validationPassed: validationPassed,
      validationMessage: validationMessage,
      userAction: userAction,
      timestamp: DateTime.now(),
    );

    _auditRecords.insert(0, record);
    await _save();
    notifyListeners();
  }

  Future<void> _save() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(keyAuditRecords, json.encode(_auditRecords.map((r) => r.toJson()).toList()));
  }
}
