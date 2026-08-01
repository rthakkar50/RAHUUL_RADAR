import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mobile/core/network/api_config.dart';
import 'package:mobile/data/repositories/scanner_repository.dart';
import 'package:mobile/data/repositories/portfolio_repository.dart';
import 'package:mobile/data/repositories/journal_repository.dart';
import 'package:mobile/data/repositories/dashboard_repository.dart';

class RealNetworkHttpOverrides extends HttpOverrides {}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  HttpOverrides.global = RealNetworkHttpOverrides();

  setUpAll(() async {
    SharedPreferences.setMockInitialValues({});
    await ApiConfig.init();
    debugPrint('[RUN-AUDIT] Initialized ApiConfig. Active Base URL: ${ApiConfig.baseUrl}');
  });

  test('REAL RUNTIME NETWORK TEST: Repositories with Production Headers', () async {
    debugPrint('\n=== START REAL NETWORK TEST: Repositories ===');
    
    // 1. Dashboard Health Check
    final dashboardRepo = DashboardRepository();
    final healthStatus = await dashboardRepo.checkServerHealth();
    debugPrint('[RUN-AUDIT] Dashboard Health Check Result: $healthStatus');
    expect(healthStatus, equals('ONLINE'));

    // 2. Scanner Repository
    final scannerRepo = ScannerRepository();
    final scanData = await scannerRepo.getSwingScans();
    debugPrint('[RUN-AUDIT] Scanner Repository Result: Total Scanned=${scanData.totalScanned}, Qualified=${scanData.qualifiedResults.length}');
    expect(scanData.qualifiedResults.isNotEmpty, isTrue);

    // 3. Portfolio Repository
    final portfolioRepo = PortfolioRepository();
    final portfolioData = await portfolioRepo.getPortfolio();
    debugPrint('[RUN-AUDIT] Portfolio Repository Result: Total Capital=${portfolioData.summary.totalCapital}, Open Positions=${portfolioData.openPositions.length}');
    expect(portfolioData.summary.totalCapital, greaterThan(0));

    // 4. Journal Repository
    final journalRepo = JournalRepository();
    final journalData = await journalRepo.getJournal();
    debugPrint('[RUN-AUDIT] Journal Repository Result: Total Trades=${journalData.trades.length}, Win Rate=${journalData.analytics.winRate}%');
    expect(journalData.trades.isNotEmpty, isTrue);

    debugPrint('=== END REAL NETWORK TEST: Repositories ===\n');
  });
}
