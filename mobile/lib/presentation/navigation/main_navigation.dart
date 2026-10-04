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
import '../screens/paper_trading/paper_trading_screen.dart';
import '../screens/portfolio/paper_portfolio_screen.dart';

import '../../core/version/app_version_manager.dart';

class _NavItemSpec {
  final String label;
  final String? subtitle;
  final IconData icon;
  final VoidCallback onTap;

  const _NavItemSpec({
    required this.label,
    required this.icon,
    required this.onTap,
    this.subtitle,
  });
}

class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation>
    with WidgetsBindingObserver {
  // Sober institutional palette tokens (scoped to navigation shell)
  static const Color _bgBase = Color(0xFF0B0E14);
  static const Color _surfaceGroup = Color(0xFF121721);
  static const Color _borderSubtle = Color(0xFF1F2735);
  static const Color _accentBlue = Color(0xFF3B82F6);
  static const Color _textPrimary = Color(0xFFF0F6FC);
  static const Color _textSecondary = Color(0xFF8B949E);

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

  void _openIndexedFromSheet(BuildContext sheetContext, int targetIndex) {
    Navigator.pop(sheetContext);
    _navigateTo(targetIndex);
  }

  void _openRouteFromSheet(BuildContext sheetContext, Widget screen) {
    Navigator.pop(sheetContext);
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => screen),
    );
  }

  void _showMoreMenu(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: _bgBase,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        side: BorderSide(color: _borderSubtle, width: 1),
      ),
      builder: (ctx) {
        return SafeArea(
          top: false,
          child: ConstrainedBox(
            constraints: BoxConstraints(
              maxHeight: MediaQuery.of(context).size.height * 0.82,
            ),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 20),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(
                      width: 36,
                      height: 4,
                      decoration: BoxDecoration(
                        color: _borderSubtle,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'More',
                        style: TextStyle(
                          color: _textPrimary,
                          fontWeight: FontWeight.w600,
                          fontSize: 18,
                          letterSpacing: 0.2,
                        ),
                      ),
                      IconButton(
                        icon: const Icon(
                          Icons.close,
                          color: _textSecondary,
                          size: 20,
                        ),
                        visualDensity: VisualDensity.compact,
                        onPressed: () => Navigator.pop(ctx),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Flexible(
                    child: ListView(
                      shrinkWrap: true,
                      children: [
                        _buildSectionHeader('TRADING'),
                        _buildSectionGroup([
                          _NavItemSpec(
                            label: 'F&O',
                            icon: Icons.show_chart,
                            onTap: () => _openIndexedFromSheet(ctx, 4),
                          ),
                          _NavItemSpec(
                            label: 'Trade Journal',
                            icon: Icons.menu_book_outlined,
                            onTap: () => _openIndexedFromSheet(ctx, 7),
                          ),
                        ]),
                        const SizedBox(height: 16),
                        _buildSectionHeader('INTELLIGENCE'),
                        _buildSectionGroup([
                          _NavItemSpec(
                            label: 'Market AI',
                            icon: Icons.analytics_outlined,
                            onTap: () => _openIndexedFromSheet(ctx, 1),
                          ),
                          _NavItemSpec(
                            label: 'AI Copilot',
                            icon: Icons.psychology_outlined,
                            onTap: () => _openIndexedFromSheet(ctx, 3),
                          ),
                        ]),
                        const SizedBox(height: 16),
                        _buildSectionHeader('RISK'),
                        _buildSectionGroup([
                          _NavItemSpec(
                            label: 'Risk Center',
                            icon: Icons.shield_outlined,
                            onTap: () => _openIndexedFromSheet(ctx, 8),
                          ),
                        ]),
                        const SizedBox(height: 16),
                        _buildSectionHeader('SYSTEM'),
                        _buildSectionGroup([
                          _NavItemSpec(
                            label: 'Settings',
                            icon: Icons.settings_outlined,
                            onTap: () => _openIndexedFromSheet(ctx, 9),
                          ),
                          _NavItemSpec(
                            label: 'Profile',
                            icon: Icons.person_outline,
                            onTap: () => _openIndexedFromSheet(ctx, 16),
                          ),
                        ]),
                        const SizedBox(height: 16),
                        _buildSectionHeader('ADVANCED'),
                        _buildSectionGroup([
                          _NavItemSpec(
                            label: 'Advanced Tools',
                            subtitle: 'Research, forensics, macro & paper trading',
                            icon: Icons.tune_outlined,
                            onTap: () {
                              Navigator.pop(ctx);
                              _showAdvancedToolsSheet(context);
                            },
                          ),
                        ]),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  void _showAdvancedToolsSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: _bgBase,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        side: BorderSide(color: _borderSubtle, width: 1),
      ),
      builder: (ctx) {
        return SafeArea(
          top: false,
          child: ConstrainedBox(
            constraints: BoxConstraints(
              maxHeight: MediaQuery.of(context).size.height * 0.82,
            ),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 20),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(
                      width: 36,
                      height: 4,
                      decoration: BoxDecoration(
                        color: _borderSubtle,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      IconButton(
                        icon: const Icon(
                          Icons.arrow_back_ios_new,
                          color: _textSecondary,
                          size: 18,
                        ),
                        visualDensity: VisualDensity.compact,
                        onPressed: () {
                          Navigator.pop(ctx);
                          _showMoreMenu(context);
                        },
                      ),
                      const SizedBox(width: 4),
                      const Expanded(
                        child: Text(
                          'Advanced Tools',
                          style: TextStyle(
                            color: _textPrimary,
                            fontWeight: FontWeight.w600,
                            fontSize: 18,
                            letterSpacing: 0.2,
                          ),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(
                          Icons.close,
                          color: _textSecondary,
                          size: 20,
                        ),
                        visualDensity: VisualDensity.compact,
                        onPressed: () => Navigator.pop(ctx),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Flexible(
                    child: ListView(
                      shrinkWrap: true,
                      children: [
                        _buildSectionHeader('SECONDARY INTELLIGENCE & RISK'),
                        _buildSectionGroup([
                          _NavItemSpec(
                            label: 'AI Sentinel',
                            icon: Icons.radar_outlined,
                            onTap: () => _openIndexedFromSheet(ctx, 12),
                          ),
                          _NavItemSpec(
                            label: 'AI Forensics',
                            icon: Icons.policy_outlined,
                            onTap: () => _openIndexedFromSheet(ctx, 13),
                          ),
                          _NavItemSpec(
                            label: 'Global Macro',
                            icon: Icons.public_outlined,
                            onTap: () => _openIndexedFromSheet(ctx, 10),
                          ),
                          _NavItemSpec(
                            label: 'AI News',
                            icon: Icons.newspaper_outlined,
                            onTap: () => _openIndexedFromSheet(ctx, 11),
                          ),
                          _NavItemSpec(
                            label: 'Portfolio Optimizer',
                            icon: Icons.donut_large_outlined,
                            onTap: () => _openIndexedFromSheet(ctx, 14),
                          ),
                          _NavItemSpec(
                            label: 'Risk Command Center',
                            icon: Icons.gpp_maybe_outlined,
                            onTap: () => _openIndexedFromSheet(ctx, 15),
                          ),
                        ]),
                        const SizedBox(height: 16),
                        _buildSectionHeader('SIMULATION'),
                        _buildSectionGroup([
                          _NavItemSpec(
                            label: 'Paper Trading',
                            icon: Icons.edit_note_outlined,
                            onTap: () => _openRouteFromSheet(
                              ctx,
                              const PaperTradingScreen(),
                            ),
                          ),
                          _NavItemSpec(
                            label: 'Paper Portfolio',
                            icon: Icons.account_balance_wallet_outlined,
                            onTap: () => _openRouteFromSheet(
                              ctx,
                              const PaperPortfolioScreen(),
                            ),
                          ),
                        ]),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 4, bottom: 8),
      child: Text(
        title,
        style: const TextStyle(
          color: _textSecondary,
          fontWeight: FontWeight.w600,
          fontSize: 11,
          letterSpacing: 1.0,
        ),
      ),
    );
  }

  Widget _buildSectionGroup(List<_NavItemSpec> items) {
    return Container(
      decoration: BoxDecoration(
        color: _surfaceGroup,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _borderSubtle, width: 1),
      ),
      child: Column(
        children: [
          for (int i = 0; i < items.length; i++) ...[
            if (i > 0)
              const Divider(
                height: 1,
                thickness: 1,
                indent: 48,
                color: _borderSubtle,
              ),
            _buildMenuRow(items[i]),
          ],
        ],
      ),
    );
  }

  Widget _buildMenuRow(_NavItemSpec item) {
    return InkWell(
      borderRadius: BorderRadius.circular(12),
      onTap: item.onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
        child: Row(
          children: [
            Icon(item.icon, color: _accentBlue, size: 20),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.label,
                    style: const TextStyle(
                      color: _textPrimary,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  if (item.subtitle != null) ...[
                    const SizedBox(height: 2),
                    Text(
                      item.subtitle!,
                      style: const TextStyle(
                        color: _textSecondary,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const Icon(
              Icons.chevron_right,
              color: _textSecondary,
              size: 18,
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: _screens),
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          border: Border(
            top: BorderSide(color: _borderSubtle, width: 1),
          ),
        ),
        child: NavigationBarTheme(
          data: NavigationBarThemeData(
            labelTextStyle: WidgetStateProperty.resolveWith((states) {
              if (states.contains(WidgetState.selected)) {
                return const TextStyle(
                  color: _textPrimary,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                );
              }
              return const TextStyle(
                color: _textSecondary,
                fontSize: 12,
                fontWeight: FontWeight.w400,
              );
            }),
          ),
          child: NavigationBar(
            height: 64,
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
            backgroundColor: _bgBase,
            surfaceTintColor: Colors.transparent,
            indicatorColor: _accentBlue.withValues(alpha: 0.16),
            destinations: const [
              NavigationDestination(
                icon: Icon(Icons.home_outlined, color: _textSecondary, size: 20),
                selectedIcon: Icon(Icons.home, color: _accentBlue, size: 20),
                label: 'Home',
              ),
              NavigationDestination(
                icon: Icon(Icons.radar_outlined, color: _textSecondary, size: 20),
                selectedIcon: Icon(Icons.radar, color: _accentBlue, size: 20),
                label: 'Scanner',
              ),
              NavigationDestination(
                icon: Icon(
                  Icons.pie_chart_outline,
                  color: _textSecondary,
                  size: 20,
                ),
                selectedIcon: Icon(
                  Icons.pie_chart,
                  color: _accentBlue,
                  size: 20,
                ),
                label: 'Portfolio',
              ),
              NavigationDestination(
                icon: Icon(
                  Icons.receipt_long_outlined,
                  color: _textSecondary,
                  size: 20,
                ),
                selectedIcon: Icon(
                  Icons.receipt_long,
                  color: _accentBlue,
                  size: 20,
                ),
                label: 'Orders',
              ),
              NavigationDestination(
                icon: Icon(Icons.menu, color: _textSecondary, size: 20),
                selectedIcon: Icon(Icons.menu, color: _accentBlue, size: 20),
                label: 'More',
              ),
            ],
          ),
        ),
      ),
    );
  }
}
