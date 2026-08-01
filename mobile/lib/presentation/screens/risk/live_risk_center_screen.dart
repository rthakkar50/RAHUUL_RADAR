import 'package:flutter/material.dart';

class LiveRiskCenterScreen extends StatefulWidget {
  const LiveRiskCenterScreen({super.key});

  @override
  State<LiveRiskCenterScreen> createState() => _LiveRiskCenterScreenState();
}

class _LiveRiskCenterScreenState extends State<LiveRiskCenterScreen> {
  bool _autoTradingEnabled = true;

  void _triggerEmergencyKillSwitch() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF161B22),
        title: const Row(
          children: [
            Icon(Icons.warning_amber, color: Colors.redAccent),
            SizedBox(width: 8),
            Text(
              'EMERGENCY KILL SWITCH',
              style: TextStyle(
                color: Colors.redAccent,
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
          ],
        ),
        content: const Text(
          'WARNING: This will instantly CLOSE ALL OPEN POSITIONS at Market Price and CANCEL ALL PENDING ORDERS. Are you sure?',
          style: TextStyle(color: Colors.white70, fontSize: 12),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text(
                    'EMERGENCY KILL SWITCH ACTIVATED — All Positions Squaring Off!',
                  ),
                  backgroundColor: Colors.redAccent,
                ),
              );
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
            child: const Text(
              'EXECUTE KILL SWITCH',
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
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
                  colors: [Colors.redAccent, Colors.orangeAccent],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(
                Icons.shield_outlined,
                color: Colors.white,
                size: 18,
              ),
            ),
            const SizedBox(width: 8),
            const Text(
              'Live Risk Command Center',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildRiskOverviewCard(),
            const SizedBox(height: 16),
            _buildLossLimitsCard(),
            const SizedBox(height: 16),
            _buildAutoTradingControlCard(),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton.icon(
                onPressed: _triggerEmergencyKillSwitch,
                icon: const Icon(Icons.cancel, color: Colors.white),
                label: const Text(
                  'EMERGENCY KILL SWITCH (SQUARE OFF ALL)',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red.shade900,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRiskOverviewCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        children: [
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Portfolio Risk Meter',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontStyle: FontStyle.italic,
                  color: Colors.white,
                ),
              ),
              Text(
                'STATUS: SAFE (0.69%)',
                style: TextStyle(
                  color: Colors.greenAccent,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const LinearProgressIndicator(
            value: 0.25,
            color: Colors.greenAccent,
            backgroundColor: Colors.white10,
            minHeight: 8,
          ),
          const SizedBox(height: 14),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _riskTile('Available Cash', '₹2,76,405', Colors.white),
              _riskTile('Broker Margin', '₹7,23,244', Colors.amberAccent),
              _riskTile('Capital Used', '72.3%', Colors.cyanAccent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _riskTile(String label, String val, Color col) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 3),
        Text(
          val,
          style: TextStyle(
            color: col,
            fontWeight: FontWeight.bold,
            fontSize: 13,
          ),
        ),
      ],
    );
  }

  Widget _buildLossLimitsCard() {
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
            'Circuit Breaker & Loss Limits',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 14,
              color: Colors.white,
            ),
          ),
          SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Daily Max Loss Limit: ₹25,000',
                style: TextStyle(color: Colors.white70, fontSize: 12),
              ),
              Text(
                'Current: -₹6,548',
                style: TextStyle(
                  color: Colors.orangeAccent,
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
                'Weekly Max Loss Limit: ₹75,000',
                style: TextStyle(color: Colors.white70, fontSize: 12),
              ),
              Text(
                'Current: -₹6,548',
                style: TextStyle(
                  color: Colors.orangeAccent,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAutoTradingControlCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: SwitchListTile(
        title: const Text(
          'Autonomous Execution Engine',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 13,
          ),
        ),
        subtitle: const Text(
          'Auto-place orders when AI score > 85.0',
          style: TextStyle(color: Colors.grey, fontSize: 11),
        ),
        value: _autoTradingEnabled,
        onChanged: (v) => setState(() => _autoTradingEnabled = v),
      ),
    );
  }
}
