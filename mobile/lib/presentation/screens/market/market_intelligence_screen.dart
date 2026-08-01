import 'package:flutter/material.dart';
import '../../../data/repositories/scanner_repository.dart';

class MarketIntelligenceScreen extends StatefulWidget {
  const MarketIntelligenceScreen({super.key});

  @override
  State<MarketIntelligenceScreen> createState() =>
      _MarketIntelligenceScreenState();
}

class _MarketIntelligenceScreenState extends State<MarketIntelligenceScreen>
    with SingleTickerProviderStateMixin {
  final ScannerRepository _scannerRepo = ScannerRepository();
  bool _isLoading = false;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      await _scannerRepo.getSwingScans();
      if (mounted) setState(() => _isLoading = false);
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
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
                  colors: [Colors.cyanAccent, Colors.blueAccent],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(
                Icons.analytics_outlined,
                color: Colors.black,
                size: 18,
              ),
            ),
            const SizedBox(width: 8),
            const Text(
              'Institutional Market Intelligence',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
          ],
        ),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadData),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Overview'),
            Tab(text: 'Sectors'),
            Tab(text: 'Flows & Breadth'),
            Tab(text: 'Volatility'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(color: Colors.cyanAccent),
            )
          : TabBarView(
              controller: _tabController,
              children: [
                _buildOverviewTab(),
                _buildSectorsTab(),
                _buildFlowsBreadthTab(),
                _buildVolatilityTab(),
              ],
            ),
    );
  }

  Widget _buildOverviewTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildMarketGradeCard(),
        const SizedBox(height: 16),
        _buildAICommentaryCard(),
        const SizedBox(height: 16),
        _buildLiveHeatmapCard(),
        const SizedBox(height: 16),
        _buildTopOpportunitiesCard(),
      ],
    );
  }

  Widget _buildMarketGradeCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.3)),
      ),
      child: Column(
        children: [
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Overall Market Grade',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              Text(
                'GRADE A+ (BULLISH)',
                style: TextStyle(
                  color: Colors.greenAccent,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricTile('Market Bias', 'BULLISH 78%', Colors.greenAccent),
              _metricTile('Trend Strength', '92.4 / 100', Colors.cyanAccent),
              _metricTile('Volatility', 'LOW (13.8)', Colors.amberAccent),
              _metricTile('AI Confidence', '94.2%', Colors.greenAccent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _metricTile(String label, String val, Color col) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 3),
        Text(
          val,
          style: TextStyle(
            color: col,
            fontWeight: FontWeight.bold,
            fontSize: 11,
          ),
        ),
      ],
    );
  }

  Widget _buildAICommentaryCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.psychology, color: Colors.purpleAccent, size: 18),
              SizedBox(width: 8),
              Text(
                'Institutional AI Commentary Engine',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
            ],
          ),
          SizedBox(height: 10),
          Text(
            '• Broader market structure remains strongly bullish above NIFTY 24,500.\n'
            '• Institutional money flow accelerating into Pharma and IT sectors.\n'
            '• Banking stocks showing heavy accumulation with low volatility contraction.\n'
            '• AI Recommendation: PREFER PHARMA & IT. AVOID METALS & REALTY.',
            style: TextStyle(color: Colors.white70, fontSize: 12, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildLiveHeatmapCard() {
    final indices = [
      {'name': 'NIFTY 50', 'change': '+1.25%', 'col': Colors.greenAccent},
      {'name': 'BANKNIFTY', 'change': '+0.88%', 'col': Colors.greenAccent},
      {'name': 'FINNIFTY', 'change': '+1.10%', 'col': Colors.greenAccent},
      {'name': 'MIDCAP 100', 'change': '-0.45%', 'col': Colors.redAccent},
    ];

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Module 2 — Live Market Heatmap',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 13,
            ),
          ),
          const SizedBox(height: 12),
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              childAspectRatio: 2.5,
              crossAxisSpacing: 10,
              mainAxisSpacing: 10,
            ),
            itemCount: indices.length,
            itemBuilder: (ctx, i) {
              final idx = indices[i];
              return Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: (idx['col'] as Color).withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: idx['col'] as Color),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      idx['name'] as String,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                    Text(
                      idx['change'] as String,
                      style: TextStyle(
                        color: idx['col'] as Color,
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildTopOpportunitiesCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Module 9 — Top 10 High Confidence Opportunities',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 13,
            ),
          ),
          SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '1. DIVISLAB (PHARMA)',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                'BUY 94.2% • R:R 1:3.2',
                style: TextStyle(
                  color: Colors.greenAccent,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '2. RELIANCE (ENERGY)',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                'BUY 91.0% • R:R 1:2.8',
                style: TextStyle(
                  color: Colors.greenAccent,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '3. HDFCBANK (BANKING)',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                'BUY 88.5% • R:R 1:2.5',
                style: TextStyle(
                  color: Colors.greenAccent,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSectorsTab() {
    final sectors = [
      {
        'name': 'PHARMA',
        'strength': '96.4',
        'flow': '+₹1,420 Cr',
        'rec': 'STRONG ACCUMULATION',
        'col': Colors.greenAccent,
      },
      {
        'name': 'IT',
        'strength': '91.2',
        'flow': '+₹890 Cr',
        'rec': 'BULLISH OUTPERFORM',
        'col': Colors.greenAccent,
      },
      {
        'name': 'BANKING',
        'strength': '85.0',
        'flow': '+₹650 Cr',
        'rec': 'ACCUMULATE ON DIPS',
        'col': Colors.cyanAccent,
      },
      {
        'name': 'AUTO',
        'strength': '74.5',
        'flow': '+₹210 Cr',
        'rec': 'NEUTRAL / HOLD',
        'col': Colors.amberAccent,
      },
      {
        'name': 'METALS',
        'strength': '38.0',
        'flow': '-₹540 Cr',
        'rec': 'UNDERPERFORM / AVOID',
        'col': Colors.redAccent,
      },
    ];

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: sectors.length,
      itemBuilder: (ctx, i) {
        final sec = sectors[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 10),
          child: ListTile(
            title: Text(
              sec['name'] as String,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            subtitle: Text(
              'Strength: ${sec['strength']} • Money Flow: ${sec['flow']}',
              style: const TextStyle(color: Colors.grey, fontSize: 11),
            ),
            trailing: Text(
              sec['rec'] as String,
              style: TextStyle(
                color: sec['col'] as Color,
                fontWeight: FontWeight.bold,
                fontSize: 11,
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildFlowsBreadthTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white10),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Module 4 — Institutional FII / DII Flow Engine',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'FII Net Flow (Cash): +₹2,450 Cr',
                    style: TextStyle(
                      color: Colors.greenAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                  Text(
                    'DII Net Flow: +₹1,120 Cr',
                    style: TextStyle(
                      color: Colors.greenAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
              SizedBox(height: 6),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'FII Index Futures: +₹820 Cr',
                    style: TextStyle(
                      color: Colors.cyanAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                  Text(
                    'Net Institutional Flow: +₹4,390 Cr',
                    style: TextStyle(
                      color: Colors.greenAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white10),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Module 5 — Market Breadth Matrix',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Advances: 1,420',
                    style: TextStyle(
                      color: Colors.greenAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                  Text(
                    'Declines: 680',
                    style: TextStyle(
                      color: Colors.redAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                  Text(
                    'A/D Ratio: 2.08',
                    style: TextStyle(
                      color: Colors.cyanAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
              SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '52W Highs: 84',
                    style: TextStyle(color: Colors.greenAccent, fontSize: 11),
                  ),
                  Text(
                    '52W Lows: 6',
                    style: TextStyle(color: Colors.redAccent, fontSize: 11),
                  ),
                  Text(
                    'Gap Ups: 34',
                    style: TextStyle(color: Colors.cyanAccent, fontSize: 11),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildVolatilityTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.white10),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Module 6 — Volatility & Option Analytics Center',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'India VIX: 13.82 (-2.1%)',
                    style: TextStyle(
                      color: Colors.greenAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                  Text(
                    'PCR (NIFTY): 1.28 (BULLISH)',
                    style: TextStyle(
                      color: Colors.cyanAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
              SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Max Pain: 24,600',
                    style: TextStyle(
                      color: Colors.amberAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                  Text(
                    'IV Rank: 22.4%',
                    style: TextStyle(
                      color: Colors.purpleAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}
