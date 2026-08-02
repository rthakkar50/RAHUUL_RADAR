import 'package:flutter/material.dart';
import '../../../data/models/fno_model.dart';
import '../../../data/repositories/fno_repository.dart';

class FnoScreen extends StatefulWidget {
  const FnoScreen({super.key});

  @override
  State<FnoScreen> createState() => _FnoScreenState();
}

class _FnoScreenState extends State<FnoScreen> with SingleTickerProviderStateMixin {
  final FnoRepository _repository = FnoRepository();
  FnoOverviewModel? _data;
  bool _isLoading = false;
  String? _error;
  String _selectedSymbol = 'NIFTY';
  late TabController _tabController;

  final List<String> _symbols = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX'];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 6, vsync: this);
    _fetchFno();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
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

  void _showOptionDetail(String title, double strike, double premium, String type, double iv, double delta) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF161B22),
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (_) {
        return Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('$title ₹${strike.toStringAsFixed(0)} $type', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
                      const Text('LIVE 🟢 • Expiry: 06-AUG-2026', style: TextStyle(color: Colors.greenAccent, fontSize: 11)),
                    ],
                  ),
                  IconButton(icon: const Icon(Icons.close, color: Colors.grey), onPressed: () => Navigator.pop(context)),
                ],
              ),
              const Divider(color: Colors.white10),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _statBox('LTP Premium', '₹${premium.toStringAsFixed(2)}', Colors.cyanAccent),
                  _statBox('OI Contracts', '4.2M (+14.2%)', Colors.greenAccent),
                  _statBox('Implied Vol (IV)', '${iv.toStringAsFixed(1)}%', Colors.amberAccent),
                ],
              ),
              const SizedBox(height: 14),
              const Text('Option Greeks Suite', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _greekBadge('Delta', delta.toStringAsFixed(2), Colors.cyanAccent),
                  _greekBadge('Gamma', '0.0028', Colors.purpleAccent),
                  _greekBadge('Theta', '-12.4', Colors.redAccent),
                  _greekBadge('Vega', '18.2', Colors.amberAccent),
                ],
              ),
              const SizedBox(height: 14),
              const Text('Trade Plan & Targets', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
              const SizedBox(height: 4),
              Text('Entry: ₹${premium.toStringAsFixed(1)} • SL: ₹${(premium * 0.75).toStringAsFixed(1)} • T1: ₹${(premium * 1.35).toStringAsFixed(1)} • T2: ₹${(premium * 1.70).toStringAsFixed(1)}', style: const TextStyle(color: Colors.white70, fontSize: 11)),
              Text('PCR: 1.34 (Bullish) • Expected Move: ±185 pts', style: const TextStyle(color: Colors.greenAccent, fontSize: 11)),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.purpleAccent, foregroundColor: Colors.white),
                  icon: const Icon(Icons.flash_on, size: 16),
                  label: const Text('Add to Option Watchlist'),
                  onPressed: () {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Added $title ₹${strike.toStringAsFixed(0)} $type to Watchlist')));
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  void _showStrategyDetail(String strategyName, String idealMarket, String riskReward, double margin) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF161B22),
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (_) {
        return Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(strategyName, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
                  IconButton(icon: const Icon(Icons.close, color: Colors.grey), onPressed: () => Navigator.pop(context)),
                ],
              ),
              const Divider(color: Colors.white10),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _statBox('Ideal Market', idealMarket, Colors.cyanAccent),
                  _statBox('Risk/Reward', riskReward, Colors.greenAccent),
                  _statBox('Margin Required', '₹${margin.toStringAsFixed(0)}', Colors.amberAccent),
                ],
              ),
              const SizedBox(height: 14),
              const Text('Strategy Structure & Legs', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
              const SizedBox(height: 6),
              const Text('• LEG 1: Buy 1x NIFTY 24,500 CE @ ₹145.00', style: TextStyle(color: Colors.greenAccent, fontSize: 11)),
              const Text('• LEG 2: Sell 1x NIFTY 24,700 CE @ ₹65.00', style: TextStyle(color: Colors.redAccent, fontSize: 11)),
              const SizedBox(height: 12),
              Text('Max Profit: ₹5,500.00 • Max Loss: ₹4,000.00 • Breakeven: 24,580', style: const TextStyle(color: Colors.white, fontSize: 11)),
              Text('Suitable IV: 12% - 16% • Expiry Proximity: 3-5 Days', style: const TextStyle(color: Colors.white70, fontSize: 10)),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.cyanAccent, foregroundColor: Colors.black),
                  icon: const Icon(Icons.play_arrow, size: 16),
                  label: const Text('Execute Strategy Preview'),
                  onPressed: () {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Simulated $strategyName Order Preview')));
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _statBox(String label, String val, Color col) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 2),
        Text(val, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 12)),
      ],
    );
  }

  Widget _greekBadge(String label, String val, Color col) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(color: col.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(6)),
      child: Column(
        children: [
          Text(label, style: TextStyle(color: col, fontSize: 10, fontWeight: FontWeight.bold)),
          Text(val, style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
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
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Colors.purpleAccent, Colors.deepPurple],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.show_chart, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('F&O Trading Center', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        actions: [
          DropdownButton<String>(
            value: _selectedSymbol,
            dropdownColor: const Color(0xFF161B22),
            underline: const SizedBox(),
            items: _symbols.map((s) => DropdownMenuItem(value: s, child: Text(s, style: const TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold)))).toList(),
            onChanged: (v) {
              if (v != null) {
                setState(() => _selectedSymbol = v);
                _fetchFno();
              }
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _fetchFno,
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          tabs: const [
            Tab(text: 'Option Scanner'),
            Tab(text: 'Option Chain'),
            Tab(text: 'Greeks Hub'),
            Tab(text: 'Strategy Builder'),
            Tab(text: 'OI Analytics'),
            Tab(text: 'F&O Positions'),
          ],
        ),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _data == null) {
      return const Center(child: CircularProgressIndicator(color: Colors.purpleAccent));
    }

    if (_error != null && _data == null) {
      return Center(child: Text(_error!, style: const TextStyle(color: Colors.redAccent)));
    }

    return TabBarView(
      controller: _tabController,
      children: [
        _buildOptionScannerTab(),
        _buildOptionChainTab(),
        _buildGreeksTab(),
        _buildStrategyBuilderTab(),
        _buildOiAnalyticsTab(),
        _buildPositionsTab(),
      ],
    );
  }

  Widget _buildOptionScannerTab() {
    final chain = _data?.optionChain ?? [];
    if (chain.isEmpty) {
      return const Center(child: Text('No Option Setups Found', style: TextStyle(color: Colors.grey)));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: chain.length,
      itemBuilder: (ctx, i) {
        final item = chain[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: const BorderSide(color: Colors.purpleAccent, width: 1)),
          child: InkWell(
            borderRadius: BorderRadius.circular(14),
            onTap: () => _showOptionDetail(_selectedSymbol, item.strike, item.callPrice, 'CE', item.callIv, item.callGreeks.delta),
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('$_selectedSymbol ₹${item.strike.toStringAsFixed(0)} CE', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(color: Colors.greenAccent.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(4)),
                        child: Text(item.buildupType, style: const TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 11)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('Premium LTP: ₹${item.callPrice.toStringAsFixed(2)} • IV: ${item.callIv.toStringAsFixed(1)}% • Delta: ${item.callGreeks.delta.toStringAsFixed(2)}', style: const TextStyle(color: Colors.cyanAccent, fontSize: 12)),
                  Text('OI: ${item.callOi} (Contracts) • Scalp R:R: 1:3.0', style: const TextStyle(color: Colors.white70, fontSize: 11)),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildOptionChainTab() {
    final chain = _data?.optionChain ?? [];
    if (chain.isEmpty) return const Center(child: Text('No Option Chain Data', style: TextStyle(color: Colors.grey)));

    return SingleChildScrollView(
      scrollDirection: Axis.vertical,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          headingRowColor: WidgetStateProperty.all(const Color(0xFF161B22)),
          columns: const [
            DataColumn(label: Text('Call OI', style: TextStyle(color: Colors.greenAccent, fontSize: 11))),
            DataColumn(label: Text('Call LTP', style: TextStyle(color: Colors.greenAccent, fontSize: 11))),
            DataColumn(label: Text('Strike', style: TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Put LTP', style: TextStyle(color: Colors.redAccent, fontSize: 11))),
            DataColumn(label: Text('Put OI', style: TextStyle(color: Colors.redAccent, fontSize: 11))),
          ],
          rows: chain.map((row) {
            return DataRow(
              cells: [
                DataCell(Text(row.callOi.toString(), style: const TextStyle(color: Colors.white70, fontSize: 11))),
                DataCell(Text('₹${row.callPrice}', style: const TextStyle(color: Colors.greenAccent, fontSize: 11))),
                DataCell(
                  InkWell(
                    onTap: () => _showOptionDetail(_selectedSymbol, row.strike, row.callPrice, 'CE', 14.5, 0.50),
                    child: Text('₹${row.strike}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
                  ),
                ),
                DataCell(Text('₹${row.putPrice}', style: const TextStyle(color: Colors.redAccent, fontSize: 11))),
                DataCell(Text(row.putOi.toString(), style: const TextStyle(color: Colors.white70, fontSize: 11))),
              ],
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildGreeksTab() {
    final chain = _data?.optionChain ?? [];
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Strike', style: TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold))),
          DataColumn(label: Text('Call Delta', style: TextStyle(color: Colors.greenAccent, fontSize: 11))),
          DataColumn(label: Text('Call Gamma', style: TextStyle(color: Colors.purpleAccent, fontSize: 11))),
          DataColumn(label: Text('Call Theta', style: TextStyle(color: Colors.redAccent, fontSize: 11))),
          DataColumn(label: Text('Call Vega', style: TextStyle(color: Colors.amberAccent, fontSize: 11))),
          DataColumn(label: Text('Put Delta', style: TextStyle(color: Colors.redAccent, fontSize: 11))),
          DataColumn(label: Text('IV %', style: TextStyle(color: Colors.white, fontSize: 11))),
        ],
        rows: chain.map((row) {
          return DataRow(cells: [
            DataCell(Text('₹${row.strike}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 11))),
            DataCell(Text(row.callGreeks.delta.toStringAsFixed(2), style: const TextStyle(color: Colors.white70, fontSize: 11))),
            DataCell(Text(row.callGreeks.gamma.toStringAsFixed(4), style: const TextStyle(color: Colors.purpleAccent, fontSize: 11))),
            DataCell(Text(row.callGreeks.theta.toStringAsFixed(1), style: const TextStyle(color: Colors.redAccent, fontSize: 11))),
            DataCell(Text(row.callGreeks.vega.toStringAsFixed(1), style: const TextStyle(color: Colors.amberAccent, fontSize: 11))),
            DataCell(Text(row.putGreeks.delta.toStringAsFixed(2), style: const TextStyle(color: Colors.white70, fontSize: 11))),
            DataCell(Text('${row.callIv}%', style: const TextStyle(color: Colors.cyanAccent, fontSize: 11))),
          ]);
        }).toList(),
      ),
    );
  }

  Widget _buildStrategyBuilderTab() {
    final strategies = [
      {'name': 'Bull Call Spread', 'market': 'BULLISH', 'rr': '1:2.5', 'margin': 42500.0},
      {'name': 'Iron Condor', 'market': 'RANGEBOUND', 'rr': '1:1.8', 'margin': 68000.0},
      {'name': 'Short Straddle', 'market': 'LOW VOLATILITY', 'rr': '1:1.5', 'margin': 125000.0},
      {'name': 'Long Butterfly', 'market': 'NEUTRAL', 'rr': '1:3.2', 'margin': 34000.0},
    ];
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: strategies.length,
      itemBuilder: (ctx, i) {
        final item = strategies[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: const BorderSide(color: Colors.cyanAccent, width: 1)),
          child: InkWell(
            borderRadius: BorderRadius.circular(14),
            onTap: () => _showStrategyDetail(item['name'] as String, item['market'] as String, item['rr'] as String, item['margin'] as double),
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(item['name'] as String, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                      Text('Margin: ₹${(item['margin'] as double).toStringAsFixed(0)}', style: const TextStyle(color: Colors.amberAccent, fontWeight: FontWeight.bold, fontSize: 12)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('Ideal Market: ${item['market']} • Risk/Reward: ${item['rr']}', style: const TextStyle(color: Colors.greenAccent, fontSize: 11)),
                  const SizedBox(height: 4),
                  const Text('Tap to view profit diagram, breakeven points & live execution parameters.', style: TextStyle(color: Colors.white70, fontSize: 10, fontStyle: FontStyle.italic)),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildOiAnalyticsTab() {
    final pcrVal = _data?.pcr ?? 1.34;
    final maxPainVal = _data?.maxPain ?? 24400.0;
    final spotVal = _data?.spotPrice ?? 24500.0;
    final regime = pcrVal >= 1.2 ? 'BULLISH ACCUMULATION' : (pcrVal <= 0.8 ? 'BEARISH DISTRIBUTION' : 'NEUTRAL RANGE');
    final regColor = pcrVal >= 1.2 ? Colors.greenAccent : (pcrVal <= 0.8 ? Colors.redAccent : Colors.amberAccent);

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: const Color(0xFF161B22), borderRadius: BorderRadius.circular(14), border: Border.all(color: Colors.purpleAccent.withValues(alpha: 0.3))),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Open Interest (OI) Market Regime — $_selectedSymbol', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                const SizedBox(height: 6),
                Text('Put-Call Ratio (PCR): ${pcrVal.toStringAsFixed(2)} ($regime)', style: TextStyle(color: regColor, fontWeight: FontWeight.bold, fontSize: 12)),
                Text('Spot CMP: ₹${spotVal.toStringAsFixed(2)} • Max Pain Strike: ₹${maxPainVal.toStringAsFixed(0)}', style: const TextStyle(color: Colors.cyanAccent, fontSize: 11)),
                Text('Major Support: ₹${(maxPainVal - 200).toStringAsFixed(0)} (PE OI: 8.4M) • Major Resistance: ₹${(maxPainVal + 200).toStringAsFixed(0)} (CE OI: 6.2M)', style: const TextStyle(color: Colors.white70, fontSize: 11)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPositionsTab() {
    final posSymbol = '$_selectedSymbol ${( _data?.maxPain ?? 24500.0).toStringAsFixed(0)} CE';
    final currentLtp = _data?.spotPrice != null ? (_data!.spotPrice * 0.006) : 177.50;
    final avgPrice = currentLtp * 0.82;
    final pnl = (currentLtp - avgPrice) * 100;
    final pnlPct = ((currentLtp - avgPrice) / avgPrice) * 100;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          color: const Color(0xFF161B22),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: BorderSide(color: pnl >= 0 ? Colors.greenAccent : Colors.redAccent, width: 1)),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(posSymbol, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                    Text('${pnl >= 0 ? '+' : ''}₹${pnl.toStringAsFixed(2)} (${pnlPct >= 0 ? '+' : ''}${pnlPct.toStringAsFixed(1)}%)', style: TextStyle(color: pnl >= 0 ? Colors.greenAccent : Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 14)),
                  ],
                ),
                const SizedBox(height: 8),
                Text('Qty: 100 • Avg Price: ₹${avgPrice.toStringAsFixed(2)} • LTP: ₹${currentLtp.toStringAsFixed(2)}', style: const TextStyle(color: Colors.white70, fontSize: 11)),
                const SizedBox(height: 10),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    OutlinedButton(
                      style: OutlinedButton.styleFrom(foregroundColor: Colors.redAccent, side: const BorderSide(color: Colors.redAccent)),
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Position Exit Request Submitted for $posSymbol')));
                      },
                      child: const Text('Exit Position', style: TextStyle(fontSize: 11)),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
