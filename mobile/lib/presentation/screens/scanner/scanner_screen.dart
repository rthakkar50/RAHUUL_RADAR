import 'package:flutter/material.dart';
import '../../../data/models/scan_response_model.dart';
import '../../../data/repositories/scanner_repository.dart';
import '../../widgets/scanner_result_card.dart';

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

  @override
  void initState() {
    super.initState();
    _fetchScans();
  }

  Future<void> _fetchScans() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final response = await _repository.getSwingScans();
      setState(() {
        _response = response;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Swing Scanner'),
        actions: [
          if (_response != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Center(
                child: Text(
                  '${_response!.execTime.toStringAsFixed(2)}s',
                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ),
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _fetchScans,
        child: _buildBody(),
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _response == null) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Executing Live AI Scanner...'),
          ],
        ),
      );
    }

    if (_error != null && _response == null) {
      return Center(
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.cloud_off, color: Colors.orangeAccent, size: 60),
                const SizedBox(height: 16),
                Text('API Unavailable', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 8),
                Text(_error!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.grey)),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: _fetchScans,
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
      return const Center(child: Text('No data'));
    }

    return Column(
      children: [
        _buildSummaryBar(),
        Expanded(
          child: _response!.qualifiedResults.isEmpty
              ? ListView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  children: const [
                    SizedBox(height: 100),
                    Center(child: Text('No trades matched quality gates.', style: TextStyle(color: Colors.grey))),
                  ],
                )
              : ListView.builder(
                  physics: const AlwaysScrollableScrollPhysics(),
                  itemCount: _response!.qualifiedResults.length,
                  itemBuilder: (context, index) {
                    return ScannerResultCard(result: _response!.qualifiedResults[index]);
                  },
                ),
        ),
      ],
    );
  }

  Widget _buildSummaryBar() {
    return Container(
      padding: const EdgeInsets.all(12),
      color: Theme.of(context).cardColor,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildSummaryItem('Scanned', '${_response!.totalScanned}'),
          _buildSummaryItem('Qualified', '${_response!.qualifiedResults.length}'),
          _buildSummaryItem('Market', _response!.marketQuality),
        ],
      ),
    );
  }

  Widget _buildSummaryItem(String label, String value) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 10, color: Colors.grey)),
        const SizedBox(height: 2),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
      ],
    );
  }
}
