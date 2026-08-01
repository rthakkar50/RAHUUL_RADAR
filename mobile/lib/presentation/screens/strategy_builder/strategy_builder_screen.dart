import 'package:flutter/material.dart';

class StrategyBuilderScreen extends StatefulWidget {
  const StrategyBuilderScreen({super.key});

  @override
  State<StrategyBuilderScreen> createState() => _StrategyBuilderScreenState();
}

class _StrategyBuilderScreenState extends State<StrategyBuilderScreen> {
  bool _emaFilter = true;
  bool _rsiFilter = true;
  bool _adxFilter = true;
  bool _macdFilter = true;
  bool _volumeFilter = true;
  bool _fnoOnly = true;

  double _minRsi = 40;
  double _maxRsi = 70;
  double _minAdx = 25;

  final TextEditingController _strategyNameController = TextEditingController(
    text: 'Alpha Swing Quantum V3',
  );

  @override
  void dispose() {
    _strategyNameController.dispose();
    super.dispose();
  }

  void _saveStrategy() {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Strategy "${_strategyNameController.text}" Saved & Compiled Successfully!',
        ),
        backgroundColor: Colors.greenAccent,
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
                  colors: [Colors.purpleAccent, Colors.indigoAccent],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(
                Icons.build_circle_outlined,
                color: Colors.white,
                size: 18,
              ),
            ),
            const SizedBox(width: 8),
            const Text(
              'Visual Strategy Builder',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildStrategyNameInput(),
            const SizedBox(height: 16),
            _buildIndicatorToggles(),
            const SizedBox(height: 16),
            _buildSliderFilters(),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                onPressed: _saveStrategy,
                icon: const Icon(Icons.save),
                label: const Text(
                  'Save & Activate Strategy',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.purpleAccent,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStrategyNameInput() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Strategy Identifier',
            style: TextStyle(
              color: Colors.grey,
              fontSize: 11,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _strategyNameController,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              contentPadding: EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 10,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIndicatorToggles() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Technical Rule Enforcers',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 14,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 10),
          SwitchListTile(
            title: const Text(
              'EMA 20/50 Bullish Crossover',
              style: TextStyle(color: Colors.white, fontSize: 13),
            ),
            subtitle: const Text(
              'Fast 20 EMA > Slow 50 EMA on Daily Chart',
              style: TextStyle(color: Colors.grey, fontSize: 11),
            ),
            value: _emaFilter,
            onChanged: (v) => setState(() => _emaFilter = v),
          ),
          SwitchListTile(
            title: const Text(
              'RSI Momentum Range Filter',
              style: TextStyle(color: Colors.white, fontSize: 13),
            ),
            subtitle: const Text(
              'RSI Relative Strength Index within bounds',
              style: TextStyle(color: Colors.grey, fontSize: 11),
            ),
            value: _rsiFilter,
            onChanged: (v) => setState(() => _rsiFilter = v),
          ),
          SwitchListTile(
            title: const Text(
              'ADX Trend Strength (> 25)',
              style: TextStyle(color: Colors.white, fontSize: 13),
            ),
            subtitle: const Text(
              'Average Directional Index trend filter',
              style: TextStyle(color: Colors.grey, fontSize: 11),
            ),
            value: _adxFilter,
            onChanged: (v) => setState(() => _adxFilter = v),
          ),
          SwitchListTile(
            title: const Text(
              'MACD Histogram Signal Crossover',
              style: TextStyle(color: Colors.white, fontSize: 13),
            ),
            subtitle: const Text(
              'MACD Line above Signal Line',
              style: TextStyle(color: Colors.grey, fontSize: 11),
            ),
            value: _macdFilter,
            onChanged: (v) => setState(() => _macdFilter = v),
          ),
          SwitchListTile(
            title: const Text(
              'Volume Expansion (> 1.5x Avg)',
              style: TextStyle(color: Colors.white, fontSize: 13),
            ),
            subtitle: const Text(
              'Institutional Volume Surge detection',
              style: TextStyle(color: Colors.grey, fontSize: 11),
            ),
            value: _volumeFilter,
            onChanged: (v) => setState(() => _volumeFilter = v),
          ),
          SwitchListTile(
            title: const Text(
              'F&O Derivatives Universe Only',
              style: TextStyle(color: Colors.white, fontSize: 13),
            ),
            subtitle: const Text(
              'Filter for liquid F&O stocks',
              style: TextStyle(color: Colors.grey, fontSize: 11),
            ),
            value: _fnoOnly,
            onChanged: (v) => setState(() => _fnoOnly = v),
          ),
        ],
      ),
    );
  }

  Widget _buildSliderFilters() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Quantitative Threshold Sliders',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 14,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'Minimum ADX Strength: ${_minAdx.toInt()}',
            style: const TextStyle(color: Colors.grey, fontSize: 12),
          ),
          Slider(
            value: _minAdx,
            min: 10,
            max: 50,
            activeColor: Colors.purpleAccent,
            onChanged: (v) => setState(() => _minAdx = v),
          ),
          Text(
            'RSI Lower Limit: ${_minRsi.toInt()} | Upper Limit: ${_maxRsi.toInt()}',
            style: const TextStyle(color: Colors.grey, fontSize: 12),
          ),
          RangeSlider(
            values: RangeValues(_minRsi, _maxRsi),
            min: 20,
            max: 80,
            activeColor: Colors.cyanAccent,
            onChanged: (v) => setState(() {
              _minRsi = v.start;
              _maxRsi = v.end;
            }),
          ),
        ],
      ),
    );
  }
}
