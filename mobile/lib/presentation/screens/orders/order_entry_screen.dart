import 'package:flutter/material.dart';
import '../../../data/models/scan_result_model.dart';
import '../../../data/repositories/order_repository.dart';

class OrderEntryScreen extends StatefulWidget {
  final ScanResultModel? scanResult;

  const OrderEntryScreen({super.key, this.scanResult});

  @override
  State<OrderEntryScreen> createState() => _OrderEntryScreenState();
}

class _OrderEntryScreenState extends State<OrderEntryScreen> {
  final OrderRepository _orderRepo = OrderRepository();
  final TextEditingController _symbolController = TextEditingController();
  final TextEditingController _qtyController = TextEditingController(
    text: '25',
  );
  final TextEditingController _priceController = TextEditingController(
    text: '0.00',
  );
  final TextEditingController _slController = TextEditingController(
    text: '0.00',
  );
  final TextEditingController _targetController = TextEditingController(
    text: '0.00',
  );

  String _side = 'BUY'; // BUY / SELL
  String _orderType = 'LIMIT'; // MARKET, LIMIT, STOP, STOP_LIMIT
  bool _isExecuting = false;

  @override
  void initState() {
    super.initState();
    if (widget.scanResult != null) {
      _symbolController.text = widget.scanResult!.symbol;
      _side = widget.scanResult!.signal.toUpperCase().contains('BUY')
          ? 'BUY'
          : 'SELL';
      _priceController.text = widget.scanResult!.price.toStringAsFixed(2);
      _slController.text = widget.scanResult!.stopLoss.toStringAsFixed(2);
      _targetController.text = widget.scanResult!.target1.toStringAsFixed(2);
    } else {
      _symbolController.text = 'DIVISLAB';
      _priceController.text = '4850.00';
      _slController.text = '4750.00';
      _targetController.text = '5050.00';
    }
  }

  @override
  void dispose() {
    _symbolController.dispose();
    _qtyController.dispose();
    _priceController.dispose();
    _slController.dispose();
    _targetController.dispose();
    super.dispose();
  }

  void _showOrderConfirmation() {
    final qty = int.tryParse(_qtyController.text) ?? 1;
    final price = double.tryParse(_priceController.text) ?? 0.0;
    final sl = double.tryParse(_slController.text) ?? 0.0;
    final target = double.tryParse(_targetController.text) ?? 0.0;
    final margin = price * qty * 0.20; // 20% Margin
    final risk = (price - sl).abs() * qty;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF161B22),
        title: Row(
          children: [
            Icon(
              _side == 'BUY' ? Icons.arrow_upward : Icons.arrow_downward,
              color: _side == 'BUY' ? Colors.greenAccent : Colors.redAccent,
            ),
            const SizedBox(width: 8),
            Text(
              'Confirm $_side Order',
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _confRow('Symbol', _symbolController.text, Colors.white),
            _confRow('Order Type', _orderType, Colors.cyanAccent),
            _confRow('Quantity', '$qty', Colors.white),
            _confRow(
              'Price',
              '₹${price.toStringAsFixed(2)}',
              Colors.blueAccent,
            ),
            _confRow(
              'Stop Loss',
              '₹${sl.toStringAsFixed(2)}',
              Colors.redAccent,
            ),
            _confRow(
              'Target',
              '₹${target.toStringAsFixed(2)}',
              Colors.greenAccent,
            ),
            const Divider(color: Colors.white10),
            _confRow(
              'Margin Required',
              '₹${margin.toStringAsFixed(2)}',
              Colors.amberAccent,
            ),
            _confRow(
              'Total Max Risk',
              '₹${risk.toStringAsFixed(2)}',
              Colors.redAccent,
            ),
            _confRow(
              'Estimated Charges',
              '₹20.00 (Flat Brokerage)',
              Colors.grey,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              _executeOrder();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: _side == 'BUY'
                  ? Colors.greenAccent
                  : Colors.redAccent,
            ),
            child: const Text(
              'Confirm & Submit',
              style: TextStyle(
                color: Colors.black,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _executeOrder() async {
    setState(() => _isExecuting = true);
    try {
      final qty = int.tryParse(_qtyController.text) ?? 1;
      final price = double.tryParse(_priceController.text) ?? 0.0;
      final sl = double.tryParse(_slController.text) ?? 0.0;

      final res = await _orderRepo.executeOrder(
        symbol: _symbolController.text,
        action: _side,
        quantity: qty,
        orderType: _orderType,
        price: price,
        triggerPrice: sl,
      );

      if (mounted) {
        setState(() => _isExecuting = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Order Submitted Successfully! Order ID: ${res.orderId}',
            ),
            backgroundColor: Colors.greenAccent,
          ),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isExecuting = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Order Execution Error: $e'),
            backgroundColor: Colors.redAccent,
          ),
        );
      }
    }
  }

  Widget _confRow(String label, String val, Color col) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
          Text(
            val,
            style: TextStyle(
              color: col,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0E14),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B0E14),
        title: const Text(
          'Order Execution Terminal',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSideSelector(),
            const SizedBox(height: 16),
            _buildOrderTypeSelector(),
            const SizedBox(height: 16),
            _buildInputFields(),
            const SizedBox(height: 16),
            _buildRiskMarginSummary(),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _isExecuting ? null : _showOrderConfirmation,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _side == 'BUY'
                      ? Colors.greenAccent
                      : Colors.redAccent,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: _isExecuting
                    ? const CircularProgressIndicator(color: Colors.black)
                    : Text(
                        'SUBMIT $_side ORDER',
                        style: const TextStyle(
                          color: Colors.black,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSideSelector() {
    return Row(
      children: [
        Expanded(
          child: GestureDetector(
            onTap: () => setState(() => _side = 'BUY'),
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 12),
              decoration: BoxDecoration(
                color: _side == 'BUY'
                    ? Colors.greenAccent
                    : const Color(0xFF161B22),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.greenAccent),
              ),
              child: Center(
                child: Text(
                  'BUY / LONG',
                  style: TextStyle(
                    color: _side == 'BUY' ? Colors.black : Colors.greenAccent,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: GestureDetector(
            onTap: () => setState(() => _side = 'SELL'),
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 12),
              decoration: BoxDecoration(
                color: _side == 'SELL'
                    ? Colors.redAccent
                    : const Color(0xFF161B22),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.redAccent),
              ),
              child: Center(
                child: Text(
                  'SELL / SHORT',
                  style: TextStyle(
                    color: _side == 'SELL' ? Colors.white : Colors.redAccent,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildOrderTypeSelector() {
    final types = ['MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT'];
    return Row(
      children: types.map((t) {
        final isSel = _orderType == t;
        return Expanded(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 2.0),
            child: ChoiceChip(
              label: Text(
                t,
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: isSel ? FontWeight.bold : FontWeight.normal,
                ),
              ),
              selected: isSel,
              selectedColor: Colors.blueAccent,
              backgroundColor: const Color(0xFF161B22),
              onSelected: (val) {
                if (val) setState(() => _orderType = t);
              },
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildInputFields() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        children: [
          _field('Symbol', _symbolController),
          const SizedBox(height: 10),
          _field('Quantity', _qtyController, isNum: true),
          const SizedBox(height: 10),
          _field('Entry Price (₹)', _priceController, isNum: true),
          const SizedBox(height: 10),
          _field('Stop Loss (₹)', _slController, isNum: true),
          const SizedBox(height: 10),
          _field('Target (₹)', _targetController, isNum: true),
        ],
      ),
    );
  }

  Widget _field(
    String label,
    TextEditingController ctrl, {
    bool isNum = false,
  }) {
    return TextField(
      controller: ctrl,
      keyboardType: isNum ? TextInputType.number : TextInputType.text,
      style: const TextStyle(
        color: Colors.white,
        fontWeight: FontWeight.bold,
        fontSize: 13,
      ),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: Colors.grey, fontSize: 12),
        border: const OutlineInputBorder(),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 12,
          vertical: 10,
        ),
      ),
    );
  }

  Widget _buildRiskMarginSummary() {
    final qty = int.tryParse(_qtyController.text) ?? 1;
    final price = double.tryParse(_priceController.text) ?? 0.0;
    final sl = double.tryParse(_slController.text) ?? 0.0;
    final margin = price * qty * 0.20;
    final risk = (price - sl).abs() * qty;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Margin Required:',
                style: TextStyle(color: Colors.grey, fontSize: 11),
              ),
              Text(
                '₹${margin.toStringAsFixed(2)}',
                style: const TextStyle(
                  color: Colors.amberAccent,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Est. Risk Amount:',
                style: TextStyle(color: Colors.grey, fontSize: 11),
              ),
              Text(
                '₹${risk.toStringAsFixed(2)}',
                style: const TextStyle(
                  color: Colors.redAccent,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'AI Recommendation:',
                style: TextStyle(color: Colors.grey, fontSize: 11),
              ),
              Text(
                'Optimal Size • R:R 1:2.5',
                style: TextStyle(
                  color: Colors.greenAccent,
                  fontWeight: FontWeight.bold,
                  fontSize: 11,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
