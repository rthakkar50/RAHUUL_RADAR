import 'package:flutter/material.dart';
import '../../../data/models/scan_result_model.dart';
import '../fno/fno_screen.dart';

class StockDetailScreen extends StatefulWidget {
  final ScanResultModel result;

  const StockDetailScreen({super.key, required this.result});

  @override
  State<StockDetailScreen> createState() => _StockDetailScreenState();
}

class _StockDetailScreenState extends State<StockDetailScreen> {
  String _selectedTimeframe = 'Daily';
  final List<String> _timeframes = ['1m', '5m', '15m', '1H', 'Daily', 'Weekly', 'Monthly'];
  bool _isWatchlisted = false;
  bool _isAlertSet = false;
  String _selectedIndicator = 'EMA + VWAP';

  @override
  Widget build(BuildContext context) {
    final result = widget.result;
    final isBuy = result.signal.toUpperCase().contains('BUY');
    final sigColor = isBuy ? Colors.greenAccent : Colors.redAccent;
    final target3 = result.target3;

    final related = _getRelatedStocks(result.sector, result.symbol);

    return Scaffold(
      backgroundColor: const Color(0xFF0B0E14),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B0E14),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  result.symbol,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(color: Colors.cyanAccent.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(4)),
                  child: const Text('NSE • EQ', style: TextStyle(color: Colors.cyanAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                ),
              ],
            ),
            Text(
              '${result.company} • ${result.sector}',
              style: const TextStyle(fontSize: 11, color: Colors.grey),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(_isWatchlisted ? Icons.star : Icons.star_border, color: Colors.amberAccent),
            onPressed: () {
              setState(() => _isWatchlisted = !_isWatchlisted);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(_isWatchlisted ? '${result.symbol} added to Watchlist' : '${result.symbol} removed from Watchlist'),
                  duration: const Duration(seconds: 1),
                ),
              );
            },
          ),
          IconButton(
            icon: Icon(_isAlertSet ? Icons.notifications_active : Icons.notifications_none, color: Colors.cyanAccent),
            onPressed: () {
              setState(() => _isAlertSet = !_isAlertSet);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(_isAlertSet ? 'Price Alert set for ${result.symbol}' : 'Price Alert cancelled'),
                  duration: const Duration(seconds: 1),
                ),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Price Header & Change
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Live CMP (NSE)', style: TextStyle(color: Colors.grey, fontSize: 11)),
                          const SizedBox(height: 2),
                          Row(
                            children: [
                              Text(
                                '₹${result.price.toStringAsFixed(2)}',
                                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
                              ),
                              const SizedBox(width: 8),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                                decoration: BoxDecoration(color: Colors.greenAccent.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(4)),
                                child: const Text('+₹58.40 (+2.42%)', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 11)),
                              ),
                            ],
                          ),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                        decoration: BoxDecoration(
                          color: sigColor.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(color: sigColor),
                        ),
                        child: Text(
                          '${result.signal.toUpperCase()} (${result.confidence.toStringAsFixed(0)}%)',
                          style: TextStyle(color: sigColor, fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // TradingView Interactive Chart Container
                  _buildInteractiveChartContainer(),
                  const SizedBox(height: 16),

                  // Technical & AI Metric Cards
                  _buildTargetGrid(result, sigColor, target3),
                  const SizedBox(height: 16),

                  // AI Analysis & Breakdown
                  _buildAiAnalysisCard(result),
                  const SizedBox(height: 16),

                  // Corporate News & Actions
                  _buildNewsAndActionsCard(result),
                  const SizedBox(height: 16),

                  // Smart Related Sector Leaders
                  _buildRelatedStocksCard(related),
                ],
              ),
            ),
          ),

          // Quick Action Bar
          _buildQuickActionBar(result),
        ],
      ),
    );
  }

  Widget _buildInteractiveChartContainer() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(Icons.show_chart, color: Colors.cyanAccent, size: 18),
                  SizedBox(width: 6),
                  Text('TradingView Pro Chart', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                ],
              ),
              DropdownButton<String>(
                value: _selectedIndicator,
                dropdownColor: const Color(0xFF161B22),
                underline: const SizedBox(),
                items: ['EMA + VWAP', 'RSI (14)', 'MACD (12,26)', 'Volume Profile']
                    .map((ind) => DropdownMenuItem(value: ind, child: Text(ind, style: const TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold))))
                    .toList(),
                onChanged: (v) {
                  if (v != null) setState(() => _selectedIndicator = v);
                },
              ),
            ],
          ),
          const SizedBox(height: 8),
          // Timeframe Selector Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: _timeframes.map((tf) {
                final isSel = tf == _selectedTimeframe;
                return Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: ChoiceChip(
                    label: Text(tf, style: TextStyle(color: isSel ? Colors.black : Colors.white70, fontSize: 10, fontWeight: FontWeight.bold)),
                    selected: isSel,
                    selectedColor: Colors.cyanAccent,
                    backgroundColor: const Color(0xFF0B0E14),
                    onSelected: (sel) {
                      if (sel) setState(() => _selectedTimeframe = tf);
                    },
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 12),
          // Simulated Candlestick Canvas
          Container(
            height: 160,
            width: double.infinity,
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: const Color(0xFF0B0E14), borderRadius: BorderRadius.circular(10)),
            child: CustomPaint(
              painter: ChartPainter(
                indicator: _selectedIndicator,
                symbol: widget.result.symbol,
                basePrice: widget.result.price,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _chartTag('EMA 9: 4,520.0', Colors.cyanAccent),
              _chartTag('EMA 20: 4,480.0', Colors.blueAccent),
              _chartTag('VWAP: 4,510.0', Colors.amberAccent),
              _chartTag('RSI: 64.2 (Bullish)', Colors.greenAccent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _chartTag(String text, Color col) {
    return Text(text, style: TextStyle(color: col, fontSize: 9, fontWeight: FontWeight.bold));
  }

  Widget _buildTargetGrid(ScanResultModel result, Color sigColor, double target3) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: sigColor.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Trade Plan & Targets', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricTile('Entry Price', '₹${result.entry.toStringAsFixed(2)}', Colors.white),
              _metricTile('Stop Loss', '₹${result.stopLoss.toStringAsFixed(2)}', Colors.redAccent),
              _metricTile('Risk Reward', result.riskReward, Colors.amberAccent),
            ],
          ),
          const Divider(color: Colors.white10, height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricTile('Target 1 (T1)', '₹${result.target1.toStringAsFixed(2)}', Colors.greenAccent),
              _metricTile('Target 2 (T2)', '₹${result.target2.toStringAsFixed(2)}', Colors.greenAccent),
              _metricTile('Target 3 (T3)', '₹${target3.toStringAsFixed(2)}', Colors.lightGreenAccent),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Volume: ${result.volume} • Delivery: 68.4%', style: const TextStyle(color: Colors.white70, fontSize: 11)),
              Text('Trade Grade: ${result.tradeGrade}', style: const TextStyle(color: Colors.amberAccent, fontWeight: FontWeight.bold, fontSize: 11)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metricTile(String label, String val, Color col) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 2),
        Text(val, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 13)),
      ],
    );
  }

  Widget _buildAiAnalysisCard(ScanResultModel result) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.purpleAccent.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(Icons.psychology, color: Colors.purpleAccent, size: 18),
                  SizedBox(width: 6),
                  Text('AI Decision Rationale', style: TextStyle(color: Colors.purpleAccent, fontWeight: FontWeight.bold, fontSize: 14)),
                ],
              ),
              Text('Score: ${result.score.toStringAsFixed(1)}/100', style: const TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 13)),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            '${result.symbol} shows strong institutional accumulation with daily & weekly trend alignment. Price is holding firmly above VWAP (+1.4%) with a narrow range CPR breakout.',
            style: const TextStyle(color: Colors.white70, fontSize: 12, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildNewsAndActionsCard(ScanResultModel result) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Corporate News & Actions', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
          const SizedBox(height: 8),
          const Text('• Q1 Revenue up +18% YoY; Net profit beats street estimates.', style: TextStyle(color: Colors.white70, fontSize: 11)),
          const SizedBox(height: 4),
          const Text('• Interim Dividend declared: ₹12.50 per share (Ex-Date: Aug 14).', style: TextStyle(color: Colors.cyanAccent, fontSize: 11)),
        ],
      ),
    );
  }

  Widget _buildRelatedStocksCard(List<Map<String, String>> related) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Sector Peers & Related Stocks', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
        const SizedBox(height: 8),
        SizedBox(
          height: 70,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: related.length,
            itemBuilder: (ctx, i) {
              final r = related[i];
              return Container(
                width: 130,
                margin: const EdgeInsets.only(right: 8),
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFF161B22),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.white10),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(r['symbol']!, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                    Text(r['price']!, style: const TextStyle(color: Colors.greenAccent, fontSize: 11)),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActionBar(ScanResultModel result) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: const BoxDecoration(
        color: Color(0xFF161B22),
        border: Border(top: BorderSide(color: Colors.white10)),
      ),
      child: Row(
        children: [
          Expanded(
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.cyanAccent,
                foregroundColor: Colors.black,
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
              icon: const Icon(Icons.show_chart, size: 16),
              label: const Text('F&O Workspace', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
              onPressed: () {
                Navigator.push(context, MaterialPageRoute(builder: (_) => const FnoScreen()));
              },
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            icon: const Icon(Icons.share, color: Colors.white),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Shared ${result.symbol} trade setup link to clipboard!')),
              );
            },
          ),
        ],
      ),
    );
  }

  List<Map<String, String>> _getRelatedStocks(String sector, String currentSym) {
    if (sector.toUpperCase() == 'PHARMA' || currentSym.contains('DIVIS')) {
      return [
        {'symbol': 'SUNPHARMA', 'price': '₹1,640.00 (+1.8%)'},
        {'symbol': 'CIPLA', 'price': '₹1,520.00 (+2.1%)'},
        {'symbol': 'DRREDDY', 'price': '₹6,840.00 (+1.2%)'},
      ];
    } else if (sector.toUpperCase() == 'BANKING' || currentSym.contains('BANK')) {
      return [
        {'symbol': 'HDFCBANK', 'price': '₹1,640.00 (+0.8%)'},
        {'symbol': 'ICICIBANK', 'price': '₹1,220.00 (+1.4%)'},
        {'symbol': 'SBIN', 'price': '₹845.00 (+2.6%)'},
      ];
    } else {
      return [
        {'symbol': 'TCS', 'price': '₹4,250.00 (+1.1%)'},
        {'symbol': 'INFY', 'price': '₹1,840.00 (+1.5%)'},
        {'symbol': 'RELIANCE', 'price': '₹2,980.00 (+0.9%)'},
      ];
    }
  }
}

class ChartPainter extends CustomPainter {
  final String indicator;
  final String symbol;
  final double basePrice;

  ChartPainter({required this.indicator, this.symbol = 'DEFAULT', this.basePrice = 1000.0});

  @override
  void paint(Canvas canvas, Size size) {
    final bgPaint = Paint()..color = const Color(0xFF0B0E14);
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), bgPaint);

    // Draw Price Grid lines & Axis labels
    final gridPaint = Paint()..color = Colors.white.withValues(alpha: 0.06)..strokeWidth = 1.0;
    final textPainter = TextPainter(textDirection: TextDirection.ltr);

    final h = size.height - 25; // Save bottom 25px for time axis
    final w = size.width - 45; // Save right 45px for price axis

    for (int i = 0; i <= 4; i++) {
      final y = (h / 4) * i;
      canvas.drawLine(Offset(0, y), Offset(w, y), gridPaint);

      final pxPrice = basePrice * (1.05 - (i * 0.025));
      textPainter.text = TextSpan(text: '₹${pxPrice.toStringAsFixed(0)}', style: const TextStyle(color: Colors.grey, fontSize: 8));
      textPainter.layout();
      textPainter.paint(canvas, Offset(w + 4, y - 5));
    }

    // Time Axis Labels
    final times = ['09:15', '11:00', '12:30', '14:00', '15:30'];
    for (int t = 0; t < times.length; t++) {
      final tx = (w / (times.length - 1)) * t;
      textPainter.text = TextSpan(text: times[t], style: const TextStyle(color: Colors.grey, fontSize: 8));
      textPainter.layout();
      textPainter.paint(canvas, Offset(tx - 10, h + 8));
    }

    // Generate unique OHLC sequence using symbol seed
    final seed = symbol.codeUnits.fold(0, (sum, char) => sum + char);
    final count = 16;
    final candleWidth = w / count;

    final emaPoints = <Offset>[];
    final vwapPoints = <Offset>[];

    for (int i = 0; i < count; i++) {
      final randVal = ((seed * (i + 1) * 37) % 100) / 100.0;
      final isUp = randVal > 0.42;
      final color = isUp ? Colors.greenAccent : Colors.redAccent;
      final candlePaint = Paint()..color = color..strokeWidth = 1.5;

      final x = (i + 0.5) * candleWidth;
      final openY = h * (0.25 + ((seed + i * 13) % 40) / 100.0);
      final closeY = isUp ? openY - 15 - (randVal * 20) : openY + 15 + (randVal * 20);
      final highY = (openY < closeY ? openY : closeY) - 8 - (randVal * 10);
      final lowY = (openY > closeY ? openY : closeY) + 8 + (randVal * 10);

      // Draw Wick
      canvas.drawLine(Offset(x, highY), Offset(x, lowY), candlePaint);

      // Draw Body
      final bodyTop = openY < closeY ? openY : closeY;
      final bodyHeight = (openY - closeY).abs().clamp(3.0, 40.0);
      canvas.drawRect(Rect.fromLTWH(x - 3, bodyTop, 6, bodyHeight), candlePaint);

      // Draw Volume Bar
      final volHeight = (10 + (randVal * 25));
      final volPaint = Paint()..color = color.withValues(alpha: 0.3);
      canvas.drawRect(Rect.fromLTWH(x - 3, h - volHeight, 6, volHeight), volPaint);

      // Calculate EMA & VWAP points
      final emaY = (openY + closeY) / 2 + 5;
      final vwapY = emaY - 8;
      emaPoints.add(Offset(x, emaY));
      vwapPoints.add(Offset(x, vwapY));
    }

    // Draw EMA Line (Cyan Overlay)
    if (indicator.contains('EMA') || indicator.contains('VWAP') || indicator == 'EMA + VWAP') {
      final emaPaint = Paint()
        ..color = Colors.cyanAccent
        ..strokeWidth = 2.0
        ..style = PaintingStyle.stroke;
      final emaPath = Path()..moveTo(emaPoints[0].dx, emaPoints[0].dy);
      for (int p = 1; p < emaPoints.length; p++) {
        emaPath.lineTo(emaPoints[p].dx, emaPoints[p].dy);
      }
      canvas.drawPath(emaPath, emaPaint);

      // Draw VWAP Line (Amber Overlay)
      final vwapPaint = Paint()
        ..color = Colors.amberAccent
        ..strokeWidth = 1.5
        ..style = PaintingStyle.stroke;
      final vwapPath = Path()..moveTo(vwapPoints[0].dx, vwapPoints[0].dy);
      for (int p = 1; p < vwapPoints.length; p++) {
        vwapPath.lineTo(vwapPoints[p].dx, vwapPoints[p].dy);
      }
      canvas.drawPath(vwapPath, vwapPaint);
    }

    // Draw RSI / MACD indicator subchart if selected
    if (indicator.contains('RSI')) {
      final rsiPaint = Paint()..color = Colors.purpleAccent..strokeWidth = 1.5..style = PaintingStyle.stroke;
      final rsiPath = Path()..moveTo(0, h * 0.7);
      for (int r = 1; r <= 10; r++) {
        rsiPath.lineTo((w / 10) * r, h * 0.7 + ((r % 2 == 0) ? -15 : 15));
      }
      canvas.drawPath(rsiPath, rsiPaint);
    } else if (indicator.contains('MACD')) {
      final macdPaint = Paint()..color = Colors.greenAccent..strokeWidth = 1.5..style = PaintingStyle.stroke;
      final macdPath = Path()..moveTo(0, h * 0.65);
      for (int m = 1; m <= 10; m++) {
        macdPath.lineTo((w / 10) * m, h * 0.65 + ((m % 3 == 0) ? 12 : -12));
      }
      canvas.drawPath(macdPath, macdPaint);
    }

    // Draw Crosshair at active candle (Center-Right)
    final crossX = w * 0.65;
    final crossY = h * 0.45;
    final crossPaint = Paint()..color = Colors.cyanAccent.withValues(alpha: 0.7)..strokeWidth = 1.0;
    canvas.drawLine(Offset(crossX, 0), Offset(crossX, h), crossPaint);
    canvas.drawLine(Offset(0, crossY), Offset(w, crossY), crossPaint);

    // Crosshair Tooltip Callout Box
    final boxPaint = Paint()..color = const Color(0xFF161B22);
    final borderPaint = Paint()..color = Colors.cyanAccent..strokeWidth = 1.0..style = PaintingStyle.stroke;
    canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromLTWH(crossX - 45, crossY - 22, 90, 18), const Radius.circular(4)), boxPaint);
    canvas.drawRRect(RRect.fromRectAndRadius(Rect.fromLTWH(crossX - 45, crossY - 22, 90, 18), const Radius.circular(4)), borderPaint);

    textPainter.text = TextSpan(text: 'CMP: ₹${basePrice.toStringAsFixed(1)}', style: const TextStyle(color: Colors.cyanAccent, fontSize: 9, fontWeight: FontWeight.bold));
    textPainter.layout();
    textPainter.paint(canvas, Offset(crossX - 40, crossY - 19));
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
