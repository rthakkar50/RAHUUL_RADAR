import 'package:flutter/material.dart';
import '../../../core/network/api_config.dart';

class AdvancedTradingTerminalScreen extends StatefulWidget {
  const AdvancedTradingTerminalScreen({super.key});

  @override
  State<AdvancedTradingTerminalScreen> createState() =>
      _AdvancedTradingTerminalScreenState();
}

class _AdvancedTradingTerminalScreenState
    extends State<AdvancedTradingTerminalScreen>
    with SingleTickerProviderStateMixin {
  late TabController _bottomTabController;

  final String _selectedSymbol = 'NIFTY';
  String _selectedTimeframe = '5M';
  String _selectedTool = 'Cursor';
  final Set<String> _activeIndicators = {'EMA', 'VWAP', 'RSI', 'Volume'};

  bool _isReplayPlaying = false;
  final double _replaySpeed = 1.0;
  bool _showAiOverlay = true;
  final bool _showScannerOverlay = true;
  bool _showOptionGreeks = true;

  final List<String> _timeframes = [
    '1M',
    '3M',
    '5M',
    '15M',
    '30M',
    '1H',
    '4H',
    '1D',
    '1W',
    '1M'
  ];

  final List<String> _drawingTools = [
    'Cursor',
    'Trend Line',
    'Horizontal',
    'Rectangle',
    'Ray',
    'Fibonacci',
    'Risk/Reward',
    'Measure'
  ];

  final List<String> _availableIndicators = [
    'EMA',
    'SMA',
    'VWAP',
    'RSI',
    'MACD',
    'ADX',
    'ATR',
    'SuperTrend',
    'Bollinger Bands',
    'Volume Profile',
    'Pivot Points',
    'CPR'
  ];

  @override
  void initState() {
    super.initState();
    _bottomTabController = TabController(length: 5, vsync: this);
    ApiConfig.logProductionEvent(
      'INFO',
      'Advanced Trading Terminal Screen Initialized.',
    );
  }

  @override
  void dispose() {
    _bottomTabController.dispose();
    super.dispose();
  }

  void _toggleIndicator(String name) {
    setState(() {
      if (_activeIndicators.contains(name)) {
        _activeIndicators.remove(name);
      } else {
        _activeIndicators.add(name);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D1117),
      appBar: AppBar(
        backgroundColor: const Color(0xFF161B22),
        elevation: 0,
        titleSpacing: 8,
        title: Row(
          children: [
            const Icon(Icons.candlestick_chart, color: Colors.cyanAccent, size: 20),
            const SizedBox(width: 8),
            Text(
              'TERMINAL ($_selectedSymbol)',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.bold,
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: const Color(0x3300FF00),
                borderRadius: BorderRadius.circular(4),
                border: Border.all(color: const Color(0x6600FF00)),
              ),
              child: const Text(
                'LIVE WSS',
                style: TextStyle(color: Colors.greenAccent, fontSize: 9, fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(
              _showAiOverlay ? Icons.psychology : Icons.psychology_outlined,
              color: _showAiOverlay ? Colors.purpleAccent : Colors.grey,
              size: 20,
            ),
            tooltip: 'Toggle AI Insights Overlay',
            onPressed: () => setState(() => _showAiOverlay = !_showAiOverlay),
          ),
          IconButton(
            icon: Icon(
              _showOptionGreeks ? Icons.analytics : Icons.analytics_outlined,
              color: _showOptionGreeks ? Colors.amberAccent : Colors.grey,
              size: 20,
            ),
            tooltip: 'Toggle Option Greeks',
            onPressed: () => setState(() => _showOptionGreeks = !_showOptionGreeks),
          ),
          PopupMenuButton<String>(
            icon: const Icon(Icons.tune, color: Colors.white70, size: 20),
            color: const Color(0xFF161B22),
            onSelected: (val) => _toggleIndicator(val),
            itemBuilder: (ctx) => _availableIndicators.map((ind) {
              final active = _activeIndicators.contains(ind);
              return PopupMenuItem(
                value: ind,
                child: Row(
                  children: [
                    Icon(
                      active ? Icons.check_box : Icons.check_box_outline_blank,
                      color: active ? Colors.cyanAccent : Colors.grey,
                      size: 18,
                    ),
                    const SizedBox(width: 8),
                    Text(ind, style: const TextStyle(color: Colors.white, fontSize: 12)),
                  ],
                ),
              );
            }).toList(),
          ),
        ],
      ),
      body: Column(
        children: [
          _buildMarketHeaderBar(),
          _buildTimeframeAndToolsBar(),
          Expanded(
            child: Row(
              children: [
                _buildLeftToolToolbar(),
                Expanded(
                  child: Stack(
                    children: [
                      _buildInteractiveChartCanvas(),
                      if (_showScannerOverlay) _buildScannerSignalBadge(),
                      if (_showAiOverlay) _buildAiRecommendationOverlay(),
                      if (_showOptionGreeks) _buildOptionGreeksOverlay(),
                    ],
                  ),
                ),
                _buildRightQuickOrderPanel(),
              ],
            ),
          ),
          _buildReplayControlBar(),
          _buildBottomDockPanel(),
        ],
      ),
    );
  }

  Widget _buildMarketHeaderBar() {
    return Container(
      height: 38,
      padding: const EdgeInsets.symmetric(horizontal: 12),
      color: const Color(0xFF161B22),
      child: Row(
        children: [
          const Text(
            '₹24,350.80',
            style: TextStyle(
              color: Colors.greenAccent,
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(width: 6),
          const Text(
            '+145.20 (+0.60%)',
            style: TextStyle(color: Colors.greenAccent, fontSize: 10),
          ),
          const Spacer(),
          _headerStatItem('O', '24,210.0'),
          _headerStatItem('H', '24,380.5'),
          _headerStatItem('L', '24,190.2'),
          _headerStatItem('VOL', '14.2M'),
          _headerStatItem('VWAP', '24,295.4'),
        ],
      ),
    );
  }

  Widget _headerStatItem(String label, String val) {
    return Padding(
      padding: const EdgeInsets.only(left: 10),
      child: Row(
        children: [
          Text('$label: ', style: const TextStyle(color: Colors.white38, fontSize: 10)),
          Text(val, style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildTimeframeAndToolsBar() {
    return Container(
      height: 34,
      padding: const EdgeInsets.symmetric(horizontal: 8),
      color: const Color(0xFF0D1117),
      child: Row(
        children: [
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: _timeframes.map((tf) {
                final isSelected = tf == _selectedTimeframe;
                return GestureDetector(
                  onTap: () => setState(() => _selectedTimeframe = tf),
                  child: Container(
                    margin: const EdgeInsets.only(right: 4),
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: isSelected ? const Color(0x3300FFFF) : Colors.transparent,
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(
                        color: isSelected ? Colors.cyanAccent : Colors.transparent,
                      ),
                    ),
                    child: Text(
                      tf,
                      style: TextStyle(
                        color: isSelected ? Colors.cyanAccent : Colors.white60,
                        fontSize: 10,
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          const Spacer(),
          Wrap(
            spacing: 4,
            children: _activeIndicators.take(3).map((ind) {
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: const Color(0x0FFFFFFF),
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(color: Colors.white12),
                ),
                child: Text(
                  ind,
                  style: const TextStyle(color: Colors.white70, fontSize: 9),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildLeftToolToolbar() {
    return Container(
      width: 42,
      color: const Color(0xFF161B22),
      child: Column(
        children: _drawingTools.map((tool) {
          final isSelected = tool == _selectedTool;
          IconData icon;
          switch (tool) {
            case 'Trend Line':
              icon = Icons.show_chart;
              break;
            case 'Horizontal':
              icon = Icons.border_horizontal;
              break;
            case 'Rectangle':
              icon = Icons.crop_square;
              break;
            case 'Fibonacci':
              icon = Icons.format_line_spacing;
              break;
            case 'Risk/Reward':
              icon = Icons.aspect_ratio;
              break;
            case 'Measure':
              icon = Icons.straighten;
              break;
            default:
              icon = Icons.near_me;
          }
          return IconButton(
            icon: Icon(icon, color: isSelected ? Colors.cyanAccent : Colors.white38, size: 18),
            tooltip: tool,
            onPressed: () => setState(() => _selectedTool = tool),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildInteractiveChartCanvas() {
    return Container(
      width: double.infinity,
      height: double.infinity,
      color: const Color(0xFF090D12),
      child: CustomPaint(
        painter: _CandlestickChartPainter(
          timeframe: _selectedTimeframe,
          activeIndicators: _activeIndicators,
        ),
      ),
    );
  }

  Widget _buildScannerSignalBadge() {
    return Positioned(
      top: 12,
      left: 12,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: const Color(0x2600FF00),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.greenAccent),
        ),
        child: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Icon(Icons.bolt, color: Colors.greenAccent, size: 14),
                SizedBox(width: 4),
                Text(
                  'SCANNER BREAKOUT (STRONG BUY)',
                  style: TextStyle(color: Colors.greenAccent, fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            SizedBox(height: 2),
            Text(
              'Score: 92/100 | Confidence: 89% | Vol Spurt: 2.4x',
              style: TextStyle(color: Colors.white70, fontSize: 9),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAiRecommendationOverlay() {
    return Positioned(
      top: 12,
      right: 12,
      child: Container(
        width: 180,
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: const Color(0xE6161B22),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: const Color(0x80E040FB)),
        ),
        child: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Icon(Icons.auto_awesome, color: Colors.purpleAccent, size: 14),
                SizedBox(width: 4),
                Text(
                  'AI SENTINEL COPILOT',
                  style: TextStyle(color: Colors.purpleAccent, fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            SizedBox(height: 4),
            Text(
              'Rec: Long Entry near ₹24,320\nTarget: ₹24,480 | SL: ₹24,260\nRisk Grade: Low (RR 1:2.6)',
              style: TextStyle(color: Colors.white, fontSize: 9, height: 1.3),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOptionGreeksOverlay() {
    return Positioned(
      bottom: 12,
      left: 12,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: const Color(0xD9161B22),
          borderRadius: BorderRadius.circular(6),
          border: Border.all(color: const Color(0x66FFC107)),
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('ATM: 24,350 CE | ', style: TextStyle(color: Colors.amberAccent, fontSize: 9, fontWeight: FontWeight.bold)),
            Text('Delta: 0.52 | Gamma: 0.012 | Theta: -8.4 | Max Pain: 24,300', style: TextStyle(color: Colors.white70, fontSize: 9)),
          ],
        ),
      ),
    );
  }

  Widget _buildRightQuickOrderPanel() {
    return Container(
      width: 140,
      color: const Color(0xFF161B22),
      padding: const EdgeInsets.all(8),
      child: Column(
        children: [
          const Text(
            'QUICK ORDER',
            style: TextStyle(color: Colors.white70, fontSize: 10, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.greenAccent.shade700,
              minimumSize: const Size(double.infinity, 32),
            ),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('BUY Order executed via Paytm Broker Adapter.')),
              );
            },
            child: const Text('BUY', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontSize: 12)),
          ),
          const SizedBox(height: 6),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.redAccent,
              minimumSize: const Size(double.infinity, 32),
            ),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('SELL Order executed via Paytm Broker Adapter.')),
              );
            },
            child: const Text('SELL', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
          ),
          const SizedBox(height: 12),
          const Divider(color: Colors.white12),
          const Text('QTY', style: TextStyle(color: Colors.white38, fontSize: 9)),
          const SizedBox(height: 4),
          Container(
            height: 28,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: Colors.black26,
              borderRadius: BorderRadius.circular(4),
              border: Border.all(color: Colors.white12),
            ),
            child: const Text('50 (1 Lot)', style: TextStyle(color: Colors.white, fontSize: 10)),
          ),
          const Spacer(),
          OutlinedButton(
            style: OutlinedButton.styleFrom(
              side: const BorderSide(color: Colors.cyanAccent),
              minimumSize: const Size(double.infinity, 28),
            ),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Paper Trade simulated successfully.')),
              );
            },
            child: const Text('PAPER TRADE', style: TextStyle(color: Colors.cyanAccent, fontSize: 9)),
          ),
        ],
      ),
    );
  }

  Widget _buildReplayControlBar() {
    return Container(
      height: 30,
      color: const Color(0xFF161B22),
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: Row(
        children: [
          const Icon(Icons.history, color: Colors.cyanAccent, size: 14),
          const SizedBox(width: 6),
          const Text('CHART REPLAY', style: TextStyle(color: Colors.white70, fontSize: 9, fontWeight: FontWeight.bold)),
          const SizedBox(width: 12),
          IconButton(
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(),
            icon: Icon(_isReplayPlaying ? Icons.pause : Icons.play_arrow, color: Colors.white, size: 16),
            onPressed: () => setState(() => _isReplayPlaying = !_isReplayPlaying),
          ),
          const SizedBox(width: 8),
          Text('${_replaySpeed}x', style: const TextStyle(color: Colors.cyanAccent, fontSize: 9)),
          const Spacer(),
          const Text('2026-08-05 15:30:00 IST', style: TextStyle(color: Colors.white38, fontSize: 9)),
        ],
      ),
    );
  }

  Widget _buildBottomDockPanel() {
    return Container(
      height: 120,
      color: const Color(0xFF0D1117),
      child: Column(
        children: [
          Container(
            height: 28,
            color: const Color(0xFF161B22),
            child: TabBar(
              controller: _bottomTabController,
              indicatorColor: Colors.cyanAccent,
              labelColor: Colors.cyanAccent,
              unselectedLabelColor: Colors.white38,
              labelStyle: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
              tabs: const [
                Tab(text: 'POSITIONS (2)'),
                Tab(text: 'ORDERS (5)'),
                Tab(text: 'HOLDINGS'),
                Tab(text: 'JOURNAL'),
                Tab(text: 'PERFORMANCE'),
              ],
            ),
          ),
          Expanded(
            child: TabBarView(
              controller: _bottomTabController,
              children: [
                _dockListView([
                  'NIFTY 24350 CE | Qty: 50 | Avg: ₹120.50 | LTP: ₹142.00 | PnL: +₹1,075.00',
                  'BANKNIFTY 52000 PE | Qty: 30 | Avg: ₹210.00 | LTP: ₹195.00 | PnL: -₹450.00',
                ]),
                _dockListView([
                  'BUY RELIANCE @ 2450.0 | LIMIT | PENDING',
                  'SELL TCS @ 3850.0 | LIMIT | COMPLETE',
                ]),
                _dockListView(['RELIANCE (100 Qty)', 'TCS (50 Qty)', 'INFY (200 Qty)']),
                _dockListView(['Trade #102: Discipline Score 92/100 | Followed Strategy Rules']),
                _dockListView(['Win Rate: 68.4% | Profit Factor: 2.15 | Sharpe Ratio: 1.85']),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _dockListView(List<String> items) {
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (ctx, i) => Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        child: Text(items[i], style: const TextStyle(color: Colors.white70, fontSize: 10)),
      ),
    );
  }
}

class _CandlestickChartPainter extends CustomPainter {
  final String timeframe;
  final Set<String> activeIndicators;

  _CandlestickChartPainter({
    required this.timeframe,
    required this.activeIndicators,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paintGreen = Paint()
      ..color = Colors.greenAccent
      ..strokeWidth = 1.5;
    final paintRed = Paint()
      ..color = Colors.redAccent
      ..strokeWidth = 1.5;
    final paintEma = Paint()
      ..color = Colors.cyanAccent
      ..strokeWidth = 1.2
      ..style = PaintingStyle.stroke;

    final width = size.width;
    final height = size.height;
    final candleWidth = width / 20;

    for (int i = 0; i < 20; i++) {
      final x = i * candleWidth + candleWidth / 2;
      final isGreen = i % 2 == 0;
      final p = isGreen ? paintGreen : paintRed;

      final openY = height * 0.4 + (i * 3 % 20);
      final closeY = isGreen ? openY - 25 : openY + 25;
      final highY = isGreen ? closeY - 15 : openY - 15;
      final lowY = isGreen ? openY + 15 : closeY + 15;

      canvas.drawLine(Offset(x, highY), Offset(x, lowY), p);
      canvas.drawRect(
        Rect.fromLTRB(x - 4, isGreen ? closeY : openY, x + 4, isGreen ? openY : closeY),
        p,
      );
    }

    if (activeIndicators.contains('EMA')) {
      final path = Path();
      for (int i = 0; i < 20; i++) {
        final x = i * candleWidth + candleWidth / 2;
        final y = height * 0.45 - (i * 2);
        if (i == 0) {
          path.moveTo(x, y);
        } else {
          path.lineTo(x, y);
        }
      }
      canvas.drawPath(path, paintEma);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
