import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../core/network/api_config.dart';
import '../../core/network/network_manager.dart';
import '../models/dashboard_data_model.dart';
import '../models/scan_result_model.dart';
import 'scanner_repository.dart';

class DashboardRepository {
  final ScannerRepository _scannerRepository;

  DashboardRepository({ScannerRepository? scannerRepository})
    : _scannerRepository = scannerRepository ?? ScannerRepository();

  Future<String> checkServerHealth() async {
    final isHealthy = await NetworkManager.instance.checkServerHealth();
    if (isHealthy) return 'ONLINE';
    for (int attempt = 1; attempt <= 2; attempt++) {
      try {
        final response = await http
            .get(
              Uri.parse('${ApiConfig.baseUrl}/health'),
              headers: ApiConfig.defaultHeaders(),
            )
            .timeout(const Duration(seconds: ApiConfig.healthTimeoutSeconds));

        if (response.statusCode == 200) {
          return 'ONLINE';
        }
      } catch (_) {
        if (attempt == 1) {
          await ApiConfig.autoDiscoverReachableServer();
        }
      }
    }
    return 'OFFLINE';
  }

  String getMarketStatus() {
    final nmStatus = NetworkManager.instance.marketStatus;
    if (nmStatus.isNotEmpty && nmStatus != 'UNKNOWN') {
      return nmStatus;
    }
    final now = DateTime.now();
    final ist = now.toUtc().add(const Duration(hours: 5, minutes: 30));

    if (ist.weekday == DateTime.saturday || ist.weekday == DateTime.sunday) {
      return 'CLOSED (Weekend)';
    }

    final timeInMinutes = ist.hour * 60 + ist.minute;
    final preOpenStart = 9 * 60; // 09:00 IST
    final marketOpen = 9 * 60 + 15; // 09:15 IST
    final marketClose = 15 * 60 + 30; // 15:30 IST

    if (timeInMinutes >= preOpenStart && timeInMinutes < marketOpen) {
      return 'PRE-OPEN';
    } else if (timeInMinutes >= marketOpen && timeInMinutes < marketClose) {
      return 'OPEN';
    } else {
      return 'CLOSED';
    }
  }

  Future<DashboardDataModel> getDashboardData() async {
    final serverStatus = await checkServerHealth();
    String marketStatus = getMarketStatus();

    String lastScanTime = 'UNAVAILABLE';
    String cacheAgeDisplay = 'UNAVAILABLE';
    bool isStale = true;
    String provider = NetworkManager.instance.provider;
    String providerHealth = NetworkManager.instance.providerHealth;
    bool fallbackUsed = NetworkManager.instance.fallbackUsed;
    bool paytmAuthenticated = NetworkManager.instance.paytmAuthenticated;
    String brokerStatusLabel = paytmAuthenticated
        ? 'Broker: Paytm Money (Authenticated)'
        : 'Broker: Paytm Unauthenticated (Fallback Active)';
    String actualBrokerFundsLabel = paytmAuthenticated
        ? 'UNAVAILABLE (Live Funds Endpoint Not Queried)'
        : 'UNAVAILABLE (Paytm 401 Unauthenticated)';
    String virtualRiskCapitalLabel = 'UNAVAILABLE';
    String paperEquityLabel = 'UNAVAILABLE';
    String paperAvailableCashLabel = 'UNAVAILABLE';
    String paperUsedMarginLabel = 'UNAVAILABLE';
    String paperPnlLabel = 'UNAVAILABLE';
    String paperOpenPositionsLabel = 'UNAVAILABLE';

    int totalScanned = 0;
    int qualifiedSignals = 0;
    String marketQuality = 'UNAVAILABLE';
    bool isOnline = serverStatus == 'ONLINE';
    List<ScanResultModel> qualifiedResults = const [];
    ScanResultModel? topPick;

    if (isOnline) {
      try {
        final scanResponse = await _scannerRepository.getSwingScans();
        totalScanned = scanResponse.totalScanned;
        qualifiedResults = scanResponse.qualifiedResults;
        qualifiedSignals = qualifiedResults.length;
        marketQuality = scanResponse.marketQuality;
        lastScanTime = scanResponse.timestamp;
        cacheAgeDisplay = scanResponse.formattedCacheAge;
        isStale = scanResponse.isStale;
        provider = scanResponse.provider;
        providerHealth = scanResponse.providerHealth;
        fallbackUsed = scanResponse.fallbackUsed;
        paytmAuthenticated = scanResponse.paytmAuthenticated;
        if (scanResponse.marketStatus.isNotEmpty && scanResponse.marketStatus != 'UNKNOWN') {
          marketStatus = scanResponse.marketStatus;
        }
        brokerStatusLabel = paytmAuthenticated
            ? 'Broker: Paytm Money (Authenticated)'
            : 'Broker: Paytm Unauthenticated (Yahoo Fallback)';
        actualBrokerFundsLabel = paytmAuthenticated
            ? 'UNAVAILABLE (Check Paytm Live Funds)'
            : 'UNAVAILABLE (Paytm 401 Unauth)';

        final buyCandidates = qualifiedResults.where((r) {
          final sig = r.signal.toUpperCase();
          return sig == 'BUY' || sig == 'STRONG_BUY' || sig == 'INSTITUTIONAL_BUY';
        }).toList()
          ..sort((a, b) => b.score.compareTo(a.score));
        if (buyCandidates.isNotEmpty) {
          topPick = buyCandidates.first;
        }
      } catch (e) {
        lastScanTime = 'Scan Error';
        marketQuality = 'ERROR';
      }

      // Fetch Virtual Risk Capital separately from Actual Broker Funds
      try {
        final riskResp = await http
            .get(
              Uri.parse('${NetworkManager.instance.baseUrl}/risk/report'),
              headers: NetworkManager.instance.defaultHeaders(),
            )
            .timeout(const Duration(seconds: 6));
        if (riskResp.statusCode == 200) {
          final rData = json.decode(riskResp.body) as Map<String, dynamic>;
          final report = rData['report'] as Map<String, dynamic>? ?? rData;
          final cap = (report['capital'] as num?)?.toDouble();
          if (cap != null) {
            virtualRiskCapitalLabel = '₹${cap.toStringAsFixed(0)} (Virtual)';
          }
        }
      } catch (_) {}

      // Fetch Paper Trading Account separately from Actual Broker Funds
      try {
        final paperResp = await http
            .get(
              Uri.parse('${NetworkManager.instance.baseUrl}/paper-trading/account'),
              headers: NetworkManager.instance.defaultHeaders(),
            )
            .timeout(const Duration(seconds: 6));
        if (paperResp.statusCode == 200) {
          final pData = json.decode(paperResp.body) as Map<String, dynamic>;
          final eq = (pData['current_portfolio_value'] as num?)?.toDouble();
          final avail = (pData['available_balance'] as num?)?.toDouble();
          final inv = (pData['invested_amount'] as num?)?.toDouble();
          final pnl = (pData['total_pnl'] as num?)?.toDouble();
          final retPct = (pData['return_pct'] as num?)?.toDouble();
          final openCnt = (pData['open_positions_count'] as num?)?.toInt();

          if (eq != null) paperEquityLabel = '₹${eq.toStringAsFixed(2)} (Paper)';
          if (avail != null) paperAvailableCashLabel = '₹${avail.toStringAsFixed(2)}';
          if (inv != null) paperUsedMarginLabel = '₹${inv.toStringAsFixed(2)}';
          if (pnl != null && retPct != null) {
            final sign = pnl >= 0 ? '+' : '';
            paperPnlLabel = '$sign₹${pnl.toStringAsFixed(2)} ($sign${retPct.toStringAsFixed(2)}%)';
          }
          if (openCnt != null) paperOpenPositionsLabel = '$openCnt Paper';
        }
      } catch (_) {}
    } else {
      lastScanTime = 'Server Unreachable';
      marketQuality = 'OFFLINE';
    }

    return DashboardDataModel(
      serverStatus: serverStatus,
      marketStatus: marketStatus,
      lastScanTime: lastScanTime,
      cacheAgeDisplay: cacheAgeDisplay,
      isStale: isStale,
      provider: provider,
      providerHealth: providerHealth,
      fallbackUsed: fallbackUsed,
      paytmAuthenticated: paytmAuthenticated,
      brokerStatusLabel: brokerStatusLabel,
      actualBrokerFundsLabel: actualBrokerFundsLabel,
      virtualRiskCapitalLabel: virtualRiskCapitalLabel,
      paperEquityLabel: paperEquityLabel,
      paperAvailableCashLabel: paperAvailableCashLabel,
      paperUsedMarginLabel: paperUsedMarginLabel,
      paperPnlLabel: paperPnlLabel,
      paperOpenPositionsLabel: paperOpenPositionsLabel,
      totalScanned: totalScanned,
      qualifiedSignals: qualifiedSignals,
      marketQuality: marketQuality,
      isOnline: isOnline,
      qualifiedResults: qualifiedResults,
      topPick: topPick,
    );
  }
}
