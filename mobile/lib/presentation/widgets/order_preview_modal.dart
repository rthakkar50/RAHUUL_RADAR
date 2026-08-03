import 'package:flutter/material.dart';
import '../../core/execution/execution_validator.dart';
import '../../core/execution/execution_audit_engine.dart';
import '../../core/paper_trading/paper_trading_engine.dart';
import '../../data/models/scan_result_model.dart';

class OrderPreviewModal extends StatefulWidget {
  final ScanResultModel item;

  const OrderPreviewModal({super.key, required this.item});

  static Future<void> show(BuildContext context, ScanResultModel item) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF161B22),
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => OrderPreviewModal(item: item),
    );
  }

  @override
  State<OrderPreviewModal> createState() => _OrderPreviewModalState();
}

class _OrderPreviewModalState extends State<OrderPreviewModal> {
  late int _quantity;
  late ValidationResult _validation;

  @override
  void initState() {
    super.initState();
    int recommended = (10000.0 / widget.item.entry).floor();
    _quantity = recommended > 0 ? recommended : 1;
    _runValidation();
  }

  void _runValidation() {
    setState(() {
      _validation = ExecutionValidator.instance.validateOrder(
        item: widget.item,
        requestedQty: _quantity,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final item = widget.item;
    final sigColor = item.signal.toUpperCase().contains('BUY')
        ? Colors.greenAccent
        : (item.signal.toUpperCase().contains('SELL') ? Colors.redAccent : Colors.amberAccent);

    final requiredCapital = item.entry * _quantity;
    final riskAmount = (item.entry - item.stopLoss).abs() * _quantity;
    final expectedProfit = (item.target1 - item.entry).abs() * _quantity;

    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.shield_outlined, color: Colors.cyanAccent, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'Order Safety Preview (${item.symbol})',
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                ],
              ),
              IconButton(
                icon: const Icon(Icons.close, color: Colors.grey),
                onPressed: () => Navigator.pop(context),
              ),
            ],
          ),
          const Divider(color: Colors.white10),

          // Safety Validation Badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: _validation.isValid ? Colors.green.withValues(alpha: 0.15) : Colors.red.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: _validation.isValid ? Colors.greenAccent : Colors.redAccent),
            ),
            child: Row(
              children: [
                Icon(_validation.isValid ? Icons.check_circle : Icons.warning_amber_rounded, color: _validation.isValid ? Colors.greenAccent : Colors.redAccent, size: 18),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _validation.message,
                    style: TextStyle(color: _validation.isValid ? Colors.greenAccent : Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),

          // Order Metrics Grid
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricPill('Signal Side', item.signal, sigColor),
              _metricPill('Entry Price', '₹${item.entry}', Colors.white),
              _metricPill('Stop Loss', '₹${item.stopLoss}', Colors.redAccent),
              _metricPill('Target 1', '₹${item.target1}', Colors.greenAccent),
            ],
          ),
          const SizedBox(height: 12),

          // Quantity Adjuster
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Order Quantity:', style: TextStyle(color: Colors.white70, fontSize: 13)),
              Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.remove_circle_outline, color: Colors.cyanAccent),
                    onPressed: _quantity > 1 ? () {
                      setState(() {
                        _quantity--;
                        _runValidation();
                      });
                    } : null,
                  ),
                  Text('$_quantity', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                  IconButton(
                    icon: const Icon(Icons.add_circle_outline, color: Colors.cyanAccent),
                    onPressed: () {
                      setState(() {
                        _quantity++;
                        _runValidation();
                      });
                    },
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 10),

          // Capital & Risk Summary Card
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.04),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Required Capital:', style: TextStyle(color: Colors.grey, fontSize: 12)),
                    Text('₹${requiredCapital.toStringAsFixed(2)}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                  ],
                ),
                const SizedBox(height: 4),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Expected Profit (T1):', style: TextStyle(color: Colors.grey, fontSize: 12)),
                    Text('+₹${expectedProfit.toStringAsFixed(2)}', style: const TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 13)),
                  ],
                ),
                const SizedBox(height: 4),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Max Risk (SL):', style: TextStyle(color: Colors.grey, fontSize: 12)),
                    Text('-₹${riskAmount.toStringAsFixed(2)}', style: const TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 13)),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Action Buttons
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () async {
                    await ExecutionAuditEngine.instance.recordAudit(
                      symbol: item.symbol,
                      signal: item.signal,
                      entry: item.entry,
                      quantity: _quantity,
                      validationPassed: _validation.isValid,
                      validationMessage: _validation.message,
                      userAction: 'CANCELLED',
                    );
                    if (context.mounted) Navigator.pop(context);
                  },
                  style: OutlinedButton.styleFrom(side: const BorderSide(color: Colors.grey)),
                  child: const Text('Cancel', style: TextStyle(color: Colors.white)),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                flex: 2,
                child: ElevatedButton.icon(
                  onPressed: _validation.isValid ? () async {
                    await ExecutionAuditEngine.instance.recordAudit(
                      symbol: item.symbol,
                      signal: item.signal,
                      entry: item.entry,
                      quantity: _quantity,
                      validationPassed: true,
                      validationMessage: _validation.message,
                      userAction: 'CONFIRMED',
                    );

                    final success = await PaperTradingEngine.instance.executePaperTradeFromScanner(
                      item,
                      requestedQty: _quantity,
                    );

                    if (context.mounted) {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(success ? 'Safety Verified! Paper Order Executed (${item.symbol})' : 'Execution Failed: Insufficient Capital'),
                          backgroundColor: success ? Colors.green : Colors.red,
                        ),
                      );
                    }
                  } : null,
                  icon: const Icon(Icons.check, size: 18),
                  label: const Text('Confirm Virtual Order'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    disabledBackgroundColor: Colors.grey.withValues(alpha: 0.3),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metricPill(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 2),
        Text(value, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 12)),
      ],
    );
  }
}
