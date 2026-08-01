import 'package:flutter/material.dart';
import '../../../data/repositories/global_macro_repository.dart';

class GlobalMacroScreen extends StatefulWidget {
  const GlobalMacroScreen({super.key});

  @override
  State<GlobalMacroScreen> createState() => _GlobalMacroScreenState();
}

class _GlobalMacroScreenState extends State<GlobalMacroScreen>
    with SingleTickerProviderStateMixin {
  final GlobalMacroRepository _repo = GlobalMacroRepository();
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final indices = _repo.getGlobalIndices();
    final commodities = _repo.getCommodities();
    final calendar = _repo.getEconomicCalendar();
    final briefing = _repo.getDailyBriefing();

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
                  colors: [Colors.blueAccent, Colors.cyanAccent],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.public, color: Colors.black, size: 18),
            ),
            const SizedBox(width: 8),
            const Text(
              'Global Macro Intelligence Hub',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17),
            ),
          ],
        ),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Briefing'),
            Tab(text: 'Indices'),
            Tab(text: 'Commodities'),
            Tab(text: 'Calendar'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildBriefingTab(briefing),
          _buildIndicesTab(indices),
          _buildCommoditiesTab(commodities),
          _buildCalendarTab(calendar),
        ],
      ),
    );
  }

  Widget _buildBriefingTab(List<String> briefing) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.4)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(
                    Icons.wb_sunny_outlined,
                    color: Colors.amberAccent,
                    size: 20,
                  ),
                  SizedBox(width: 8),
                  Text(
                    'Module 9 — AI Morning Daily Briefing',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              ...briefing.map(
                (b) => Padding(
                  padding: const EdgeInsets.only(bottom: 8.0),
                  child: Text(
                    '• $b',
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 12,
                      height: 1.4,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildIndicesTab(List<GlobalMarketTickerModel> indices) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: indices.length,
      itemBuilder: (ctx, i) {
        final item = indices[i];
        final col = item.isPositive ? Colors.greenAccent : Colors.redAccent;
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 10),
          child: ListTile(
            title: Text(
              item.name,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            subtitle: Text(
              item.value,
              style: const TextStyle(color: Colors.grey, fontSize: 12),
            ),
            trailing: Text(
              item.change,
              style: TextStyle(
                color: col,
                fontWeight: FontWeight.bold,
                fontSize: 13,
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildCommoditiesTab(List<GlobalMarketTickerModel> commodities) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: commodities.length,
      itemBuilder: (ctx, i) {
        final item = commodities[i];
        final col = item.isPositive ? Colors.greenAccent : Colors.redAccent;
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 10),
          child: ListTile(
            title: Text(
              item.name,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            subtitle: Text(
              item.value,
              style: const TextStyle(color: Colors.grey, fontSize: 12),
            ),
            trailing: Text(
              item.change,
              style: TextStyle(
                color: col,
                fontWeight: FontWeight.bold,
                fontSize: 13,
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildCalendarTab(List<EconomicEventModel> calendar) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: calendar.length,
      itemBuilder: (ctx, i) {
        final ev = calendar[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(14.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '${ev.country} — ${ev.event}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 6,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.redAccent.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        ev.impact,
                        style: const TextStyle(
                          color: Colors.redAccent,
                          fontSize: 9,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  'Time: ${ev.date} • Forecast: ${ev.forecast} • Previous: ${ev.previous}',
                  style: const TextStyle(color: Colors.grey, fontSize: 11),
                ),
                const Divider(color: Colors.white10),
                Text(
                  'AI Event Impact Verdict: ${ev.aiVerdict}',
                  style: const TextStyle(
                    color: Colors.cyanAccent,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
