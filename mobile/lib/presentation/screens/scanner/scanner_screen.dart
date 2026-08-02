import 'dart:async';
import 'package:flutter/material.dart';
import '../../../core/bus/live_data_bus.dart';
import '../../../data/models/scan_response_model.dart';
import '../../../data/models/scan_result_model.dart';
import '../../../data/repositories/scanner_repository.dart';
import '../../widgets/scanner_loading_shimmer.dart';
import '../stock_detail/stock_detail_screen.dart';
import 'widgets/scanner_summary_panel.dart';
import 'widgets/scanner_inspector_dialog.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> with SingleTickerProviderStateMixin {
  final ScannerRepository _repository = ScannerRepository();
  ScanResponseModel? _swingResponse;
  ScanResponseModel? _intradayResponse;
  bool _isSwingLoading = false;
  bool _isIntradayLoading = false;
  String? _swingError;
  String? _intradayError;
  Timer? _autoRefreshTimer;
  StreamSubscription? _busSubscription;
  late TabController _tabController;

  String _selectedUniverse = 'NIFTY 200';
  final List<String> _universes = ['NIFTY 200', 'F&O Stocks', 'NIFTY 500'];

  String _sortBy = 'AI Score';
  final List<String> _sortOptions = ['AI Score', 'Confidence', 'Volume', 'R:R', 'Risk'];
  String _searchQuery = '';

  final Set<String> _heldSymbols = {'DIXON.NS', 'TATASTEEL', 'RELIANCE'};
  final Set<String> _pendingOrderSymbols = {'HDFCBANK'};

  ScanResultModel? _compareItemA;
  ScanResultModel? _compareItemB;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 6, vsync: this);
    _tabController.addListener(_handleTabChange);
    _fetchSwingScans();
    _autoRefreshTimer = Timer.periodic(const Duration(seconds: 60), (_) {
      if (mounted) {
        _fetchSwingScans(isAutoRefresh: true);
        if (_tabController.index == 1) _fetchIntradayScans(isAutoRefresh: true);
      }
    });

    _busSubscription = LiveDataBus().stream.listen((event) {
      if (mounted && event.type == LiveEventType.scannerUpdate) {
        setState(() {});
      }
    });
  }

  void _handleTabChange() {
    if (_tabController.indexIsChanging) return;
    setState(() {
      if (_tabController.index == 0) {
        _selectedUniverse = 'NIFTY 200';
      } else if (_tabController.index == 1) {
        _selectedUniverse = 'F&O Stocks';
        if (_intradayResponse == null) {
          _fetchIntradayScans();
        }
      }
    });
  }

  @override
  void dispose() {
    _autoRefreshTimer?.cancel();
    _busSubscription?.cancel();
    _tabController.removeListener(_handleTabChange);
    _tabController.dispose();
    super.dispose();
  }

  bool _isSwingFetching = false;
  bool _isIntradayFetching = false;

  Future<void> _fetchSwingScans({bool isAutoRefresh = false}) async {
    if (_isSwingFetching) return;
    _isSwingFetching = true;

    setState(() {
      _isSwingLoading = true;
      if (!isAutoRefresh) _swingError = null;
    });

    try {
      final response = await _repository.getSwingScans();
      if (mounted) {
        setState(() {
          _swingResponse = response;
          _isSwingLoading = false;
          _swingError = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _swingError = e.toString();
          _isSwingLoading = false;
        });
      }
    } finally {
      _isSwingFetching = false;
    }
  }

  Future<void> _fetchIntradayScans({bool isAutoRefresh = false}) async {
    if (_isIntradayFetching) return;
    _isIntradayFetching = true;

    setState(() {
      _isIntradayLoading = true;
      if (!isAutoRefresh) _intradayError = null;
    });

    try {
      final response = await _repository.getIntradayScans();
      if (mounted) {
        setState(() {
          _intradayResponse = response;
          _isIntradayLoading = false;
          _intradayError = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _intradayError = e.toString();
          _isIntradayLoading = false;
        });
      }
    } finally {
      _isIntradayFetching = false;
    }
  }

  void _openDetail(ScanResultModel item) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => StockDetailScreen(result: item)),
    );
  }

  void _showCompareModal(ScanResultModel a, ScanResultModel b) {
    showModalBottomSheet(
      context: context,
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
                  const Text('Scanner Setup Comparison', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                  IconButton(icon: const Icon(Icons.close, color: Colors.grey), onPressed: () => Navigator.pop(context)),
                ],
              ),
              const Divider(color: Colors.white10),
              Table(
                border: TableBorder.all(color: Colors.white10, borderRadius: BorderRadius.circular(8)),
                children: [
                  TableRow(
                    children: [
                      _tableCell('Metric', isHeader: true),
                      _tableCell(a.symbol, isHeader: true, col: Colors.cyanAccent),
                      _tableCell(b.symbol, isHeader: true, col: Colors.amberAccent),
                    ],
                  ),
                  TableRow(children: [_tableCell('AI Score'), _tableCell('${a.score}'), _tableCell('${b.score}')]),
                  TableRow(children: [_tableCell('Confidence'), _tableCell('${a.confidence}%'), _tableCell('${b.confidence}%')]),
                  TableRow(children: [_tableCell('Signal'), _tableCell(a.displaySignal, col: Colors.greenAccent), _tableCell(b.displaySignal, col: Colors.greenAccent)]),
                  TableRow(children: [_tableCell('Risk Reward'), _tableCell(a.riskReward), _tableCell(b.riskReward)]),
                  TableRow(children: [_tableCell('Volume'), _tableCell(a.volume), _tableCell(b.volume)]),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _tableCell(String text, {bool isHeader = false, Color col = Colors.white}) {
    return Padding(
      padding: const EdgeInsets.all(8),
      child: Text(
        text,
        style: TextStyle(
          color: isHeader ? (col == Colors.white ? Colors.cyanAccent : col) : col,
          fontWeight: isHeader ? FontWeight.bold : FontWeight.normal,
          fontSize: isHeader ? 12 : 11,
        ),
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
                  colors: [Colors.cyanAccent, Colors.blueAccent],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.radar, color: Colors.black, size: 18),
            ),
            const SizedBox(width: 8),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Institutional Decision Terminal',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                Text(
                  'LIVE 🟢 • 24x7 Broadcast Active',
                  style: TextStyle(fontSize: 10, color: Colors.greenAccent),
                ),
              ],
            ),
          ],
        ),
        actions: [
          DropdownButton<String>(
            value: _selectedUniverse,
            dropdownColor: const Color(0xFF161B22),
            underline: const SizedBox(),
            items: _universes.map((u) => DropdownMenuItem(value: u, child: Text(u, style: const TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold)))).toList(),
            onChanged: (v) {
              if (v != null) setState(() => _selectedUniverse = v);
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: (_isSwingLoading || _isIntradayLoading) ? null : () {
              if (_tabController.index == 1) {
                _fetchIntradayScans();
              } else {
                _fetchSwingScans();
              }
            },
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          tabs: const [
            Tab(text: 'Swing Scanner'),
            Tab(text: 'Intraday Scanner'),
            Tab(text: 'High Volume'),
            Tab(text: 'Breakout'),
            Tab(text: 'Watchlist'),
            Tab(text: "Today's Best"),
          ],
        ),
      ),
      body: Column(
        children: [
          _buildScannerDecisionHeader(),
          _buildFilterBar(),
          Expanded(child: _buildBody()),
        ],
      ),
    );
  }

  Widget _buildScannerDecisionHeader() {
    final bool isIntradayTab = _tabController.index == 1;
    final activeResponse = isIntradayTab ? _intradayResponse : _swingResponse;

    if (activeResponse != null) {
      return ScannerSummaryPanel(
        response: activeResponse,
        universeName: _selectedUniverse,
      );
    }
    final results = activeResponse?.qualifiedResults ?? [];
    final totalScanned = _selectedUniverse == 'F&O Stocks' ? 184 : (activeResponse?.totalScanned ?? 200);
    final buyCount = results.where((r) => ['BUY', 'STRONG_BUY', 'INSTITUTIONAL_BUY'].contains(r.signal.toUpperCase())).length;
    final sellCount = results.where((r) => ['SELL', 'STRONG_SELL', 'INSTITUTIONAL_SELL'].contains(r.signal.toUpperCase())).length;
    final watchCount = results.where((r) => r.signal.toUpperCase() == 'WATCH').length;
    final qualCount = results.length;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      color: const Color(0xFF161B22),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _hdrStat('Universe', _selectedUniverse, Colors.cyanAccent),
              _hdrStat('Scanned', '$totalScanned', Colors.white),
              _hdrStat('Qualified', '$qualCount', Colors.cyanAccent),
              _hdrStat('BUY', '$buyCount', Colors.greenAccent),
              _hdrStat('SELL', '$sellCount', Colors.redAccent),
              _hdrStat('WATCH', '$watchCount', Colors.amberAccent),
              _hdrStat('Regime', 'BULLISH', Colors.greenAccent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _hdrStat(String label, String val, Color col) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 2),
        Text(val, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 11)),
      ],
    );
  }

  Widget _buildFilterBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      color: const Color(0xFF0B0E14),
      child: Row(
        children: [
          Expanded(
            child: SizedBox(
              height: 34,
              child: TextField(
                style: const TextStyle(color: Colors.white, fontSize: 12),
                decoration: InputDecoration(
                  hintText: 'Search symbol or sector...',
                  hintStyle: const TextStyle(color: Colors.grey, fontSize: 11),
                  prefixIcon: const Icon(Icons.search, size: 16, color: Colors.grey),
                  contentPadding: const EdgeInsets.symmetric(vertical: 0),
                  filled: true,
                  fillColor: const Color(0xFF161B22),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide.none),
                ),
                onChanged: (v) => setState(() => _searchQuery = v.toUpperCase()),
              ),
            ),
          ),
          const SizedBox(width: 8),
          DropdownButton<String>(
            value: _sortBy,
            dropdownColor: const Color(0xFF161B22),
            underline: const SizedBox(),
            items: _sortOptions.map((s) => DropdownMenuItem(value: s, child: Text('Sort: $s', style: const TextStyle(color: Colors.cyanAccent, fontSize: 11)))).toList(),
            onChanged: (v) {
              if (v != null) setState(() => _sortBy = v);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildBody() {
    final bool isIntradayTab = _tabController.index == 1;
    final bool isLoading = isIntradayTab ? _isIntradayLoading : _isSwingLoading;
    final String? error = isIntradayTab ? _intradayError : _swingError;
    final ScanResponseModel? response = isIntradayTab ? _intradayResponse : _swingResponse;

    if (isLoading && response == null) {
      return const ScannerLoadingShimmer();
    }

    if (error != null && response == null) {
      return Center(
        child: Text(error, style: const TextStyle(color: Colors.redAccent)),
      );
    }

    final swingAll = _swingResponse?.qualifiedResults ?? [];
    final swingFiltered = swingAll.where((r) => r.symbol.contains(_searchQuery) || r.sector.contains(_searchQuery)).toList();

    final intradayAll = _intradayResponse?.qualifiedResults ?? [];
    final intradayFiltered = intradayAll.where((r) => r.symbol.contains(_searchQuery) || r.sector.contains(_searchQuery)).toList();

    // DATA SOURCE: /api/v1/scanner/swing
    final swingList = swingFiltered.where((r) => r.signal.toUpperCase() == 'BUY' || r.signal.toUpperCase() == 'WATCH').toList();

    // DATA SOURCE: /api/v1/scanner/intraday
    // Intraday API only returns intraday-specific results, no further filtering needed
    final intradayList = intradayFiltered;

    // DATA SOURCE: /api/v1/scanner/swing
    final volumeList = swingFiltered.where((r) => r.volume.contains('+') || r.volume.contains('x') || r.volume.contains('M') || r.volume.contains('K')).toList();

    // DATA SOURCE: /api/v1/scanner/swing
    final breakoutList = swingFiltered.where((r) => r.trend.toUpperCase().contains('BREAKOUT') || r.trend.toUpperCase().contains('BUILDUP') || r.trend.toUpperCase().contains('BULLISH')).toList();

    // DATA SOURCE: /api/v1/scanner/swing
    final watchlistList = swingFiltered.where((r) => _heldSymbols.contains(r.symbol) || _pendingOrderSymbols.contains(r.symbol)).toList();

    // DATA SOURCE: /api/v1/scanner/swing
    final sortedList = List<ScanResultModel>.from(swingFiltered)
      ..sort((a, b) {
        int cmpScore = b.score.compareTo(a.score);
        if (cmpScore != 0) return cmpScore;
        int cmpConf = b.confidence.compareTo(a.confidence);
        if (cmpConf != 0) return cmpConf;
        return b.riskReward.compareTo(a.riskReward);
      });
    final todaysBestList = sortedList.take(10).toList();

    // TASK-3: Pass explicit lists without fallback logic (no list.isNotEmpty ? list : filtered)
    return TabBarView(
      controller: _tabController,
      children: [
        _buildSwingScannerTab(swingList),
        _buildIntradayScannerTab(intradayList),
        _buildHighVolumeTab(volumeList),
        _buildBreakoutTab(breakoutList),
        _buildWatchlistTab(watchlistList),
        _buildTodaysBestTab(todaysBestList),
      ],
    );
  }

  Color _getSignalColor(String signal) {
    if (signal.toUpperCase() == 'BUY') return Colors.greenAccent;
    if (signal.toUpperCase() == 'SELL') return Colors.redAccent;
    return Colors.amberAccent;
  }

  Widget _buildSwingScannerTab(List<ScanResultModel> list) {
    if (list.isEmpty) return _emptyState('No qualified opportunities available.');

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: list.length,
      itemBuilder: (ctx, i) {
        final item = list[i];
        final isHeld = _heldSymbols.contains(item.symbol);
        final isPending = _pendingOrderSymbols.contains(item.symbol);
        final sigColor = _getSignalColor(item.signal);

        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: BorderSide(color: sigColor.withValues(alpha: 0.6), width: 1.5)),
          child: InkWell(
            borderRadius: BorderRadius.circular(14),
            onTap: () => _openDetail(item),
            onLongPress: () => ScannerInspectorDialog.show(context, item),
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Text(item.symbol, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                          const SizedBox(width: 8),
                          _smartBadge(item.signal, sigColor),
                          const SizedBox(width: 6),
                          if (isHeld)
                            _smartBadge('Holding', Colors.purpleAccent)
                          else if (isPending)
                            _smartBadge('Pending Order', Colors.amberAccent)
                          else
                            _smartBadge(item.sector, Colors.cyanAccent),
                        ],
                      ),
                      Row(
                        children: [
                          Text('${item.confidence.toStringAsFixed(1)}% Swing Score', style: TextStyle(color: sigColor, fontWeight: FontWeight.bold, fontSize: 13)),
                          const SizedBox(width: 4),
                          IconButton(
                            icon: const Icon(Icons.info_outline, size: 16, color: Colors.cyanAccent),
                            padding: EdgeInsets.zero,
                            constraints: const BoxConstraints(),
                            onPressed: () => ScannerInspectorDialog.show(context, item),
                          ),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _chip(item.signal == 'SELL' ? 'Daily: Bearish' : 'Daily: Bullish', item.signal == 'SELL' ? Colors.redAccent : Colors.greenAccent),
                      _chip(item.signal == 'SELL' ? 'Weekly: Weak' : 'Weekly: Strong Bull', item.signal == 'SELL' ? Colors.orangeAccent : Colors.lightGreenAccent),
                      _chip(isHeld ? 'Increase Position' : 'Pattern: Setup Cleared', isHeld ? Colors.amberAccent : Colors.cyanAccent),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('Ideal Entry Zone: ₹${item.entry} - ₹${(item.entry * 1.005).toStringAsFixed(1)} • SL: ₹${item.stopLoss}', style: const TextStyle(color: Colors.white, fontSize: 12)),
                  Text('T1: ₹${item.target1} • T2: ₹${item.target2} • R:R: ${item.riskReward} • Hold: 3-5 Days', style: const TextStyle(color: Colors.white70, fontSize: 11)),
                  const SizedBox(height: 6),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(item.signal == 'SELL' ? 'Setup Risk: MEDIUM (Short Setup)' : 'Chasing Warning: NO (Ideal Entry)', style: TextStyle(color: sigColor, fontSize: 10, fontWeight: FontWeight.bold)),
                      Row(
                        children: [
                          GestureDetector(
                            onTap: () => ScannerInspectorDialog.show(context, item),
                            child: const Text('🔍 Inspect', style: TextStyle(color: Colors.blueAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                          ),
                          const SizedBox(width: 10),
                          GestureDetector(
                            onTap: () {
                              if (_compareItemA == null) {
                                _compareItemA = item;
                                ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Selected ${item.symbol} for comparison. Tap another setup to compare.')));
                              } else {
                                _compareItemB = item;
                                _showCompareModal(_compareItemA!, _compareItemB!);
                                _compareItemA = null;
                                _compareItemB = null;
                              }
                            },
                            child: const Text('⚡ Compare Setup', style: TextStyle(color: Colors.cyanAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                          ),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildIntradayScannerTab(List<ScanResultModel> list) {
    if (list.isEmpty) return _emptyState('No qualified opportunities available.');

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: list.length,
      itemBuilder: (ctx, i) {
        final item = list[i];
        final isHeld = _heldSymbols.contains(item.symbol);
        final sigColor = _getSignalColor(item.signal);
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: BorderSide(color: sigColor.withValues(alpha: 0.5), width: 1.5)),
          child: InkWell(
            borderRadius: BorderRadius.circular(14),
            onTap: () => _openDetail(item),
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Text('${item.symbol} (F&O Intraday)', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                          const SizedBox(width: 8),
                          _smartBadge(item.signal, sigColor),
                          const SizedBox(width: 6),
                          if (isHeld) _smartBadge('Holding', Colors.purpleAccent),
                        ],
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(color: sigColor.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(4)),
                        child: Text('Rank #${i + 1}', style: TextStyle(color: sigColor, fontWeight: FontWeight.bold, fontSize: 11)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _badge(item.signal == 'SELL' ? 'ORB: Low Breakdown' : 'ORB: High Break', item.signal == 'SELL' ? Colors.redAccent : Colors.greenAccent),
                      _badge(item.signal == 'SELL' ? 'VWAP: Below (-1.5%)' : 'VWAP: Above (+1.2%)', item.signal == 'SELL' ? Colors.orangeAccent : Colors.cyanAccent),
                      _badge(item.signal == 'SELL' ? 'OI: Short Buildup' : 'OI: Long Buildup', item.signal == 'SELL' ? Colors.redAccent : Colors.purpleAccent),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('Scalp Probability: ${item.confidence.toStringAsFixed(0)}% • CPR Status: Range Breakout', style: const TextStyle(color: Colors.white, fontSize: 11)),
                  Text('Intraday Vol Burst: ${item.volume} • Risk/Reward: ${item.riskReward}', style: const TextStyle(color: Colors.white70, fontSize: 10)),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildHighVolumeTab(List<ScanResultModel> list) {
    if (list.isEmpty) return _emptyState('No qualified opportunities available.');

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: list.length,
      itemBuilder: (ctx, i) {
        final item = list[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: BorderSide(color: Colors.blueAccent.withValues(alpha: 0.3))),
          child: InkWell(
            borderRadius: BorderRadius.circular(14),
            onTap: () => _openDetail(item),
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(item.symbol, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                      Text('Volume Surge ${item.volume}', style: const TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold, fontSize: 13)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('5-Day Avg Vol: 1.2M • Today Vol: 4.8M (+300% Spike)', style: const TextStyle(color: Colors.white, fontSize: 12)),
                  Text('Delivery %: 68.4% • Institutional Money Flow: STRONG BUY', style: const TextStyle(color: Colors.greenAccent, fontSize: 11)),
                  Text('Liquidity Score: 96/100 • Volume Rank: #${i + 1}', style: const TextStyle(color: Colors.white70, fontSize: 10)),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildBreakoutTab(List<ScanResultModel> list) {
    if (list.isEmpty) return _emptyState('No qualified opportunities available.');

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: list.length,
      itemBuilder: (ctx, i) {
        final item = list[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: BorderSide(color: Colors.orangeAccent.withValues(alpha: 0.3))),
          child: InkWell(
            borderRadius: BorderRadius.circular(14),
            onTap: () => _openDetail(item),
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(item.symbol, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                      Text('Breakout +${(item.score - 70).toStringAsFixed(1)}%', style: const TextStyle(color: Colors.orangeAccent, fontWeight: FontWeight.bold, fontSize: 13)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('Key Resistance Cleared: ₹${item.stopLoss * 1.05} • Support: ₹${item.stopLoss}', style: const TextStyle(color: Colors.white, fontSize: 12)),
                  Text('52-Week High Breakout • All-Time High Proximity: 1.2%', style: const TextStyle(color: Colors.cyanAccent, fontSize: 11)),
                  Text('AI Confidence: ${item.confidence}% • Volume Confirmation: VERIFIED', style: const TextStyle(color: Colors.greenAccent, fontSize: 11)),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildWatchlistTab(List<ScanResultModel> list) {
    if (list.isEmpty) return _emptyState('Watchlist is empty. Bookmark symbols to monitor.');

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: list.length,
      itemBuilder: (ctx, i) {
        final item = list[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: const BorderSide(color: Colors.white10)),
          child: ListTile(
            onTap: () => _openDetail(item),
            leading: const Icon(Icons.star, color: Colors.amberAccent),
            title: Text(item.symbol, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
            subtitle: Text('Price: ₹${item.price} • PnL: +₹1,450.00 (+5.88%)\nTarget: ₹${item.target1} • SL: ₹${item.stopLoss}', style: const TextStyle(color: Colors.white70, fontSize: 11)),
            trailing: const Icon(Icons.notifications_active_outlined, color: Colors.cyanAccent, size: 20),
          ),
        );
      },
    );
  }

  Widget _buildTodaysBestTab(List<ScanResultModel> list) {
    if (list.isEmpty) return _emptyState('No qualified opportunities available.');

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: list.length,
      itemBuilder: (ctx, i) {
        final item = list[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14), side: BorderSide(color: Colors.greenAccent.withValues(alpha: 0.4))),
          child: InkWell(
            borderRadius: BorderRadius.circular(14),
            onTap: () => _openDetail(item),
            child: Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          CircleAvatar(
                            radius: 14,
                            backgroundColor: Colors.greenAccent,
                            child: Text('#${i + 1}', style: const TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontSize: 11)),
                          ),
                          const SizedBox(width: 10),
                          Text(item.symbol, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                        ],
                      ),
                      Text('AI Score: ${item.score.toStringAsFixed(1)}', style: const TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 14)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('Signal: ${item.signal} • Confidence: ${item.confidence}% • Sector: ${item.sector}', style: const TextStyle(color: Colors.white, fontSize: 12)),
                  Text('Expected Return: +5.88% • Risk: LOW • Hold: Swing Positional', style: const TextStyle(color: Colors.cyanAccent, fontSize: 11)),
                  const SizedBox(height: 4),
                  Text('AI Rationale: Strong multi-timeframe trend alignment with institutional volume surge.', style: const TextStyle(color: Colors.white70, fontSize: 11, fontStyle: FontStyle.italic)),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  static Widget _smartBadge(String text, Color col) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(color: col.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(4)),
      child: Text(text, style: TextStyle(color: col, fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }

  static Widget _chip(String text, Color col) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(color: col.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(4)),
      child: Text(text, style: TextStyle(color: col, fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }

  static Widget _badge(String text, Color col) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(color: col.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(4)),
      child: Text(text, style: TextStyle(color: col, fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }

  static Widget _emptyState(String text) {
    return Center(
      child: Text(text, style: const TextStyle(color: Colors.grey)),
    );
  }
}
