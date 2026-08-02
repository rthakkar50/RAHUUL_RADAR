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

  final List<String> _symbols = ['NIFTY', 'BANKNIFTY', 'FINNIFTY'];

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
              child: const Icon(
                Icons.show_chart,
                color: Colors.white,
                size: 18,
              ),
            ),
            const SizedBox(width: 8),
            const Text(
              'F&O Trading Center',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _fetchFno,
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          tabs: const [
            Tab(text: 'Intraday Scanner'),
            Tab(text: 'Option Scanner'),
            Tab(text: 'Option Chain'),
            Tab(text: 'Greeks'),
            Tab(text: 'Strategy'),
            Tab(text: 'Positions'),
          ],
        ),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _data == null) {
      return const Center(
        child: CircularProgressIndicator(color: Colors.purpleAccent),
      );
    }

    if (_error != null && _data == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.error_outline,
                color: Colors.redAccent,
                size: 48,
              ),
              const SizedBox(height: 12),
              Text(
                _error!,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white70),
              ),
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

    return TabBarView(
      controller: _tabController,
      children: [
        _buildIntradayScannerTab(),
        _buildOptionScannerTab(),
        _buildOptionChainTab(d),
        _buildGreeksTab(d),
        _buildStrategyTab(),
        _buildPositionsTab(d),
      ],
    );
  }

  Widget _buildIntradayScannerTab() {
    final items = [
      {'symbol': 'RELIANCE', 'type': 'Breakout', 'momentum': 'Rank #1', 'volume': '+340%', 'vwap': 'Above VWAP', 'orb': 'ORB High Break'},
      {'symbol': 'HDFCBANK', 'type': 'Volume Explosion', 'momentum': 'Rank #2', 'volume': '+410%', 'vwap': 'Above VWAP', 'orb': 'ORB High Break'},
      {'symbol': 'ICICIBANK', 'type': 'VWAP Cross', 'momentum': 'Rank #3', 'volume': '+210%', 'vwap': 'Above VWAP', 'orb': 'Consolidating'},
      {'symbol': 'INFY', 'type': 'Momentum Surge', 'momentum': 'Rank #4', 'volume': '+180%', 'vwap': 'Above VWAP', 'orb': 'ORB High Break'},
    ];

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: items.length,
      itemBuilder: (ctx, i) {
        final item = items[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      item['symbol']!,
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.greenAccent.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        item['momentum']!,
                        style: const TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Signal: ${item['type']}', style: const TextStyle(color: Colors.cyanAccent, fontSize: 12)),
                    Text('Vol: ${item['volume']}', style: const TextStyle(color: Colors.amberAccent, fontSize: 12)),
                  ],
                ),
                const SizedBox(height: 4),
                Text('VWAP: ${item['vwap']} • ORB: ${item['orb']}', style: const TextStyle(color: Colors.white70, fontSize: 11)),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildOptionScannerTab() {
    final alerts = [
      {'setup': 'NIFTY 24800 CE', 'action': 'Best CE Buy', 'oi': '+48% OI Build', 'iv': 'IV Spike 18.4', 'pcr': 'PCR 1.45 (Bullish)'},
      {'setup': 'BANKNIFTY 52500 CE', 'action': 'Best CE Buy', 'oi': '+62% OI Build', 'iv': 'Gamma Spike', 'pcr': 'PCR 1.32 (Bullish)'},
      {'setup': 'FINNIFTY 23400 PE', 'action': 'Best PE Hedge', 'oi': '+22% OI Build', 'iv': 'IV Crush', 'pcr': 'PCR 0.82 (Bearish)'},
    ];

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: alerts.length,
      itemBuilder: (ctx, i) {
        final a = alerts[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: const Icon(Icons.flash_on, color: Colors.amberAccent),
            title: Text(a['setup']!, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: Text('${a['action']} • ${a['oi']}\n${a['iv']} • ${a['pcr']}', style: const TextStyle(color: Colors.white70, fontSize: 11)),
            trailing: const Icon(Icons.arrow_forward_ios, color: Colors.purpleAccent, size: 14),
          ),
        );
      },
    );
  }

  Widget _buildOptionChainTab(FnoOverviewModel d) {
    return SingleChildScrollView(
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
          const Text(
            'Option Chain Matrix',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 12),
          _buildOptionChainTable(d),
        ],
      ),
    );
  }

  Widget _buildGreeksTab(FnoOverviewModel d) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.purpleAccent.withValues(alpha: 0.4)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Options Greeks Analytics Hub',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
              ),
              const SizedBox(height: 12),
              _greekRow('Delta (Δ)', '0.52', 'ATM Sensitivity', Colors.greenAccent),
              _greekRow('Gamma (Γ)', '0.0035', 'Acceleration', Colors.cyanAccent),
              _greekRow('Theta (Θ)', '-12.40 Rs/day', 'Time Decay Burn', Colors.redAccent),
              _greekRow('Vega (V)', '18.20', 'Volatility Impact', Colors.purpleAccent),
              _greekRow('Rho (ρ)', '4.15', 'Interest Rate Impact', Colors.amberAccent),
            ],
          ),
        ),
      ],
    );
  }

  static Widget _greekRow(String name, String val, String desc, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(name, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 13)),
              Text(desc, style: const TextStyle(color: Colors.grey, fontSize: 10)),
            ],
          ),
          Text(val, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
        ],
      ),
    );
  }

  Widget _buildStrategyTab() {
    final strategies = [
      {'name': 'Bull Call Spread', 'bias': 'Bullish', 'risk': 'Defined', 'reward': '1:2.8'},
      {'name': 'Bear Put Spread', 'bias': 'Bearish', 'risk': 'Defined', 'reward': '1:2.5'},
      {'name': 'Iron Condor', 'bias': 'Neutral', 'risk': 'Limited', 'reward': '1:1.9'},
      {'name': 'Long Straddle', 'bias': 'High Volatility', 'risk': 'Premium Paid', 'reward': 'Unlimited'},
      {'name': 'Short Strangle', 'bias': 'Low Volatility', 'risk': 'Managed', 'reward': 'Max Premium'},
    ];

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: strategies.length,
      itemBuilder: (ctx, i) {
        final s = strategies[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: const Icon(Icons.layers_outlined, color: Colors.purpleAccent),
            title: Text(s['name']!, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: Text('Bias: ${s['bias']} • Risk: ${s['risk']} • R:R: ${s['reward']}', style: const TextStyle(color: Colors.white70, fontSize: 11)),
            trailing: const Icon(Icons.arrow_forward_ios, color: Colors.grey, size: 14),
          ),
        );
      },
    );
  }

  Widget _buildPositionsTab(FnoOverviewModel d) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white10),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Live F&O Broker Positions & Margins', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _posTile('Open P&L', '+₹12,450.00', Colors.greenAccent),
                  _posTile('Used Margin', '₹7,23,244.20', Colors.purpleAccent),
                  _posTile('Available Cash', '₹2,76,405.13', Colors.cyanAccent),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  static Widget _posTile(String label, String val, Color col) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 4),
        Text(val, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 12)),
      ],
    );
  }

  Widget _buildSymbolSelector() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          const Text(
            'Target Index:',
            style: TextStyle(color: Colors.white70, fontWeight: FontWeight.bold),
          ),
          DropdownButton<String>(
            value: _selectedSymbol,
            dropdownColor: const Color(0xFF161B22),
            underline: const SizedBox(),
            items: _symbols.map((sym) {
              return DropdownMenuItem<String>(
                value: sym,
                child: Text(
                  sym,
                  style: const TextStyle(
                    color: Colors.purpleAccent,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              );
            }).toList(),
            onChanged: (val) {
              if (val != null) {
                setState(() => _selectedSymbol = val);
                _fetchFno();
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildMetricsOverview(FnoOverviewModel d) {
    final isBullishPcr = d.pcr >= 1.0;
    return Row(
      children: [
        Expanded(
          child: _metricCard(
            'PCR Ratio',
            d.pcr.toStringAsFixed(2),
            isBullishPcr ? 'Bullish Sentiment' : 'Bearish Sentiment',
            isBullishPcr ? Colors.greenAccent : Colors.redAccent,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _metricCard(
            'Max Pain Level',
            '₹${d.maxPain.toStringAsFixed(0)}',
            'Option Expiry Pin',
            Colors.purpleAccent,
          ),
        ),
      ],
    );
  }

  Widget _metricCard(String title, String val, String sub, Color accent) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: accent.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(color: Colors.grey, fontSize: 11)),
          const SizedBox(height: 4),
          Text(val, style: TextStyle(color: accent, fontWeight: FontWeight.bold, fontSize: 18)),
          const SizedBox(height: 2),
          Text(sub, style: const TextStyle(color: Colors.white70, fontSize: 10)),
        ],
      ),
    );
  }

  Widget _buildBuildUpBanner(FnoOverviewModel d) {
    final topStrike = d.optionChain.isNotEmpty ? d.optionChain.first : null;
    final buildType = topStrike?.buildupType ?? 'Long Build-up';
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.purpleAccent.withValues(alpha: 0.15),
            Colors.deepPurple.withValues(alpha: 0.25),
          ],
        ),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.purpleAccent.withValues(alpha: 0.4)),
      ),
      child: Row(
        children: [
          const Icon(Icons.insights, color: Colors.purpleAccent, size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Market Build-Up: $buildType',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                  ),
                ),
                const SizedBox(height: 2),
                const Text(
                  'Institutional Long Accumulation in Progress',
                  style: TextStyle(color: Colors.white70, fontSize: 11),
                ),
              ],
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
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white10),
      ),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          headingRowHeight: 40,
          dataRowMinHeight: 36,
          dataRowMaxHeight: 44,
          columnSpacing: 16,
          columns: const [
            DataColumn(label: Text('CALL OI', style: TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.bold))),
            DataColumn(label: Text('CHG OI', style: TextStyle(color: Colors.grey, fontSize: 10))),
            DataColumn(label: Text('IV', style: TextStyle(color: Colors.grey, fontSize: 10))),
            DataColumn(label: Text('STRIKE', style: TextStyle(color: Colors.amberAccent, fontSize: 11, fontWeight: FontWeight.bold))),
            DataColumn(label: Text('IV', style: TextStyle(color: Colors.grey, fontSize: 10))),
            DataColumn(label: Text('CHG OI', style: TextStyle(color: Colors.grey, fontSize: 10))),
            DataColumn(label: Text('PUT OI', style: TextStyle(color: Colors.redAccent, fontSize: 11, fontWeight: FontWeight.bold))),
          ],
          rows: d.optionChain.map((strike) {
            final isAtm = (strike.strike - d.spotPrice).abs() < 100;
            return DataRow(
              color: isAtm ? WidgetStateProperty.all(Colors.purpleAccent.withValues(alpha: 0.15)) : null,
              cells: [
                DataCell(Text('${strike.callOi}', style: const TextStyle(color: Colors.white, fontSize: 11))),
                DataCell(Text('${strike.callOiChange}', style: TextStyle(color: strike.callOiChange >= 0 ? Colors.greenAccent : Colors.redAccent, fontSize: 11))),
                DataCell(Text('${strike.callIv.toStringAsFixed(1)}%', style: const TextStyle(color: Colors.white70, fontSize: 10))),
                DataCell(Text(
                  '₹${strike.strike.toStringAsFixed(0)}',
                  style: TextStyle(
                    color: isAtm ? Colors.amberAccent : Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                )),
                DataCell(Text('${strike.putIv.toStringAsFixed(1)}%', style: const TextStyle(color: Colors.white70, fontSize: 10))),
                DataCell(Text('${strike.putOiChange}', style: TextStyle(color: strike.putOiChange >= 0 ? Colors.greenAccent : Colors.redAccent, fontSize: 11))),
                DataCell(Text('${strike.putOi}', style: const TextStyle(color: Colors.white, fontSize: 11))),
              ],
            );
          }).toList(),
        ),
      ),
    );
  }
}
