import 'package:flutter/material.dart';
import '../../../data/models/broker_connector_model.dart';
import '../../../data/repositories/broker_orchestrator.dart';

class BrokerSettingsScreen extends StatefulWidget {
  const BrokerSettingsScreen({super.key});

  @override
  State<BrokerSettingsScreen> createState() => _BrokerSettingsScreenState();
}

class _BrokerSettingsScreenState extends State<BrokerSettingsScreen> {
  final BrokerOrchestrator _orchestrator = BrokerOrchestrator();

  @override
  Widget build(BuildContext context) {
    final brokers = _orchestrator.getAvailableBrokers();
    final active = brokers.firstWhere((b) => b.isDefault, orElse: () => brokers.first);

    return Scaffold(
      backgroundColor: const Color(0xFF0B0E14),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B0E14),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Colors.amberAccent, Colors.orangeAccent]),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.hub_outlined, color: Colors.black, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('Broker Orchestrator Hub', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildActiveBrokerCard(active),
            const SizedBox(height: 16),
            _buildAccountSummaryCard(),
            const SizedBox(height: 16),
            _buildFailoverCard(),
            const SizedBox(height: 16),
            _buildMultiBrokerConnectorsList(brokers),
            const SizedBox(height: 16),
            _buildAuditLogsCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildActiveBrokerCard(BrokerInfoModel active) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.amberAccent.withValues(alpha: 0.4), width: 1.2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.verified, color: Colors.amberAccent, size: 20),
                  const SizedBox(width: 8),
                  Text(active.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(color: Colors.greenAccent.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(6)),
                child: const Text('CONNECTED', style: TextStyle(color: Colors.greenAccent, fontSize: 10, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(color: Colors.white10, height: 1),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _infoTile('Latency', '${active.latencyMs} ms', Colors.cyanAccent),
              _infoTile('API Health', active.apiHealth, Colors.greenAccent),
              _infoTile('Token Expiry', active.tokenExpiry, Colors.amberAccent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _infoTile(String label, String val, Color col) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        const SizedBox(height: 2),
        Text(val, style: TextStyle(color: col, fontWeight: FontWeight.bold, fontSize: 12)),
      ],
    );
  }

  Widget _buildAccountSummaryCard() {
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
          Text('Module 4 — Unified Account Manager', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
          SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Account Balance: ₹9,93,101.13', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
              Text('Margin Used: ₹7,23,244.20', style: TextStyle(color: Colors.amberAccent, fontSize: 12, fontWeight: FontWeight.bold)),
            ],
          ),
          SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Buying Power: ₹2,76,405.13', style: TextStyle(color: Colors.cyanAccent, fontSize: 12, fontWeight: FontWeight.bold)),
              Text('Open Positions: 5', style: TextStyle(color: Colors.greenAccent, fontSize: 12, fontWeight: FontWeight.bold)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFailoverCard() {
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
          Text('Module 6 — Failover Readiness Framework', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
          SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Primary Broker:', style: TextStyle(color: Colors.grey, fontSize: 11)),
              Text('Paytm Money API v2 (ACTIVE)', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 11)),
            ],
          ),
          SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Secondary Standby:', style: TextStyle(color: Colors.grey, fontSize: 11)),
              Text('Zerodha Kite Connect v3 (READY)', style: TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 11)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMultiBrokerConnectorsList(List<BrokerInfoModel> brokers) {
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
          const Text('Module 2 — Multi-Broker Connector Registry', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
          const SizedBox(height: 10),
          ...brokers.map((b) {
            return ListTile(
              dense: true,
              contentPadding: EdgeInsets.zero,
              title: Text(b.name, style: TextStyle(color: b.isActive ? Colors.white : Colors.white60, fontWeight: FontWeight.bold, fontSize: 13)),
              subtitle: Text(b.isActive ? 'Active Primary Connection' : 'Inactive Connector (Future Ready)', style: TextStyle(color: b.isActive ? Colors.greenAccent : Colors.grey, fontSize: 10)),
              trailing: b.isActive
                  ? const Icon(Icons.check_circle, color: Colors.greenAccent, size: 18)
                  : ElevatedButton(
                      onPressed: null,
                      style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 8), visualDensity: VisualDensity.compact),
                      child: const Text('Connect', style: TextStyle(fontSize: 10)),
                    ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildAuditLogsCard() {
    final logs = _orchestrator.getAuditLogs();
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
          const Text('Module 7 — Broker Action Audit Logs', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.white)),
          const SizedBox(height: 10),
          ...logs.take(3).map((l) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 6.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('[${l.action}] ${l.brokerName}', style: const TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                  Text(l.details, style: const TextStyle(color: Colors.grey, fontSize: 10)),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }
}
