import 'dart:async';
import 'package:flutter/material.dart';
import '../../../data/models/scan_response_model.dart';
import '../../../data/models/scan_result_model.dart';
import '../../../data/repositories/scanner_repository.dart';
import '../../widgets/scanner_loading_shimmer.dart';
import '../../widgets/scanner_result_card.dart';

enum ScannerFilter { all, buy, sell, watch, highConfidence, highScore }

enum ScannerSort { scoreDesc, confidenceDesc, rrDesc, symbolAsc }

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  final ScannerRepository _repository = ScannerRepository();
  ScanResponseModel? _response;
  bool _isLoading = false;
  String? _error;
  DateTime? _lastRefreshTime;
  Timer? _autoRefreshTimer;

  // Search & Filter local state
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';
  ScannerFilter _selectedFilter = ScannerFilter.all;
  final ScannerSort _selectedSort = ScannerSort.scoreDesc;
  final String _selectedSector = 'ALL';

  @override
  void initState() {
    super.initState();
    _fetchScans();
    // Auto refresh every 60 seconds (Task 1)
    _autoRefreshTimer = Timer.periodic(const Duration(seconds: 60), (_) {
      if (mounted) _fetchScans(isAutoRefresh: true);
    });
  }

  @override
  void dispose() {
    _autoRefreshTimer?.cancel();
    _searchController.dispose();
    super.dispose();
  }

  bool _isFetching = false;

  Future<void> _fetchScans({bool isAutoRefresh = false}) async {
    if (_isFetching) return;
    _isFetching = true;

    debugPrint(
      '[RUN-AUDIT] [ScannerScreen] [STATE TRANSITION] -> LOADING (isAutoRefresh: $isAutoRefresh)',
    );
    setState(() {
      _isLoading = true;
      if (!isAutoRefresh) _error = null;
    });

    try {
      final response = await _repository.getSwingScans();
      debugPrint(
        '[RUN-AUDIT] [ScannerScreen] Repository returned SUCCESS. Qualified count: ${response.qualifiedResults.length}',
      );
      if (mounted) {
        debugPrint('[RUN-AUDIT] [ScannerScreen] [STATE TRANSITION] -> SUCCESS');
        setState(() {
          _response = response;
          _lastRefreshTime = DateTime.now();
          _isLoading = false;
          _error = null;
        });
      }
    } catch (e, st) {
      debugPrint('[RUN-AUDIT] [ScannerScreen] Repository THREW EXCEPTION: $e');
      debugPrint('[RUN-AUDIT] [ScannerScreen] STACKTRACE:\n$st');
      if (mounted) {
        debugPrint(
          '[RUN-AUDIT] [ScannerScreen] [STATE TRANSITION] -> ERROR (error: $e)',
        );
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    } finally {
      _isFetching = false;
    }
  }

  List<ScanResultModel> _getFilteredResults() {
    if (_response == null) return [];

    final query = _searchQuery.trim().toLowerCase();

    final list = _response!.qualifiedResults.where((item) {
      // 1. Filter Chip Matching
      bool matchesFilter = true;
      switch (_selectedFilter) {
        case ScannerFilter.buy:
          matchesFilter = item.signal.toUpperCase().contains('BUY');
          break;
        case ScannerFilter.sell:
          matchesFilter = item.signal.toUpperCase().contains('SELL');
          break;
        case ScannerFilter.watch:
          matchesFilter =
              item.signal.toUpperCase().contains('WATCH') ||
              item.signal.toUpperCase().contains('HOLD') ||
              item.signal.toUpperCase().contains('NEUTRAL') ||
              item.confidence >= 70.0;
          break;
        case ScannerFilter.highConfidence:
          matchesFilter = item.confidence >= 70.0;
          break;
        case ScannerFilter.highScore:
          matchesFilter = item.score >= 70.0;
          break;
        case ScannerFilter.all:
          matchesFilter = true;
          break;
      }

      if (!matchesFilter) return false;

      // 2. Sector Filter
      if (_selectedSector != 'ALL' &&
          item.sector.toUpperCase() != _selectedSector) {
        return false;
      }

      // 3. Search Query Matching
      if (query.isEmpty) return true;

      final symbolMatch = item.symbol.toLowerCase().contains(query);
      final companyMatch = item.company.toLowerCase().contains(query);
      final sectorMatch = item.sector.toLowerCase().contains(query);

      return symbolMatch || companyMatch || sectorMatch;
    }).toList();

    // Sort Results
    list.sort((a, b) {
      switch (_selectedSort) {
        case ScannerSort.scoreDesc:
          return b.score.compareTo(a.score);
        case ScannerSort.confidenceDesc:
          return b.confidence.compareTo(a.confidence);
        case ScannerSort.rrDesc:
          return b.riskReward.compareTo(a.riskReward);
        case ScannerSort.symbolAsc:
          return a.symbol.compareTo(b.symbol);
      }
    });

    return list;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Live AI Scanner'),
        actions: [
          _buildLiveStatusIndicator(),
          if (_response != null)
            Padding(
              padding: const EdgeInsets.only(right: 16.0, left: 8.0),
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.blueAccent.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    '${_response!.execTime.toStringAsFixed(2)}s',
                    style: const TextStyle(
                      color: Colors.blueAccent,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => _fetchScans(isAutoRefresh: false),
        child: Column(
          children: [
            _buildSearchBar(),
            _buildFilterChips(),
            if (_isLoading && _response != null)
              const LinearProgressIndicator(
                minHeight: 2.5,
                color: Colors.blueAccent,
              ),
            Expanded(child: _buildBody()),
          ],
        ),
      ),
    );
  }

  Widget _buildLiveStatusIndicator() {
    final isScanning = _isLoading;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: isScanning
            ? Colors.orangeAccent.withValues(alpha: 0.2)
            : Colors.greenAccent.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isScanning ? Colors.orangeAccent : Colors.greenAccent,
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 7,
            height: 7,
            decoration: BoxDecoration(
              color: isScanning ? Colors.orangeAccent : Colors.greenAccent,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 5),
          Text(
            isScanning ? 'SCANNING' : 'LIVE',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              color: isScanning ? Colors.orangeAccent : Colors.greenAccent,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
      child: TextField(
        controller: _searchController,
        onChanged: (val) => setState(() => _searchQuery = val),
        decoration: InputDecoration(
          hintText: 'Search by Symbol or Company...',
          prefixIcon: const Icon(Icons.search, size: 20),
          suffixIcon: _searchQuery.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear, size: 18),
                  onPressed: () {
                    _searchController.clear();
                    setState(() => _searchQuery = '');
                  },
                )
              : null,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 12,
          ),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
          filled: true,
          fillColor: Theme.of(context).cardColor,
        ),
      ),
    );
  }

  Widget _buildFilterChips() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: Row(
        children: [
          _buildChip('ALL', ScannerFilter.all),
          _buildChip('BUY', ScannerFilter.buy),
          _buildChip('SELL', ScannerFilter.sell),
          _buildChip('WATCH', ScannerFilter.watch),
          _buildChip('HIGH CONFIDENCE', ScannerFilter.highConfidence),
          _buildChip('HIGH SCORE', ScannerFilter.highScore),
        ],
      ),
    );
  }

  Widget _buildChip(String label, ScannerFilter filter) {
    final isSelected = _selectedFilter == filter;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4.0),
      child: ChoiceChip(
        label: Text(
          label,
          style: TextStyle(
            fontSize: 11,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            color: isSelected ? Colors.white : Colors.grey,
          ),
        ),
        selected: isSelected,
        selectedColor: Colors.blueAccent,
        backgroundColor: Theme.of(context).cardColor,
        onSelected: (selected) {
          if (selected) {
            setState(() => _selectedFilter = filter);
          }
        },
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _response == null) {
      return const ScannerLoadingShimmer();
    }

    if (_error != null && _response == null) {
      debugPrint(
        '[RUN-AUDIT] [ScannerScreen] RENDERING ERROR WIDGET "API Unavailable". Current _error value: "$_error"',
      );
      return Center(
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.cloud_off,
                  color: Colors.orangeAccent,
                  size: 60,
                ),
                const SizedBox(height: 16),
                Text(
                  'API Unavailable',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 8),
                Text(
                  _error!,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.grey),
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () => _fetchScans(isAutoRefresh: false),
                  icon: const Icon(Icons.refresh),
                  label: const Text('Retry'),
                ),
              ],
            ),
          ),
        ),
      );
    }

    if (_response == null) {
      return const Center(child: Text('No scanner data available.'));
    }

    final filteredList = _getFilteredResults();

    return Column(
      children: [
        _buildSummaryBar(),
        Expanded(
          child: filteredList.isEmpty
              ? _buildEmptyState()
              : ListView.builder(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.only(bottom: 16),
                  itemCount: filteredList.length,
                  itemBuilder: (context, index) {
                    return ScannerResultCard(
                      key: ValueKey(filteredList[index].symbol),
                      result: filteredList[index],
                    );
                  },
                ),
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      children: [
        const SizedBox(height: 60),
        Center(
          child: Column(
            children: [
              const Icon(Icons.search_off, size: 48, color: Colors.grey),
              const SizedBox(height: 12),
              Text(
                _searchQuery.isNotEmpty
                    ? 'No matching stocks found for "$_searchQuery"'
                    : 'No signals match the selected filter.',
                style: const TextStyle(color: Colors.grey, fontSize: 14),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              if (_selectedFilter != ScannerFilter.all ||
                  _searchQuery.isNotEmpty)
                TextButton.icon(
                  onPressed: () {
                    _searchController.clear();
                    setState(() {
                      _searchQuery = '';
                      _selectedFilter = ScannerFilter.all;
                    });
                  },
                  icon: const Icon(Icons.filter_alt_off),
                  label: const Text('Reset Filters & Search'),
                ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      color: Theme.of(context).cardColor,
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildSummaryItem('Scanned', '${_response!.totalScanned}'),
              _buildSummaryItem(
                'Qualified',
                '${_response!.qualifiedResults.length}',
              ),
              _buildSummaryItem('Market Quality', _response!.marketQuality),
            ],
          ),
          if (_lastRefreshTime != null) ...[
            const SizedBox(height: 6),
            const Divider(height: 1, color: Colors.white12),
            const SizedBox(height: 6),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.update, size: 12, color: Colors.blueAccent),
                const SizedBox(width: 4),
                Text(
                  'Last refreshed: ${_lastRefreshTime!.hour.toString().padLeft(2, '0')}:${_lastRefreshTime!.minute.toString().padLeft(2, '0')}:${_lastRefreshTime!.second.toString().padLeft(2, '0')} (Auto-refreshes every 60s)',
                  style: const TextStyle(fontSize: 11, color: Colors.grey),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSummaryItem(String label, String value) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 10, color: Colors.grey)),
        const SizedBox(height: 2),
        Text(
          value,
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
        ),
      ],
    );
  }
}
