import 'package:flutter/material.dart';
import '../../../data/repositories/news_repository.dart';

class AiNewsScreen extends StatefulWidget {
  const AiNewsScreen({super.key});

  @override
  State<AiNewsScreen> createState() => _AiNewsScreenState();
}

class _AiNewsScreenState extends State<AiNewsScreen> with SingleTickerProviderStateMixin {
  final NewsRepository _repo = NewsRepository();
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final newsList = _repo.getLatestNews();

    return Scaffold(
      backgroundColor: const Color(0xFF0B0E14),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B0E14),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Colors.cyanAccent, Colors.tealAccent]),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.newspaper_outlined, color: Colors.black, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('AI News & Sentiment Engine', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Live Feed'),
            Tab(text: 'Portfolio Impact'),
            Tab(text: 'Sentiment Heatmap'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildLiveFeedTab(newsList),
          _buildPortfolioImpactTab(newsList.first),
          _buildSentimentHeatmapTab(),
        ],
      ),
    );
  }

  Widget _buildLiveFeedTab(List<NewsItemModel> newsList) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: newsList.length,
      itemBuilder: (ctx, i) {
        final item = newsList[i];
        final isVeryBullish = item.sentiment == 'VERY BULLISH';
        final col = isVeryBullish ? Colors.greenAccent : Colors.cyanAccent;

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
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(color: Colors.redAccent.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(4)),
                      child: Text(item.category, style: const TextStyle(color: Colors.redAccent, fontSize: 9, fontWeight: FontWeight.bold)),
                    ),
                    Text(item.timeAgo, style: const TextStyle(color: Colors.grey, fontSize: 10)),
                  ],
                ),
                const SizedBox(height: 8),
                Text(item.title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                const SizedBox(height: 6),
                Text('Source: ${item.source} • Stock: ${item.affectedSymbol}', style: const TextStyle(color: Colors.white70, fontSize: 11)),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: col.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: col.withValues(alpha: 0.3)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('AI Sentiment: ${item.sentiment}', style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 12)),
                          Text('Confidence: ${item.confidencePct}%', style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 11)),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text('Summary: ${item.summary}', style: const TextStyle(color: Colors.white70, fontSize: 11)),
                      const SizedBox(height: 4),
                      Text('Action: ${item.suggestedAction}', style: const TextStyle(color: Colors.amberAccent, fontWeight: FontWeight.bold, fontSize: 11)),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildPortfolioImpactTab(NewsItemModel item) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.greenAccent.withValues(alpha: 0.4)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Row(
                children: [
                  Icon(Icons.warning_amber_rounded, color: Colors.greenAccent, size: 20),
                  SizedBox(width: 8),
                  Text('Module 6 — Portfolio Holding News Impact Alert', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                ],
              ),
              const SizedBox(height: 12),
              Text('Matched Holding: ${item.affectedSymbol} (Qty: 25 shares)', style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 13)),
              const SizedBox(height: 6),
              Text('Breaking Event: ${item.title}', style: const TextStyle(color: Colors.white70, fontSize: 12)),
              const SizedBox(height: 8),
              const Text('AI Expected Impact: POSITIVE (+3.5% to +5.0% price expansion)', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 12)),
              const SizedBox(height: 4),
              Text('Suggested Action: ${item.suggestedAction}', style: const TextStyle(color: Colors.amberAccent, fontWeight: FontWeight.bold, fontSize: 12)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildSentimentHeatmapTab() {
    final heatmap = [
      {'sector': 'PHARMA', 'sentiment': 'VERY BULLISH (94%)', 'col': Colors.greenAccent},
      {'sector': 'IT', 'sentiment': 'BULLISH (86%)', 'col': Colors.greenAccent},
      {'sector': 'ENERGY', 'sentiment': 'BULLISH (82%)', 'col': Colors.cyanAccent},
      {'sector': 'AUTO', 'sentiment': 'NEUTRAL (55%)', 'col': Colors.amberAccent},
      {'sector': 'METALS', 'sentiment': 'BEARISH (32%)', 'col': Colors.redAccent},
    ];

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: heatmap.length,
      itemBuilder: (ctx, i) {
        final item = heatmap[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 10),
          child: ListTile(
            title: Text(item['sector'] as String, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
            trailing: Text(item['sentiment'] as String, style: TextStyle(color: item['col'] as Color, fontWeight: FontWeight.bold, fontSize: 12)),
          ),
        );
      },
    );
  }
}
