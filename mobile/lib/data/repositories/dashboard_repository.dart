import 'package:http/http.dart' as http;
import '../../core/network/api_config.dart';
import '../models/dashboard_data_model.dart';
import 'scanner_repository.dart';

class DashboardRepository {
  final ScannerRepository _scannerRepository;

  DashboardRepository({ScannerRepository? scannerRepository})
      : _scannerRepository = scannerRepository ?? ScannerRepository();

  Future<String> checkServerHealth() async {
    for (int attempt = 1; attempt <= 3; attempt++) {
      try {
        final response = await http.get(
          Uri.parse('${ApiConfig.baseUrl}/health'),
          headers: ApiConfig.defaultHeaders(),
        ).timeout(const Duration(seconds: ApiConfig.healthTimeoutSeconds));
        
        if (response.statusCode == 200) {
          return 'ONLINE';
        }
      } catch (_) {
        if (attempt == 1) {
          await ApiConfig.autoDiscoverReachableServer();
        } else if (attempt < 3) {
          await Future.delayed(const Duration(milliseconds: 500));
        }
      }
    }
    return 'OFFLINE';
  }

  String getMarketStatus() {
    final now = DateTime.now();
    // Convert current UTC timestamp to Indian Standard Time (UTC+5:30)
    final ist = now.toUtc().add(const Duration(hours: 5, minutes: 30));
    
    if (ist.weekday == DateTime.saturday || ist.weekday == DateTime.sunday) {
      return '🔴 CLOSED (Weekend)';
    }
    
    final timeInMinutes = ist.hour * 60 + ist.minute;
    final preOpenStart = 9 * 60; // 09:00 IST
    final marketOpen = 9 * 60 + 15; // 09:15 IST
    final marketClose = 15 * 60 + 30; // 15:30 IST
    
    if (timeInMinutes >= preOpenStart && timeInMinutes < marketOpen) {
      return '🟡 PRE-OPEN';
    } else if (timeInMinutes >= marketOpen && timeInMinutes < marketClose) {
      return '🟢 OPEN';
    } else {
      return '🔴 CLOSED';
    }
  }

  Future<DashboardDataModel> getDashboardData() async {
    final serverStatus = await checkServerHealth();
    final marketStatus = getMarketStatus();
    
    String lastScanTime = 'Never';
    int totalScanned = 0;
    int qualifiedSignals = 0;
    String marketQuality = 'N/A';
    bool isOnline = serverStatus == 'ONLINE';
    
    if (isOnline) {
      try {
        // Re-use ScannerRepository without duplicating API fetching or model parsing logic
        final scanResponse = await _scannerRepository.getSwingScans();
        totalScanned = scanResponse.totalScanned;
        qualifiedSignals = scanResponse.qualifiedResults.length;
        marketQuality = scanResponse.marketQuality;
        
        final now = DateTime.now();
        lastScanTime = '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}:${now.second.toString().padLeft(2, '0')}';
      } catch (e) {
        lastScanTime = 'Scan Error';
        marketQuality = 'ERROR';
      }
    } else {
      lastScanTime = 'Server Unreachable';
      marketQuality = 'OFFLINE';
    }

    return DashboardDataModel(
      serverStatus: serverStatus,
      marketStatus: marketStatus,
      lastScanTime: lastScanTime,
      totalScanned: totalScanned,
      qualifiedSignals: qualifiedSignals,
      marketQuality: marketQuality,
      isOnline: isOnline,
    );
  }
}
