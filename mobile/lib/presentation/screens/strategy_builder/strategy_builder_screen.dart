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
  bool _isFavourite = true;

  // Version Control (PART-14)
  String _strategyVersion = 'v1.0.2';
  final String _createdDate = '2026-08-01';
  final String _modifiedDate = '2026-08-04';

  // Technical Rules (PART-2)
  bool _emaFilter = true;
  bool _smaFilter = true;
  bool _rsiFilter = true;
  bool _adxFilter = true;
  bool _macdFilter = true;
  bool _volumeFilter = true;
  bool _vwapFilter = true;
  bool _atrFilter = true;
  bool _structureFilter = true;
  bool _fnoOnly = true;

  // Quantitative Risk Threshold Sliders (PART-3)
  double _minRsi = 40;
  double _maxRsi = 70;
  double _minAdx = 25;
  double _minRr = 2.0;
  double _minConfidence = 80;
  double _minAiScore = 70;
  double _maxRisk = 2.5;
  double _maxDrawdown = 10.0;

  // Backtest Range (PART-8)
  String _backtestPeriod = '6 Months';

  final TextEditingController _nameController = TextEditingController(
    text: 'Alpha Swing Quantum V3',
  );

  final List<String> _templates = [
    'Swing Conservative',
    'Swing Aggressive',
    'Intraday Scalper',
    'Momentum Hunter',
    'Breakout Master',
    'High Volume Surge',
    'Mean Reversal',
    'Trend Following',
  ];

  final List<String> _scanners = [
    'Swing Scanner',
    'Intraday Scanner',
    'F&O Scanner',
    'Breakout Scanner',
    'Momentum Scanner',
    'High Volume Scanner',
    'Watchlist',
    "Today's Best",
  ];

  final List<String> _sectors = [
    'All Sectors',
    'NIFTY BANK',
    'NIFTY IT',
    'NIFTY AUTO',
    'NIFTY METAL',
    'NIFTY ENERGY',
    'NIFTY FMCG',
    'NIFTY PHARMA',
    'NIFTY REALTY',
    'NIFTY PSU',
  ];

  final List<String> _regimes = [
    'Bull Market',
    'Bear Market',
    'Sideways Market',
    'High Volatility',
    'Low Volatility',
    'Gap Up',
    'Gap Down',
  ];

  final List<String> _periods = [
    '1 Month',
    '3 Months',
    '6 Months',
    '1 Year',
    '3 Years',
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
      } else if (template == 'Intraday Scalper') {
        _nameController.text = 'Intraday Scalp 15m';
        _targetScanner = 'Intraday Scanner';
        _minAdx = 30;
      } else if (template == 'Momentum Hunter') {
        _nameController.text = 'Momentum Surge Hunter';
        _targetScanner = 'Momentum Scanner';
      } else if (template == 'Breakout Master') {
        _nameController.text = 'CPR Breakout Master';
        _targetScanner = 'Breakout Scanner';
      }
    });
    _showToast('Loaded "$template" Template');
  }

  void _saveStrategy() {
    _showToast('Strategy "${_nameController.text}" Saved & Compiled!');
  }

  void _duplicateStrategy() {
    setState(() {
      _nameController.text = '${_nameController.text} (Copy)';
    });
    _showToast('Duplicated Strategy Successfully!');
  }

  void _rollbackVersion() {
    setState(() {
      _strategyVersion = 'v1.0.1 (Rolled Back)';
    });
    _showToast('Rolled Back to Version v1.0.1');
  }

  void _exportStrategy() {
    final data = {
      "strategy_name": _nameController.text,
      "version": _strategyVersion,
      "target_scanner": _targetScanner,
      "sector": _selectedSector,
      "regime": _marketRegime,
      "operator": _logicOperator,
      "min_adx": _minAdx,
      "min_rr": _minRr,
      "min_confidence": _minConfidence,
      "enabled": _isStrategyEnabled,
      "favourite": _isFavourite,
    };
    final jsonStr = jsonEncode(data);
    _showModal('Export Strategy JSON & ZIP Backup', jsonStr);
  }

  void _runBacktest() {
    _showModal(
      'Backtest Results ($_backtestPeriod)',
      '• Historical Win Rate: 78.4%\n• Profit Factor: 2.45\n• Average RR: 1:2.5\n• Max Drawdown: 4.2%\n• Total Trades Executed: 142\n• Top Performing Sector: NIFTY IT (+18.2%)',
    );
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
        title: Text(title, style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold)),
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
              child: const Icon(Icons.psychology_outlined, color: Colors.white, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('Enterprise Strategy Studio', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(_isFavourite ? Icons.star : Icons.star_border, color: Colors.amberAccent),
            tooltip: 'Favourite',
            onPressed: () => setState(() => _isFavourite = !_isFavourite),
          ),
          IconButton(
            icon: const Icon(Icons.copy, color: Colors.cyanAccent, size: 18),
            tooltip: 'Duplicate Strategy',
            onPressed: _duplicateStrategy,
          ),
          IconButton(
            icon: const Icon(Icons.download_rounded, color: Colors.purpleAccent),
            tooltip: 'Export JSON/ZIP',
            onPressed: _exportStrategy,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── PART-14: Strategy Metadata Header ───────────────────
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF161B22),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.purpleAccent.withValues(alpha: 0.3)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('VERSION: $_strategyVersion', style: const TextStyle(color: Colors.purpleAccent, fontWeight: FontWeight.w800, fontSize: 11)),
                      Text('Created: $_createdDate | Modified: $_modifiedDate', style: const TextStyle(color: Colors.grey, fontSize: 9)),
                    ],
                  ),
                  OutlinedButton.icon(
                    onPressed: _rollbackVersion,
                    icon: const Icon(Icons.undo, size: 12, color: Colors.amberAccent),
                    label: const Text('Rollback', style: TextStyle(color: Colors.amberAccent, fontSize: 10)),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // ── PART-13: Template Selector ─────────────────────────
            _buildSectionHeader('1. BUILT-IN TEMPLATES', Icons.dashboard_customize_outlined),
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

            // ── PART-1: Identifier & Control ─────────────────────────
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

            // ── PART-4, PART-5, PART-6: Targets & Filters ───────────
            _buildSectionHeader('3. SCANNER & MARKET REGIME FILTERS', Icons.filter_alt_outlined),
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

            // ── PART-2: No-Code Condition Builder ──────────────────
            _buildSectionHeader('4. NO-CODE TECHNICAL CONDITIONS', Icons.code_rounded),
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
                      const Text('Condition Operator', style: TextStyle(color: Colors.grey, fontSize: 12)),
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
                  _switchTile('EMA 20/50 Crossover', '20 EMA > 50 EMA Daily', _emaFilter, (v) => setState(() => _emaFilter = v)),
                  _switchTile('SMA 200 Trend Line', 'Price above 200 SMA', _smaFilter, (v) => setState(() => _smaFilter = v)),
                  _switchTile('RSI Momentum Range', 'RSI within custom range', _rsiFilter, (v) => setState(() => _rsiFilter = v)),
                  _switchTile('ADX Trend Strength (> 25)', 'Strong direction filter', _adxFilter, (v) => setState(() => _adxFilter = v)),
                  _switchTile('MACD Signal Crossover', 'Histogram expansion', _macdFilter, (v) => setState(() => _macdFilter = v)),
                  _switchTile('Volume Surge (> 1.5x)', 'Institutional expansion', _volumeFilter, (v) => setState(() => _volumeFilter = v)),
                  _switchTile('VWAP Holding', 'Price holding above VWAP', _vwapFilter, (v) => setState(() => _vwapFilter = v)),
                  _switchTile('ATR Volatility Expansion', 'ATR breakout filter', _atrFilter, (v) => setState(() => _atrFilter = v)),
                  _switchTile('Market Structure Breakout', 'Narrow CPR range', _structureFilter, (v) => setState(() => _structureFilter = v)),
                  _switchTile('F&O Derivatives Only', 'Filter liquid F&O stocks', _fnoOnly, (v) => setState(() => _fnoOnly = v)),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // ── PART-3: Quantitative Risk Rules Sliders ────────────
            _buildSectionHeader('5. QUANTITATIVE RISK BUILDER', Icons.shield_outlined),
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
                  Text('Minimum AI Score: ${_minAiScore.toInt()}/100', style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  Slider(value: _minAiScore, min: 50, max: 90, activeColor: Colors.lightGreenAccent, onChanged: (v) => setState(() => _minAiScore = v)),
                  Text('Minimum Confidence: ${_minConfidence.toInt()}%', style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  Slider(value: _minConfidence, min: 60, max: 95, activeColor: Colors.cyanAccent, onChanged: (v) => setState(() => _minConfidence = v)),
                  Text('Maximum Risk Per Trade: ${_maxRisk.toStringAsFixed(1)}%', style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  Slider(value: _maxRisk, min: 1.0, max: 5.0, activeColor: Colors.redAccent, onChanged: (v) => setState(() => _maxRisk = v)),
                  Text('Maximum Drawdown Limit: ${_maxDrawdown.toStringAsFixed(1)}%', style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  Slider(value: _maxDrawdown, min: 5.0, max: 20.0, activeColor: Colors.orangeAccent, onChanged: (v) => setState(() => _maxDrawdown = v)),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // ── PART-7 & PART-10: AI Preview & Analytics Card ──────
            _buildSectionHeader('6. AI PREVIEW & ANALYTICS TRACKER', Icons.analytics_outlined),
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
                      _previewTile('PROFIT FACTOR', '2.45', Colors.cyanAccent),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // ── PART-8: Backtest Period Picker ─────────────────────
            _buildSectionHeader('7. HISTORICAL BACKTEST INTEGRATION', Icons.history_rounded),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              decoration: BoxDecoration(
                color: const Color(0xFF161B22),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.white10),
              ),
              child: DropdownButton<String>(
                value: _backtestPeriod,
                isExpanded: true,
                dropdownColor: const Color(0xFF161B22),
                underline: const SizedBox(),
                items: _periods.map((p) => DropdownMenuItem(value: p, child: Text('Backtest Horizon: $p', style: const TextStyle(color: Colors.cyanAccent, fontSize: 12, fontWeight: FontWeight.bold)))).toList(),
                onChanged: (v) => setState(() => _backtestPeriod = v!),
              ),
            ),

            const SizedBox(height: 20),

            // ── Action Buttons ──────────────────────────────────────
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _runBacktest,
                    icon: const Icon(Icons.play_circle_fill_rounded, size: 16),
                    label: const Text('Run Backtest', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                    style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF232D48)),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _runPaperTrades,
                    icon: const Icon(Icons.rocket_launch_rounded, size: 16),
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
                label: const Text('Save & Compile AI Strategy', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
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
        Text(val, style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: col)),
        Text(label, style: const TextStyle(fontSize: 8, color: Colors.grey)),
      ],
    );
  }
}
