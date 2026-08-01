import 'package:flutter/material.dart';
import '../../core/network/api_config.dart';
import '../screens/dashboard/dashboard_screen.dart';
import '../screens/market/market_intelligence_screen.dart';
import '../screens/macro/global_macro_screen.dart';
import '../screens/news/ai_news_screen.dart';
import '../screens/scanner/scanner_screen.dart';
import '../screens/copilot/ai_copilot_screen.dart';
import '../screens/sentinel/ai_sentinel_screen.dart';
import '../screens/forensics/ai_forensics_screen.dart';
import '../screens/fno/fno_screen.dart';
import '../screens/orders/order_book_screen.dart';
import '../screens/portfolio/portfolio_screen.dart';
import '../screens/portfolio/ai_portfolio_optimizer_screen.dart';
import '../screens/journal/journal_screen.dart';
import '../screens/risk/live_risk_center_screen.dart';
import '../screens/risk/ai_risk_command_center_screen.dart';
import '../screens/settings/settings_screen.dart';

class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> with WidgetsBindingObserver {
  int _currentIndex = 0;

  late final List<Widget> _screens = [
    DashboardScreen(onNavigate: _navigateTo),
    const MarketIntelligenceScreen(),
    const GlobalMacroScreen(),
    const AiNewsScreen(),
    const ScannerScreen(),
    const AiCopilotScreen(),
    const AiSentinelScreen(),
    const AiForensicsScreen(),
    const FnoScreen(),
    const OrderBookScreen(),
    const PortfolioScreen(),
    const AiPortfolioOptimizerScreen(),
    const JournalScreen(),
    const LiveRiskCenterScreen(),
    const AiRiskCommandCenterScreen(),
    const SettingsScreen(),
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    ApiConfig.logProductionEvent('INFO', 'App initialized and listening to lifecycle events.');
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    if (state == AppLifecycleState.resumed) {
      ApiConfig.logProductionEvent('INFO', 'App resumed from background. Validating connectivity.');
    } else if (state == AppLifecycleState.paused) {
      ApiConfig.logProductionEvent('INFO', 'App paused into background.');
    }
  }

  void _navigateTo(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: _navigateTo,
        backgroundColor: const Color(0xFF0B0E14),
        indicatorColor: Colors.blueAccent.withValues(alpha: 0.25),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.dashboard_outlined),
            selectedIcon: Icon(Icons.dashboard, color: Colors.blueAccent),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.analytics_outlined),
            selectedIcon: Icon(Icons.analytics, color: Colors.cyanAccent),
            label: 'Market AI',
          ),
          NavigationDestination(
            icon: Icon(Icons.radar_outlined),
            selectedIcon: Icon(Icons.radar, color: Colors.blueAccent),
            label: 'Scanner',
          ),
          NavigationDestination(
            icon: Icon(Icons.psychology_outlined),
            selectedIcon: Icon(Icons.psychology, color: Colors.cyanAccent),
            label: 'Copilot',
          ),
          NavigationDestination(
            icon: Icon(Icons.show_chart_outlined),
            selectedIcon: Icon(Icons.show_chart, color: Colors.purpleAccent),
            label: 'F&O',
          ),
          NavigationDestination(
            icon: Icon(Icons.receipt_long_outlined),
            selectedIcon: Icon(Icons.receipt_long, color: Colors.blueAccent),
            label: 'Orders',
          ),
          NavigationDestination(
            icon: Icon(Icons.pie_chart_outline),
            selectedIcon: Icon(Icons.pie_chart, color: Colors.cyanAccent),
            label: 'Portfolio',
          ),
          NavigationDestination(
            icon: Icon(Icons.menu_book_outlined),
            selectedIcon: Icon(Icons.menu_book, color: Colors.amberAccent),
            label: 'Journal',
          ),
          NavigationDestination(
            icon: Icon(Icons.shield_outlined),
            selectedIcon: Icon(Icons.shield, color: Colors.redAccent),
            label: 'Risk',
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            selectedIcon: Icon(Icons.settings, color: Colors.grey),
            label: 'Settings',
          ),
        ],
      ),
    );
  }
}
