import 'package:flutter/material.dart';
import '../../../core/network/api_config.dart';

class MarketReplayScreen extends StatefulWidget {
  const MarketReplayScreen({super.key});

  @override
  State<MarketReplayScreen> createState() => _MarketReplayScreenState();
}

class _MarketReplayScreenState extends State<MarketReplayScreen> {
  final String _selectedSymbol = 'RELIANCE';
  String _selectedTimeframe = '5M';
  bool _isPlaying = false;
  double _replaySpeed = 1.0;
  int _currentCandleIndex = 12;

  final List<String> _timeframes = ['1M', '3M', '5M', '15M', '30M', '1H', '1D'];
  final List<double> _speeds = [1.0, 2.0, 5.0, 10.0, 25.0, 50.0];

  @override
  void initState() {
    super.initState();
    ApiConfig.logProductionEvent(
      'INFO',
      'Market Replay & Trading Simulator Screen Initialized.',
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0D1117),
      appBar: AppBar(
        backgroundColor: const Color(0xFF161B22),
        elevation: 0,
        title: Row(
          children: [
            const Icon(Icons.history, color: Colors.cyanAccent, size: 20),
            const SizedBox(width: 8),
            Text(
              'MARKET REPLAY ($_selectedSymbol)',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.bold,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.bookmark_add, color: Colors.cyanAccent, size: 20),
            tooltip: 'Bookmark Session',
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Replay session bookmarked.')),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          _buildTopTimeframeBar(),
          Expanded(
            child: Stack(
              children: [
                _buildReplayCandlestickChart(),
                _buildAiReplayBadge(),
                _buildSimulatorOverlay(),
              ],
            ),
          ),
          _buildReplayControlBar(),
          _buildSimulatorStatsDock(),
        ],
      ),
    );
  }

  Widget _buildTopTimeframeBar() {
    return Container(
      height: 36,
      color: const Color(0xFF161B22),
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: Row(
        children: [
          const Text('Session: 2026-08-01 | ', style: TextStyle(color: Colors.white70, fontSize: 10)),
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
                      border: Border.all(color: isSelected ? Colors.cyanAccent : Colors.transparent),
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
        ],
      ),
    );
  }

  Widget _buildReplayCandlestickChart() {
    return Container(
      width: double.infinity,
      height: double.infinity,
      color: const Color(0xFF090D12),
      child: CustomPaint(
        painter: _ReplayChartPainter(candleCount: _currentCandleIndex),
      ),
    );
  }

  Widget _buildAiReplayBadge() {
    return Positioned(
      top: 12,
      left: 12,
      child: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: const Color(0xE6161B22),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.purpleAccent),
        ),
        child: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Icon(Icons.auto_awesome, color: Colors.purpleAccent, size: 14),
                SizedBox(width: 4),
                Text('AI REPLAY EVENT DETECTED', style: TextStyle(color: Colors.purpleAccent, fontSize: 10, fontWeight: FontWeight.bold)),
              ],
            ),
            SizedBox(height: 2),
            Text('Scanner Breakout @ ₹2,420.0 | Confidence 89%', style: TextStyle(color: Colors.white, fontSize: 9)),
          ],
        ),
      ),
    );
  }

  Widget _buildSimulatorOverlay() {
    return Positioned(
      top: 12,
      right: 12,
      child: Column(
        children: [
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.greenAccent.shade700,
              minimumSize: const Size(90, 30),
            ),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Simulated BUY Order placed at replay candle price.')),
              );
            },
            child: const Text('SIM BUY', style: TextStyle(color: Colors.black, fontSize: 10, fontWeight: FontWeight.bold)),
          ),
          const SizedBox(height: 6),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.redAccent,
              minimumSize: const Size(90, 30),
            ),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Simulated SELL Order placed at replay candle price.')),
              );
            },
            child: const Text('SIM SELL', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  Widget _buildReplayControlBar() {
    return Container(
      height: 44,
      color: const Color(0xFF161B22),
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          IconButton(
            icon: const Icon(Icons.skip_previous, color: Colors.white70, size: 20),
            onPressed: () {
              if (_currentCandleIndex > 1) {
                setState(() => _currentCandleIndex--);
              }
            },
          ),
          IconButton(
            icon: Icon(_isPlaying ? Icons.pause_circle_filled : Icons.play_circle_filled, color: Colors.cyanAccent, size: 28),
            onPressed: () => setState(() => _isPlaying = !_isPlaying),
          ),
          IconButton(
            icon: const Icon(Icons.skip_next, color: Colors.white70, size: 20),
            onPressed: () {
              if (_currentCandleIndex < 20) {
                setState(() => _currentCandleIndex++);
              }
            },
          ),
          const SizedBox(width: 12),
          DropdownButton<double>(
            value: _replaySpeed,
            dropdownColor: const Color(0xFF161B22),
            style: const TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold),
            underline: const SizedBox(),
            items: _speeds.map((s) => DropdownMenuItem(value: s, child: Text('${s}x'))).toList(),
            onChanged: (val) {
              if (val != null) setState(() => _replaySpeed = val);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSimulatorStatsDock() {
    return Container(
      height: 50,
      color: const Color(0xFF0D1117),
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          _statText('Simulated PnL', '+₹1,850.00', Colors.greenAccent),
          _statText('Sim Win Rate', '75.0%', Colors.cyanAccent),
          _statText('Discipline Score', '94/100', Colors.amberAccent),
        ],
      ),
    );
  }

  Widget _statText(String label, String val, Color color) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.white38, fontSize: 9)),
        Text(val, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold)),
      ],
    );
  }
}

class _ReplayChartPainter extends CustomPainter {
  final int candleCount;

  _ReplayChartPainter({required this.candleCount});

  @override
  void paint(Canvas canvas, Size size) {
    final paintGreen = Paint()
      ..color = Colors.greenAccent
      ..strokeWidth = 1.5;
    final paintRed = Paint()
      ..color = Colors.redAccent
      ..strokeWidth = 1.5;

    final width = size.width;
    final height = size.height;
    final candleWidth = width / 20;

    for (int i = 0; i < candleCount; i++) {
      final x = i * candleWidth + candleWidth / 2;
      final isGreen = i % 2 == 0;
      final p = isGreen ? paintGreen : paintRed;

      final openY = height * 0.4 + (i * 4 % 25);
      final closeY = isGreen ? openY - 20 : openY + 20;
      final highY = isGreen ? closeY - 10 : openY - 10;
      final lowY = isGreen ? openY + 10 : closeY + 10;

      canvas.drawLine(Offset(x, highY), Offset(x, lowY), p);
      canvas.drawRect(
        Rect.fromLTRB(x - 4, isGreen ? closeY : openY, x + 4, isGreen ? openY : closeY),
        p,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
