import 'package:flutter/material.dart';
import '../../../data/models/order_model.dart';
import '../../../data/repositories/order_repository.dart';

class OrderEntrySheet extends StatefulWidget {
  final String symbol;
  final double initialPrice;
  final String defaultAction;

  const OrderEntrySheet({
    super.key,
    required this.symbol,
    this.initialPrice = 0.0,
    this.defaultAction = 'BUY',
  });

  static Future<void> show(
    BuildContext context, {
    required String symbol,
    double initialPrice = 0.0,
    String defaultAction = 'BUY',
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF161B22),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(ctx).viewInsets.bottom,
        ),
        child: OrderEntrySheet(
          symbol: symbol,
          initialPrice: initialPrice,
          defaultAction: defaultAction,
        ),
      ),
    );
  }

  @override
  State<OrderEntrySheet> createState() => _OrderEntrySheetState();
}

class _OrderEntrySheetState extends State<OrderEntrySheet> {
  final _repository = OrderRepository();
  late String _action;
  String _orderType = 'MARKET'; // MARKET, LIMIT, SL, SL-M
  String _product = 'I'; // I = INTRADAY, C = DELIVERY
  int _quantity = 10;
  late TextEditingController _priceController;
  late TextEditingController _triggerPriceController;

  OrderPreviewModel? _preview;
  bool _isLoadingPreview = false;
  bool _isExecuting = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _action = widget.defaultAction;
    _priceController = TextEditingController(
      text: widget.initialPrice > 0 ? widget.initialPrice.toStringAsFixed(2) : '',
    );
    _triggerPriceController = TextEditingController();
    _fetchPreview();
  }

  @override
  void dispose() {
    _priceController.dispose();
    _triggerPriceController.dispose();
    super.dispose();
  }

  Future<void> _fetchPreview() async {
    setState(() {
      _isLoadingPreview = true;
      _errorMessage = null;
    });

    try {
      final priceVal = double.tryParse(_priceController.text) ?? widget.initialPrice;
      final triggerVal = double.tryParse(_triggerPriceController.text) ?? 0.0;

      final previewData = await _repository.getOrderPreview(
        symbol: widget.symbol,
        action: _action,
        quantity: _quantity,
        orderType: _orderType,
        price: priceVal,
        triggerPrice: triggerVal,
        product: _product,
      );

      if (mounted) {
        setState(() {
          _preview = previewData;
          _isLoadingPreview = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString().replaceAll('Exception: ', '');
          _isLoadingPreview = false;
        });
      }
    }
  }

  Future<void> _executeOrder() async {
    setState(() {
      _isExecuting = true;
      _errorMessage = null;
    });

    try {
      final priceVal = double.tryParse(_priceController.text) ?? widget.initialPrice;
      final triggerVal = double.tryParse(_triggerPriceController.text) ?? 0.0;

      final result = await _repository.executeOrder(
        symbol: widget.symbol,
        action: _action,
        quantity: _quantity,
        orderType: _orderType,
        price: priceVal,
        triggerPrice: triggerVal,
        product: _product,
        confirmed: true,
      );

      if (mounted) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Order Placed Successfully! Order ID: ${result.orderId}'),
            backgroundColor: Colors.green.shade800,
            duration: const Duration(seconds: 4),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString().replaceAll('Exception: ', '');
          _isExecuting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isBuy = _action == 'BUY';
    final actionColor = isBuy ? Colors.green : Colors.red;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header Sheet Handle & Symbol Title
          Center(
            child: Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.only(bottom: 16),
              decoration: BoxDecoration(
                color: Colors.grey.shade700,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.symbol,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Text(
                    'NSE • LIVE PAYTM ORDER ENGINE',
                    style: TextStyle(color: Colors.grey, fontSize: 11),
                  ),
                ],
              ),
              IconButton(
                icon: const Icon(Icons.close, color: Colors.grey),
                onPressed: () => Navigator.pop(context),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // BUY / SELL Toggle
          Row(
            children: [
              Expanded(
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: isBuy ? Colors.green : Colors.grey.shade900,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  onPressed: () {
                    setState(() => _action = 'BUY');
                    _fetchPreview();
                  },
                  child: const Text('BUY', style: TextStyle(fontWeight: FontWeight.bold)),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: !isBuy ? Colors.red : Colors.grey.shade900,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  onPressed: () {
                    setState(() => _action = 'SELL');
                    _fetchPreview();
                  },
                  child: const Text('SELL', style: TextStyle(fontWeight: FontWeight.bold)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Product & Order Type Chips
          Row(
            children: [
              ChoiceChip(
                label: const Text('Intraday (MIS)'),
                selected: _product == 'I',
                selectedColor: Colors.blue.shade900,
                onSelected: (val) {
                  if (val) {
                    setState(() => _product = 'I');
                    _fetchPreview();
                  }
                },
              ),
              const SizedBox(width: 8),
              ChoiceChip(
                label: const Text('Delivery (CNC)'),
                selected: _product == 'C',
                selectedColor: Colors.blue.shade900,
                onSelected: (val) {
                  if (val) {
                    setState(() => _product = 'C');
                    _fetchPreview();
                  }
                },
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Order Type Selector: MARKET, LIMIT, SL, SL-M
          Wrap(
            spacing: 8,
            children: ['MARKET', 'LIMIT', 'SL', 'SL-M'].map((type) {
              final isSel = _orderType == type;
              return ChoiceChip(
                label: Text(type),
                selected: isSel,
                selectedColor: actionColor.withValues(alpha: 0.3),
                labelStyle: TextStyle(
                  color: isSel ? Colors.white : Colors.grey,
                  fontWeight: isSel ? FontWeight.bold : FontWeight.normal,
                ),
                onSelected: (val) {
                  if (val) {
                    setState(() => _orderType = type);
                    _fetchPreview();
                  }
                },
              );
            }).toList(),
          ),
          const SizedBox(height: 16),

          // Quantity Field
          Row(
            children: [
              const Text('Quantity', style: TextStyle(color: Colors.grey, fontSize: 14)),
              const Spacer(),
              IconButton(
                icon: const Icon(Icons.remove_circle_outline, color: Colors.blue),
                onPressed: () {
                  if (_quantity > 1) {
                    setState(() => _quantity--);
                    _fetchPreview();
                  }
                },
              ),
              SizedBox(
                width: 60,
                child: TextField(
                  keyboardType: TextInputType.number,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  decoration: const InputDecoration(border: InputBorder.none),
                  controller: TextEditingController(text: '$_quantity')
                    ..selection = TextSelection.collapsed(offset: '$_quantity'.length),
                  onChanged: (val) {
                    final n = int.tryParse(val);
                    if (n != null && n > 0) {
                      _quantity = n;
                      _fetchPreview();
                    }
                  },
                ),
              ),
              IconButton(
                icon: const Icon(Icons.add_circle_outline, color: Colors.blue),
                onPressed: () {
                  setState(() => _quantity++);
                  _fetchPreview();
                },
              ),
            ],
          ),

          // Price Field if LIMIT or SL
          if (_orderType == 'LIMIT' || _orderType == 'SL') ...[
            const SizedBox(height: 12),
            TextField(
              controller: _priceController,
              keyboardType: TextInputType.numberWithOptions(decimal: true),
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                labelText: 'Limit Price (₹)',
                labelStyle: const TextStyle(color: Colors.grey),
                filled: true,
                fillColor: const Color(0xFF0D1117),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
              onChanged: (_) => _fetchPreview(),
            ),
          ],

          // Trigger Price Field if SL or SL-M
          if (_orderType == 'SL' || _orderType == 'SL-M') ...[
            const SizedBox(height: 12),
            TextField(
              controller: _triggerPriceController,
              keyboardType: TextInputType.numberWithOptions(decimal: true),
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                labelText: 'Trigger Price (₹)',
                labelStyle: const TextStyle(color: Colors.grey),
                filled: true,
                fillColor: const Color(0xFF0D1117),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
              onChanged: (_) => _fetchPreview(),
            ),
          ],
          const SizedBox(height: 16),

          // Error Banner (Surfaces actual Paytm rejection reasons)
          if (_errorMessage != null) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red.shade900.withValues(alpha: 0.4),
                border: Border.all(color: Colors.red.shade700),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber_rounded, color: Colors.redAccent),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      _errorMessage!,
                      style: const TextStyle(color: Colors.redAccent, fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],

          // Order Preview Panel (Task 2)
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFF0D1117),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: Colors.grey.shade800),
            ),
            child: _isLoadingPreview
                ? const Center(child: CircularProgressIndicator())
                : Column(
                    children: [
                      _previewRow('Symbol', _preview?.symbol ?? widget.symbol),
                      _previewRow('Exchange', _preview?.exchange ?? 'NSE'),
                      _previewRow('Product', _preview?.product ?? 'INTRADAY'),
                      _previewRow('Order Type', _preview?.orderType ?? _orderType),
                      _previewRow('Quantity', '${_preview?.quantity ?? _quantity}'),
                      _previewRow('Price', '₹${(_preview?.price ?? widget.initialPrice).toStringAsFixed(2)}'),
                      const Divider(color: Colors.grey),
                      _previewRow('Estimated Margin', '₹${(_preview?.estimatedMargin ?? 0.0).toStringAsFixed(2)}', isHighlight: true),
                      _previewRow('Brokerage & Taxes', '₹${(_preview?.taxesAndCharges ?? 0.0).toStringAsFixed(2)}'),
                      _previewRow('Total Cost', '₹${(_preview?.totalCost ?? 0.0).toStringAsFixed(2)}', isHighlight: true, isBold: true),
                    ],
                  ),
          ),
          const SizedBox(height: 20),

          // User Confirmation & Execution Button (Task 2)
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: actionColor,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            onPressed: _isExecuting ? null : _executeOrder,
            child: _isExecuting
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                  )
                : Text(
                    'CONFIRM & PLACE $_action ORDER',
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _previewRow(String label, String value, {bool isHighlight = false, bool isBold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: isBold ? Colors.white : Colors.grey.shade400, fontSize: 13)),
          Text(
            value,
            style: TextStyle(
              color: isHighlight ? (isBold ? Colors.amberAccent : Colors.white) : Colors.grey.shade300,
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
              fontSize: isBold ? 14 : 13,
            ),
          ),
        ],
      ),
    );
  }
}
