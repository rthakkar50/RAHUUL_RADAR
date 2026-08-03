import 'package:flutter/material.dart';
import '../../../core/network/api_config.dart';
import 'broker_settings_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final TextEditingController _ipController = TextEditingController(
    text: ApiConfig.localIp,
  );
  final TextEditingController _portController = TextEditingController(
    text: ApiConfig.port,
  );

  bool _telegramEnabled = true;
  bool _autoRefreshEnabled = true;
  bool _isTesting = false;

  @override
  void dispose() {
    _ipController.dispose();
    _portController.dispose();
    super.dispose();
  }

  void _saveApiSettings() async {
    setState(() => _isTesting = true);
    await ApiConfig.saveSettings(
      _ipController.text,
      _portController.text,
      'Production',
    );
    setState(() => _isTesting = false);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('API Configuration Saved & Tested! Server: ${ApiConfig.serverType} (${ApiConfig.lastLatencyMs}ms)'),
          backgroundColor: ApiConfig.connectionState == ServerConnectionState.offline ? Colors.redAccent : Colors.green,
        ),
      );
    }
  }

  void _runManualTest() async {
    setState(() => _isTesting = true);
    final details = await ApiConfig.testConnectionDetails();
    setState(() => _isTesting = false);

    if (!mounted) return;

    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF161B22),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        final diag = details['diagnostics'] as Map<String, dynamic>;
        return Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Network Diagnostics Report',
                    style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.grey),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const Divider(color: Colors.white10),
              const SizedBox(height: 8),
              _diagRow('Resolved URL', details['resolvedUrl'] ?? 'N/A', Colors.cyanAccent),
              _diagRow('Server Type', details['serverName'] ?? 'N/A', Colors.amberAccent),
              _diagRow('Latency', '${details['latencyMs']} ms', Colors.greenAccent),
              _diagRow('HTTP Status', '${details['httpStatus']}', Colors.white),
              _diagRow('API Version', details['apiVersion'] ?? 'N/A', Colors.white),
              _diagRow('Python Version', details['pythonVersion'] ?? 'N/A', Colors.white70),
              _diagRow('Scanner Status', details['scannerStatus'] ?? 'N/A', Colors.greenAccent),
              const SizedBox(height: 12),
              const Text('Layer Diagnostics:', style: TextStyle(color: Colors.grey, fontSize: 12, fontWeight: FontWeight.bold)),
              const SizedBox(height: 6),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: diag.entries.map((e) {
                  final isPass = e.value.toString().contains('PASS') || e.value.toString().contains('200');
                  return Chip(
                    backgroundColor: isPass ? Colors.green.withValues(alpha: 0.2) : Colors.red.withValues(alpha: 0.2),
                    side: BorderSide(color: isPass ? Colors.greenAccent : Colors.redAccent),
                    label: Text(
                      '${e.key}: ${e.value}',
                      style: TextStyle(color: isPass ? Colors.greenAccent : Colors.redAccent, fontSize: 10),
                    ),
                  );
                }).toList(),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _diagRow(String label, String val, Color valColor) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
          Text(val, style: TextStyle(color: valColor, fontSize: 12, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ApiConfig.connectionState;
    Color statusColor = Colors.greenAccent;
    String statusText = 'ONLINE (${ApiConfig.serverType.toUpperCase()})';

    if (state == ServerConnectionState.local) {
      statusColor = Colors.cyanAccent;
      statusText = 'LOCAL MODE';
    } else if (state == ServerConnectionState.wakingServer) {
      statusColor = Colors.amberAccent;
      statusText = 'WAKING CLOUD SERVER';
    } else if (state == ServerConnectionState.offline) {
      statusColor = Colors.redAccent;
      statusText = 'OFFLINE';
    } else if (state == ServerConnectionState.checking || state == ServerConnectionState.connecting) {
      statusColor = Colors.orangeAccent;
      statusText = 'CONNECTING...';
    }

    return Scaffold(
      backgroundColor: const Color(0xFF0B0E14),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B0E14),
        title: const Text(
          'Enterprise Settings',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _sectionTitle('Live Server Connection & Health'),
          _buildCard([
            ListTile(
              leading: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: statusColor.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                ),
                child: Icon(Icons.dns, color: statusColor, size: 20),
              ),
              title: Row(
                children: [
                  Text(
                    statusText,
                    style: TextStyle(color: statusColor, fontSize: 13, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.white10,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '${ApiConfig.lastLatencyMs} ms',
                      style: const TextStyle(color: Colors.white70, fontSize: 10),
                    ),
                  ),
                ],
              ),
              subtitle: Text(
                ApiConfig.statusMessage,
                style: const TextStyle(color: Colors.grey, fontSize: 11),
              ),
              trailing: _isTesting
                  ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.cyanAccent))
                  : IconButton(
                      icon: const Icon(Icons.refresh, color: Colors.cyanAccent, size: 20),
                      onPressed: () async {
                        setState(() => _isTesting = true);
                        await ApiConfig.autoDiscoverReachableServer();
                        setState(() => _isTesting = false);
                      },
                    ),
            ),
            const Divider(color: Colors.white10, height: 1),
            Padding(
              padding: const EdgeInsets.all(12.0),
              child: Column(
                children: [
                  _diagRow('Active Base URL', ApiConfig.baseUrl, Colors.cyanAccent),
                  _diagRow('Server Type', ApiConfig.serverType, Colors.amberAccent),
                  _diagRow('Python Version', ApiConfig.pythonVersion, Colors.white70),
                  _diagRow('Market Status', ApiConfig.marketStatus, Colors.greenAccent),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(right: 12.0, bottom: 12.0, left: 12.0),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: _isTesting ? null : _runManualTest,
                      icon: const Icon(Icons.speed, size: 16),
                      label: const Text('Test Connection'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.cyanAccent,
                        side: const BorderSide(color: Colors.cyanAccent),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ]),
          const SizedBox(height: 16),

          _sectionTitle('API Endpoint & Server Network'),
          _buildCard([
            ListTile(
              title: const Text(
                'Active API Base URL',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                ),
              ),
              subtitle: Text(
                ApiConfig.baseUrl,
                style: const TextStyle(color: Colors.cyanAccent, fontSize: 11),
              ),
              trailing: const Icon(
                Icons.check_circle,
                color: Colors.greenAccent,
                size: 20,
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 16.0,
                vertical: 8.0,
              ),
              child: TextField(
                controller: _ipController,
                style: const TextStyle(color: Colors.white, fontSize: 13),
                decoration: const InputDecoration(
                  labelText: 'Custom Server URL / IP',
                  labelStyle: TextStyle(color: Colors.grey),
                  border: OutlineInputBorder(),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(right: 16.0, bottom: 8.0),
              child: Align(
                alignment: Alignment.centerRight,
                child: ElevatedButton.icon(
                  onPressed: _saveApiSettings,
                  icon: const Icon(Icons.save, size: 16),
                  label: const Text('Save & Reconnect'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blueAccent,
                  ),
                ),
              ),
            ),
          ]),
          const SizedBox(height: 16),

          _sectionTitle('Broker & Execution Pipeline'),
          _buildCard([
            ListTile(
              leading: const Icon(
                Icons.account_balance_wallet,
                color: Colors.amberAccent,
              ),
              title: const Text(
                'Paytm Money API v2 Engine',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                ),
              ),
              subtitle: const Text(
                'Connected & Authenticated (OAuth2 Active)',
                style: TextStyle(color: Colors.greenAccent, fontSize: 11),
              ),
              trailing: const Icon(Icons.chevron_right, color: Colors.grey),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const BrokerSettingsScreen(),
                  ),
                );
              },
            ),
          ]),
          const SizedBox(height: 16),

          _sectionTitle('Preferences & Notifications'),
          _buildCard([
            SwitchListTile(
              title: const Text(
                'Telegram Signals & Risk Alerts',
                style: TextStyle(color: Colors.white, fontSize: 13),
              ),
              subtitle: const Text(
                'Forward live A-Grade signals to Telegram Bot',
                style: TextStyle(color: Colors.grey, fontSize: 11),
              ),
              value: _telegramEnabled,
              onChanged: (val) => setState(() => _telegramEnabled = val),
            ),
            SwitchListTile(
              title: const Text(
                'Background Scanner Auto-Refresh',
                style: TextStyle(color: Colors.white, fontSize: 13),
              ),
              subtitle: const Text(
                'Auto-sync live market ticks every 60s',
                style: TextStyle(color: Colors.grey, fontSize: 11),
              ),
              value: _autoRefreshEnabled,
              onChanged: (val) => setState(() => _autoRefreshEnabled = val),
            ),
          ]),
          const SizedBox(height: 16),

          _sectionTitle('About RAHUUL_RADAR Enterprise'),
          _buildCard([
            const ListTile(
              leading: Icon(Icons.info_outline, color: Colors.blueAccent),
              title: Text(
                'Enterprise Release Version',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                ),
              ),
              subtitle: Text(
                'v6.5.7 Gold Master • Built for Multi-Tenant Quant Trading',
                style: TextStyle(color: Colors.grey, fontSize: 11),
              ),
            ),
          ]),
        ],
      ),
    );
  }

  Widget _sectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0, left: 4.0),
      child: Text(
        title,
        style: const TextStyle(
          color: Colors.grey,
          fontWeight: FontWeight.bold,
          fontSize: 12,
        ),
      ),
    );
  }

  Widget _buildCard(List<Widget> children) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(children: children),
    );
  }
}
