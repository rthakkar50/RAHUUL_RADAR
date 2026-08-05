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
import '../screens/profile/user_profile_screen.dart';
import '../screens/settings/settings_screen.dart';
import '../screens/terminal/advanced_trading_terminal_screen.dart';

import '../../core/version/app_version_manager.dart';

class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation>
    with WidgetsBindingObserver {
  int _currentIndex = 0;

  late final List<Widget> _screens = [
    DashboardScreen(onNavigate: _navigateTo), // Index 0: Home
    const MarketIntelligenceScreen(), // Index 1: Market AI
    const ScannerScreen(), // Index 2: Swing Trading Scanner ONLY
    const AiCopilotScreen(), // Index 3: Copilot
    const FnoScreen(), // Index 4: F&O Terminal ONLY
    const OrderBookScreen(), // Index 5: Orders
    const PortfolioScreen(), // Index 6: Portfolio
    const JournalScreen(), // Index 7: Journal
    const LiveRiskCenterScreen(), // Index 8: Risk
    const SettingsScreen(), // Index 9: Settings
    const GlobalMacroScreen(), // Index 10: Global Macro
    const AiNewsScreen(), // Index 11: AI News
    const AiSentinelScreen(), // Index 12: AI Sentinel
    const AiForensicsScreen(), // Index 13: AI Forensics
    const AiPortfolioOptimizerScreen(), // Index 14: Portfolio Optimizer
    const AiRiskCommandCenterScreen(), // Index 15: Risk Command Center
    const UserProfileScreen(), // Index 16: User Profile
    const AdvancedTradingTerminalScreen(), // Index 17: Advanced Terminal
  ];


  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    ApiConfig.logProductionEvent(
      'INFO',
      'App initialized and listening to lifecycle events.',
    );
    _checkForUpdates();
  }

  Future<void> _checkForUpdates() async {
    final versionModel = await AppVersionManager.instance.checkAppVersion();
    if (versionModel != null && mounted) {
      AppVersionManager.instance.promptUpdateIfAvailable(context, versionModel);
    }
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
      ApiConfig.logProductionEvent(
        'INFO',
        'App resumed from background. Validating connectivity.',
      );
    } else if (state == AppLifecycleState.paused) {
      ApiConfig.logProductionEvent('INFO', 'App paused into background.');
    }
  }

  int _selectedNavTab = 0; // 0: Home, 1: Scanner, 2: Portfolio, 3: Orders, 4: More

  void _navigateTo(int index) {
    setState(() {
      _currentIndex = index;
      if (index == 0) {
        _selectedNavTab = 0;
      } else if (index == 2) {
        _selectedNavTab = 1;
      } else if (index == 6) {
        _selectedNavTab = 2;
      } else if (index == 5) {
        _selectedNavTab = 3;
      } else {
        _selectedNavTab = 4;
      }
    });
  }

  void _showMoreMenu(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF0B0E14),
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        return Container(
          height: MediaQuery.of(context).size.height * 0.85,
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.white24,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Institutional Navigation Suite',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.grey),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
              const Divider(color: Colors.white10),
              Expanded(
                child: ListView(
                  children: [
                    _buildSectionHeader('🤖 AI Suite & Forecasting', Colors.cyanAccent),
                    _buildMenuItem(ctx, 'AI Copilot Decision Intelligence', Icons.psychology, Colors.cyanAccent, 3),
                    _buildMenuItem(ctx, 'AI Sentinel & Market Forecast', Icons.radar, Colors.greenAccent, 12),
                    _buildMenuItem(ctx, 'AI Forensics & Learning Hub', Icons.policy, Colors.tealAccent, 13),
                    
                    const SizedBox(height: 16),
                    _buildSectionHeader('📈 Trading & Execution Center', Colors.purpleAccent),
                    _buildMenuItem(ctx, 'F&O Trading Center', Icons.show_chart, Colors.purpleAccent, 4),
                    _buildMenuItem(ctx, 'Trade Journal & Analytics', Icons.menu_book, Colors.amberAccent, 7),
                    _buildMenuItem(ctx, 'Live Risk Center', Icons.shield, Colors.redAccent, 8),
                    _buildMenuItem(ctx, 'Risk Command Center', Icons.warning_amber, Colors.deepOrange, 15),
                    
                    const SizedBox(height: 16),
                    _buildSectionHeader('🌍 Market Intelligence & Research', Colors.blueAccent),
                    _buildMenuItem(ctx, 'Market AI & Options Analytics', Icons.analytics_outlined, Colors.blueAccent, 1),
                    _buildMenuItem(ctx, 'Global Macro Intelligence Hub', Icons.public, Colors.indigoAccent, 10),
                    _buildMenuItem(ctx, 'AI News & Sentiment Engine', Icons.newspaper, Colors.orangeAccent, 11),
                    _buildMenuItem(ctx, 'Portfolio Optimizer', Icons.pie_chart, Colors.amber, 14),
                    
                    const SizedBox(height: 16),
                    _buildSectionHeader('⚙ Account & Settings', Colors.grey),
                    _buildMenuItem(ctx, 'User Profile & Cloud Workspace', Icons.person, Colors.cyan, 16),
                    _buildMenuItem(ctx, 'Settings & System Diagnostics', Icons.settings, Colors.grey, 9),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSectionHeader(String title, Color accentColor) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, top: 4),
      child: Text(
        title,
        style: TextStyle(
          color: accentColor,
          fontWeight: FontWeight.bold,
          fontSize: 13,
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  Widget _buildMenuItem(BuildContext ctx, String label, IconData icon, Color color, int targetIndex) {
    return Card(
      color: const Color(0xFF161B22),
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        leading: Icon(icon, color: color, size: 22),
        title: Text(
          label,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 13,
            fontWeight: FontWeight.w600,
          ),
        ),
        trailing: const Icon(Icons.chevron_right, color: Colors.grey, size: 18),
        onTap: () {
          Navigator.pop(ctx);
          _navigateTo(targetIndex);
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: _screens),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedNavTab,
        onDestinationSelected: (idx) {
          if (idx == 4) {
            _showMoreMenu(context);
          } else {
            if (idx == 0) {
              _navigateTo(0);
            } else if (idx == 1) {
              _navigateTo(2);
            } else if (idx == 2) {
              _navigateTo(6);
            } else if (idx == 3) {
              _navigateTo(5);
            }
          }
        },
        backgroundColor: const Color(0xFF0B0E14),
        indicatorColor: Colors.blueAccent.withValues(alpha: 0.25),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home, color: Colors.blueAccent),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.radar_outlined),
            selectedIcon: Icon(Icons.radar, color: Colors.cyanAccent),
            label: 'Scanner',
          ),
          NavigationDestination(
            icon: Icon(Icons.pie_chart_outline),
            selectedIcon: Icon(Icons.pie_chart, color: Colors.greenAccent),
            label: 'Portfolio',
          ),
          NavigationDestination(
            icon: Icon(Icons.receipt_long_outlined),
            selectedIcon: Icon(Icons.receipt_long, color: Colors.amberAccent),
            label: 'Orders',
          ),
          NavigationDestination(
            icon: Icon(Icons.menu),
            selectedIcon: Icon(Icons.menu, color: Colors.purpleAccent),
            label: 'More',
          ),
        ],
      ),
    );
  }
}
