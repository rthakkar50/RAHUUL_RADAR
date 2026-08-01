import 'package:flutter/material.dart';
import '../../../data/models/fno_model.dart';
import '../../../data/repositories/fno_repository.dart';

class FnoScreen extends StatefulWidget {
  const FnoScreen({super.key});

  @override
  State<FnoScreen> createState() => _FnoScreenState();
}

class _FnoScreenState extends State<FnoScreen> {
  final FnoRepository _repository = FnoRepository();
  FnoOverviewModel? _data;
  bool _isLoading = false;
  String? _error;
  String _selectedSymbol = 'NIFTY';

  final List<String> _symbols = ['NIFTY', 'BANKNIFTY', 'FINNIFTY'];

  @override
  void initState() {
    super.initState();
    _fetchFno();
  }

  Future<void> _fetchFno() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final data = await _repository.getFnoOverview(symbol: _selectedSymbol);
      if (mounted) {
        setState(() {
          _data = data;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0E14),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B0E14),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Colors.purpleAccent, Colors.deepPurple]),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.show_chart, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('F&O Derivatives Engine', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _fetchFno,
          )
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _data == null) {
      return const Center(child: CircularProgressIndicator(color: Colors.purpleAccent));
    }

    if (_error != null && _data == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, color: Colors.redAccent, size: 48),
              const SizedBox(height: 12),
              Text(_error!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white70)),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _fetchFno,
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    final d = _data!;

    return RefreshIndicator(
      onRefresh: _fetchFno,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSymbolSelector(),
            const SizedBox(height: 16),
            _buildMetricsOverview(d),
            const SizedBox(height: 16),
            _buildBuildUpBanner(d),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Option Chain Matrix', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                Text('Expiry: ${d.expiryDate}', style: const TextStyle(color: Colors.purpleAccent, fontSize: 12, fontWeight: FontWeight.bold)),
              ],
            ),
            const SizedBox(height: 10),
            _buildOptionChainTable(d),
          ],
        ),
      ),
    );
  }

  Widget _buildSymbolSelector() {
    return Row(
      children: _symbols.map((sym) {
        final isSel = _selectedSymbol == sym;
        return Padding(
          padding: const EdgeInsets.only(right: 8.0),
          child: ChoiceChip(
            label: Text(sym),
            selected: isSel,
            selectedColor: Colors.purpleAccent,
            backgroundColor: const Color(0xFF161B22),
            labelStyle: TextStyle(color: isSel ? Colors.white : Colors.white70, fontWeight: isSel ? FontWeight.bold : FontWeight.normal),
            onSelected: (val) {
              if (val) {
                setState(() => _selectedSymbol = sym);
                _fetchFno();
              }
            },
          ),
        );
      }).toList(),
    );
  }

  Widget _buildMetricsOverview(FnoOverviewModel d) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricTile('Spot Price', '₹${d.spotPrice.toStringAsFixed(2)}', Colors.cyanAccent),
              _metricTile('PCR Ratio', '${d.pcr}', d.pcr >= 1.0 ? Colors.greenAccent : Colors.redAccent),
              _metricTile('Max Pain', '₹${d.maxPain.toStringAsFixed(0)}', Colors.amberAccent),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(color: Colors.white10, height: 1),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricTile('IV Rank', '${d.ivRank}%', Colors.purpleAccent),
              _metricTile('IV Percentile', '${d.ivPercentile}%', Colors.deepPurpleAccent),
              _metricTile('Margin / Lot', '₹${(d.marginRequired / 1000).toStringAsFixed(0)}K', Colors.white),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metricTile(String label, String val, Color col) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 3),
        Text(val, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 14)),
      ],
    );
  }

  Widget _buildBuildUpBanner(FnoOverviewModel d) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.green.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.greenAccent.withValues(alpha: 0.3)),
      ),
      child: const Row(
        children: [
          Icon(Icons.trending_up, color: Colors.greenAccent, size: 18),
          SizedBox(width: 8),
          Expanded(
            child: Text(
              'Bullish Long Build-up in ATM Calls. Put writing active at Max Pain strike.',
              style: TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOptionChainTable(FnoOverviewModel d) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          headingRowHeight: 36,
          dataRowMinHeight: 40,
          dataRowMaxHeight: 40,
          horizontalMargin: 12,
          columnSpacing: 16,
          headingRowColor: WidgetStateProperty.all(const Color(0xFF21262D)),
          columns: const [
            DataColumn(label: Text('CALL OI', style: TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.bold))),
            DataColumn(label: Text('CALL LTP', style: TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.bold))),
            DataColumn(label: Text('STRIKE', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold))),
            DataColumn(label: Text('PUT LTP', style: TextStyle(color: Colors.redAccent, fontSize: 11, fontWeight: FontWeight.bold))),
            DataColumn(label: Text('PUT OI', style: TextStyle(color: Colors.redAccent, fontSize: 11, fontWeight: FontWeight.bold))),
            DataColumn(label: Text('DELTA', style: TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold))),
            DataColumn(label: Text('BUILDUP', style: TextStyle(color: Colors.amberAccent, fontSize: 11, fontWeight: FontWeight.bold))),
          ],
          rows: d.optionChain.map((item) {
            final isAtm = (item.strike - d.spotPrice).abs() < 50;
            return DataRow(
              color: isAtm ? WidgetStateProperty.all(Colors.purpleAccent.withValues(alpha: 0.15)) : null,
              cells: [
                DataCell(Text('${(item.callOi / 1000).toStringAsFixed(0)}K', style: const TextStyle(fontSize: 11, color: Colors.white70))),
                DataCell(Text(item.callPrice.toStringAsFixed(1), style: const TextStyle(fontSize: 11, color: Colors.greenAccent, fontWeight: FontWeight.bold))),
                DataCell(Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(color: isAtm ? Colors.purpleAccent : Colors.transparent, borderRadius: BorderRadius.circular(4)),
                  child: Text(item.strike.toStringAsFixed(0), style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: isAtm ? Colors.white : Colors.white)),
                )),
                DataCell(Text('₹${item.putPrice.toStringAsFixed(1)}', style: const TextStyle(fontSize: 11, color: Colors.redAccent, fontWeight: FontWeight.bold))),
                DataCell(Text('${(item.putOi / 1000).toStringAsFixed(0)}K', style: const TextStyle(fontSize: 11, color: Colors.white70))),
                DataCell(Text('${item.callGreeks.delta.toStringAsFixed(2)}', style: const TextStyle(fontSize: 11, color: Colors.cyanAccent))),
                DataCell(Text(item.buildupType, style: const TextStyle(fontSize: 10, color: Colors.amberAccent))),
              ],
            );
          }).toList(),
        ),
      ),
    );
  }
}
