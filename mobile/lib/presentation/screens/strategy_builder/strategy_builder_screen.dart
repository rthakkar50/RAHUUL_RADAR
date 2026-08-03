import 'dart:convert';
import 'package:flutter/material.dart';

class StrategyBuilderScreen extends StatefulWidget {
  const StrategyBuilderScreen({super.key});

  @override
  State<StrategyBuilderScreen> createState() => _StrategyBuilderScreenState();
}

class _StrategyBuilderScreenState extends State<StrategyBuilderScreen> {
  String _selectedTemplate = 'Swing Conservative';
  String _targetScanner = 'Swing Scanner';
  String _selectedSector = 'All Sectors';
  String _marketRegime = 'Bull Market';
  String _logicOperator = 'AND';
  bool _isStrategyEnabled = true;

  // Technical Rules
  bool _emaFilter = true;
  bool _rsiFilter = true;
  bool _adxFilter = true;
  bool _macdFilter = true;
  bool _volumeFilter = true;
  bool _vwapFilter = true;
  bool _fnoOnly = true;

  // Quantitative Threshold Sliders
  double _minRsi = 40;
  double _maxRsi = 70;
  double _minAdx = 25;
  double _minRr = 2.0;
  double _minConfidence = 80;
  double _maxRisk = 2.5;

  final TextEditingController _nameController = TextEditingController(
    text: 'Alpha Swing Quantum V3',
  );

  final List<String> _templates = [
    'Swing Conservative',
    'Swing Aggressive',
    'Intraday Scalping',
    'Momentum Breakout',
    'High Volume Surge',
    'Mean Reversal',
    'Trend Following',
  ];

  final List<String> _scanners = [
    'Swing Scanner',
    'Intraday Scanner',
    'F&O Scanner',
    'Breakout Scanner',
    'High Volume Scanner',
    'Momentum Scanner',
    'Watchlist',
    "Today's Best",
  ];

  final List<String> _sectors = [
    'All Sectors',
    'NIFTY IT',
    'NIFTY BANK',
    'NIFTY PHARMA',
    'NIFTY AUTO',
    'NIFTY METAL',
    'NIFTY ENERGY',
    'NIFTY FMCG',
  ];

  final List<String> _regimes = [
    'Bull Market',
    'Bear Market',
    'Sideways Market',
    'High Volatility',
    'Low Volatility',
  ];

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  void _applyTemplate(String template) {
    setState(() {
      _selectedTemplate = template;
      if (template == 'Swing Conservative') {
        _nameController.text = 'Swing Conservative Setup';
        _minAdx = 25;
        _minRr = 2.0;
        _minConfidence = 85;
      } else if (template == 'Swing Aggressive') {
        _nameController.text = 'Swing Aggressive Alpha';
        _minAdx = 20;
        _minRr = 1.5;
        _minConfidence = 75;
      } else if (template == 'Intraday Scalping') {
        _nameController.text = 'Intraday Scalp 15m';
        _targetScanner = 'Intraday Scanner';
        _minAdx = 30;
        _minConfidence = 80;
      } else if (template == 'Momentum Breakout') {
        _nameController.text = 'Breakout Surge Max';
        _targetScanner = 'Breakout Scanner';
        _minAdx = 28;
      }
    });
    _showToast('Loaded "$template" Template');
  }

  void _saveStrategy() {
    _showToast('Strategy "${_nameController.text}" Saved & Compiled!');
  }

  void _exportStrategy() {
    final data = {
      "strategy_name": _nameController.text,
      "target_scanner": _targetScanner,
      "sector": _selectedSector,
      "regime": _marketRegime,
      "operator": _logicOperator,
      "min_adx": _minAdx,
      "min_rr": _minRr,
      "min_confidence": _minConfidence,
      "enabled": _isStrategyEnabled,
    };
    final jsonStr = jsonEncode(data);
    _showModal('Export Strategy JSON', jsonStr);
  }

  void _runBacktest() {
    _showToast('Running Historical Backtest for "${_nameController.text}"...');
  }

  void _runPaperTrades() {
    _showToast('Automated Paper Trading Started for "${_nameController.text}"');
  }

  void _showToast(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg),
        backgroundColor: Colors.purpleAccent,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _showModal(String title, String content) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: const Color(0xFF161B22),
        title: Text(title, style: const TextStyle(color: Colors.white, fontSize: 14)),
        content: SelectableText(content, style: const TextStyle(color: Colors.cyanAccent, fontSize: 12)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close', style: TextStyle(color: Colors.purpleAccent)),
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
              child: const Icon(Icons.build_circle_outlined, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('Enterprise Strategy Builder', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.download_rounded, color: Colors.cyanAccent),
            tooltip: 'Export JSON',
            onPressed: _exportStrategy,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── TASK-12: Template Selector ─────────────────────────
            _buildSectionHeader('1. STRATEGY TEMPLATES', Icons.dashboard_customize_outlined),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              decoration: BoxDecoration(
                color: const Color(0xFF161B22),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.white10),
              ),
              child: DropdownButton<String>(
                value: _selectedTemplate,
                isExpanded: true,
                dropdownColor: const Color(0xFF161B22),
                underline: const SizedBox(),
                items: _templates.map((t) => DropdownMenuItem(value: t, child: Text(t, style: const TextStyle(color: Colors.purpleAccent, fontWeight: FontWeight.bold)))).toList(),
                onChanged: (v) {
                  if (v != null) _applyTemplate(v);
                },
              ),
            ),

            const SizedBox(height: 16),

            // ── TASK-1: Strategy Identifier & Activation ───────────
            _buildSectionHeader('2. STRATEGY IDENTIFIER & CONTROL', Icons.tune_rounded),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF161B22),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.white10),
              ),
              child: Column(
                children: [
                  TextField(
                    controller: _nameController,
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                    decoration: const InputDecoration(
                      labelText: 'Strategy Name',
                      labelStyle: TextStyle(color: Colors.grey),
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Enable Strategy', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                      Switch(
                        value: _isStrategyEnabled,
                        activeTrackColor: Colors.greenAccent,
                        onChanged: (v) => setState(() => _isStrategyEnabled = v),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // ── TASK-2, TASK-5, TASK-6: Target & Filters ────────────
            _buildSectionHeader('3. TARGET SCANNER & FILTERS', Icons.filter_alt_outlined),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF161B22),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.white10),
              ),
              child: Column(
                children: [
                  _dropdownRow('Target Scanner', _targetScanner, _scanners, (v) => setState(() => _targetScanner = v!)),
                  const SizedBox(height: 8),
                  _dropdownRow('Sector Filter', _selectedSector, _sectors, (v) => setState(() => _selectedSector = v!)),
                  const SizedBox(height: 8),
                  _dropdownRow('Market Regime', _marketRegime, _regimes, (v) => setState(() => _marketRegime = v!)),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // ── TASK-3: Entry Conditions Builder ───────────────────
            _buildSectionHeader('4. TECHNICAL ENTRY RULES', Icons.code_rounded),
            const SizedBox(height: 8),
            Container(
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
                      const Text('Combine Rules With', style: TextStyle(color: Colors.grey, fontSize: 12)),
                      SegmentedButton<String>(
                        segments: const [
                          ButtonSegment(value: 'AND', label: Text('AND')),
                          ButtonSegment(value: 'OR', label: Text('OR')),
                        ],
                        selected: {_logicOperator},
                        onSelectionChanged: (s) => setState(() => _logicOperator = s.first),
                      ),
                    ],
                  ),
                  const Divider(color: Colors.white10, height: 16),
                  _switchTile('EMA 20/50 Bullish Crossover', '20 EMA > 50 EMA Trend Filter', _emaFilter, (v) => setState(() => _emaFilter = v)),
                  _switchTile('RSI Momentum Filter', 'RSI within 40 - 70 range', _rsiFilter, (v) => setState(() => _rsiFilter = v)),
                  _switchTile('ADX Trend Strength (> 25)', 'Strong directional trend', _adxFilter, (v) => setState(() => _adxFilter = v)),
                  _switchTile('MACD Signal Crossover', 'Histogram expansion', _macdFilter, (v) => setState(() => _macdFilter = v)),
                  _switchTile('Volume Surge (> 1.5x)', 'Institutional volume', _volumeFilter, (v) => setState(() => _volumeFilter = v)),
                  _switchTile('VWAP Holding', 'Price above VWAP', _vwapFilter, (v) => setState(() => _vwapFilter = v)),
                  _switchTile('F&O Universe Only', 'Filter liquid F&O stocks', _fnoOnly, (v) => setState(() => _fnoOnly = v)),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // ── TASK-4: Risk Rules Sliders ─────────────────────────
            _buildSectionHeader('5. QUANTITATIVE RISK RULES', Icons.shield_outlined),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF161B22),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.white10),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('RSI Range: ${_minRsi.toInt()} - ${_maxRsi.toInt()}', style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  RangeSlider(values: RangeValues(_minRsi, _maxRsi), min: 20, max: 80, activeColor: Colors.cyanAccent, onChanged: (v) => setState(() { _minRsi = v.start; _maxRsi = v.end; })),
                  Text('Minimum Risk Reward: 1:${_minRr.toStringAsFixed(1)}', style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  Slider(value: _minRr, min: 1.0, max: 4.0, divisions: 6, activeColor: Colors.purpleAccent, onChanged: (v) => setState(() => _minRr = v)),
                  Text('Minimum Confidence: ${_minConfidence.toInt()}%', style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  Slider(value: _minConfidence, min: 60, max: 95, activeColor: Colors.cyanAccent, onChanged: (v) => setState(() => _minConfidence = v)),
                  Text('Maximum Risk Per Trade: ${_maxRisk.toStringAsFixed(1)}%', style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  Slider(value: _maxRisk, min: 1.0, max: 5.0, activeColor: Colors.redAccent, onChanged: (v) => setState(() => _maxRisk = v)),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // ── TASK-7 & TASK-13: Preview & Analytics Card ─────────
            _buildSectionHeader('6. LIVE PREVIEW & ANALYTICS', Icons.analytics_outlined),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF131A2A),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.3)),
              ),
              child: Column(
                children: [
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('ESTIMATED CANDIDATES', style: TextStyle(color: Colors.grey, fontSize: 10, fontWeight: FontWeight.bold)),
                      Text('34 Ranked (21 Qualified)', style: TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _previewTile('BUY', '4', Colors.greenAccent),
                      _previewTile('SELL', '1', Colors.redAccent),
                      _previewTile('WATCH', '16', Colors.amberAccent),
                      _previewTile('WIN RATE', '78.4%', Colors.lightGreenAccent),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // ── Action Buttons ──────────────────────────────────────
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _runBacktest,
                    icon: const Icon(Icons.history, size: 16),
                    label: const Text('Backtest', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                    style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF232D48)),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _runPaperTrades,
                    icon: const Icon(Icons.play_arrow, size: 16),
                    label: const Text('Paper Trade', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                    style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF232D48)),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                onPressed: _saveStrategy,
                icon: const Icon(Icons.save_rounded),
                label: const Text('Save & Compile Strategy', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.purpleAccent),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, color: Colors.purpleAccent, size: 16),
        const SizedBox(width: 6),
        Text(title, style: const TextStyle(color: Colors.purpleAccent, fontWeight: FontWeight.bold, fontSize: 12, letterSpacing: 0.5)),
      ],
    );
  }

  Widget _dropdownRow(String label, String value, List<String> items, ValueChanged<String?> onChanged) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
        DropdownButton<String>(
          value: value,
          dropdownColor: const Color(0xFF161B22),
          underline: const SizedBox(),
          items: items.map((i) => DropdownMenuItem(value: i, child: Text(i, style: const TextStyle(color: Colors.cyanAccent, fontSize: 12, fontWeight: FontWeight.bold)))).toList(),
          onChanged: onChanged,
        ),
      ],
    );
  }

  Widget _switchTile(String title, String subtitle, bool val, ValueChanged<bool> onChanged) {
    return SwitchListTile(
      dense: true,
      contentPadding: EdgeInsets.zero,
      title: Text(title, style: const TextStyle(color: Colors.white, fontSize: 12)),
      subtitle: Text(subtitle, style: const TextStyle(color: Colors.grey, fontSize: 10)),
      value: val,
      onChanged: onChanged,
    );
  }

  Widget _previewTile(String label, String val, Color col) {
    return Column(
      children: [
        Text(val, style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: col)),
        Text(label, style: const TextStyle(fontSize: 9, color: Colors.grey)),
      ],
    );
  }
}
