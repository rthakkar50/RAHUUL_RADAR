import 'package:flutter/material.dart';
import '../../../core/network/api_config.dart';
import '../../../core/network/network_manager.dart';
import 'broker_settings_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final TextEditingController _ipController = TextEditingController(
    text: NetworkManager.instance.userSavedUrl,
  );
  final TextEditingController _portController = TextEditingController(
    text: '8000',
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
          content: Text('API Configuration Saved! Active Server: ${NetworkManager.instance.serverType} (${NetworkManager.instance.latencyMs}ms)'),
          backgroundColor: NetworkManager.instance.state == NetworkState.offline ? Colors.redAccent : Colors.green,
        ),
      );
    }
  }

  void _runManualTest() async {
    setState(() => _isTesting = true);
    final details = await NetworkManager.instance.runFullDiagnostics();
    setState(() => _isTesting = false);

    if (!mounted) return;

    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF161B22),
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        final diag = details['diagnostics'] as Map<String, dynamic>;
        return SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Network Diagnostics & Telemetry',
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
              _diagRow('Current URL', details['currentUrl'] ?? 'N/A', Colors.cyanAccent),
              _diagRow('Server Type', details['serverType'] ?? 'N/A', Colors.amberAccent),
              _diagRow('Discovery Source', details['discoverySource'] ?? 'N/A', Colors.blueAccent),
              _diagRow('Last Working URL', details['lastWorkingUrl'] ?? 'N/A', Colors.white70),
              _diagRow('Latency', '${details['latencyMs']} ms', Colors.greenAccent),
              _diagRow('HTTP Status', '${details['httpStatus']}', Colors.white),
              _diagRow('Python Version', details['pythonVersion'] ?? 'N/A', Colors.white70),
              _diagRow('Market Status', details['marketStatus'] ?? 'N/A', Colors.greenAccent),
              _diagRow('Failure Reason', details['failureReason'] ?? 'None', Colors.orangeAccent),
              const SizedBox(height: 12),
              const Text('Network Layer Checks:', style: TextStyle(color: Colors.grey, fontSize: 12, fontWeight: FontWeight.bold)),
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
          Flexible(
            child: Text(
              val,
              textAlign: TextAlign.right,
              style: TextStyle(color: valColor, fontSize: 12, fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = NetworkManager.instance.state;
    Color statusColor = Colors.greenAccent;
    String statusText = 'ONLINE (${NetworkManager.instance.serverType.toUpperCase()})';

    if (state == NetworkState.local) {
      statusColor = Colors.cyanAccent;
      statusText = 'LOCAL MODE';
    } else if (state == NetworkState.render) {
      statusColor = Colors.amberAccent;
      statusText = 'RENDER CLOUD';
    } else if (state == NetworkState.tunnel) {
      statusColor = Colors.purpleAccent;
      statusText = 'DYNAMIC TUNNEL';
    } else if (state == NetworkState.offline || state == NetworkState.error) {
      statusColor = Colors.redAccent;
      statusText = 'OFFLINE';
    } else if (state == NetworkState.checking || state == NetworkState.discovering || state == NetworkState.connecting) {
      statusColor = Colors.orangeAccent;
      statusText = 'DISCOVERING...';
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
          _sectionTitle('Enterprise Network Manager Status'),
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
                      '${NetworkManager.instance.latencyMs} ms',
                      style: const TextStyle(color: Colors.white70, fontSize: 10),
                    ),
                  ),
                ],
              ),
              subtitle: Text(
                'Source: ${NetworkManager.instance.discoverySource}',
                style: const TextStyle(color: Colors.grey, fontSize: 11),
              ),
              trailing: _isTesting
                  ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.cyanAccent))
                  : IconButton(
                      icon: const Icon(Icons.refresh, color: Colors.cyanAccent, size: 20),
                      onPressed: () async {
                        setState(() => _isTesting = true);
                        await NetworkManager.instance.startPlatformAwareDiscovery();
                        setState(() => _isTesting = false);
                      },
                    ),
            ),
            const Divider(color: Colors.white10, height: 1),
            Padding(
              padding: const EdgeInsets.all(12.0),
              child: Column(
                children: [
                  _diagRow('Active Base URL', NetworkManager.instance.baseUrl, Colors.cyanAccent),
                  _diagRow('Last Working URL', NetworkManager.instance.lastWorkingUrl, Colors.white70),
                  _diagRow('Server Type', NetworkManager.instance.serverType, Colors.amberAccent),
                  _diagRow('Python Version', NetworkManager.instance.pythonVersion, Colors.white70),
                  _diagRow('Market Status', NetworkManager.instance.marketStatus, Colors.greenAccent),
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
                      label: const Text('Test Connection & Diagnostics'),
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

          _sectionTitle('API Endpoint Configuration'),
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
                NetworkManager.instance.baseUrl,
                style: const TextStyle(color: Colors.cyanAccent, fontSize: 11),
              ),
              trailing: const Icon(
                Icons.check_circle,
                color: Colors.greenAccent,
                size: 20,
              ),
            ),
            if (!NetworkManager.instance.isProduction()) ...[
              Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16.0,
                  vertical: 8.0,
                ),
                child: TextField(
                  controller: _ipController,
                  style: const TextStyle(color: Colors.white, fontSize: 13),
                  decoration: const InputDecoration(
                    labelText: 'Custom Server / Tunnel URL',
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
                    label: const Text('Save & Discover'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blueAccent,
                    ),
                  ),
                ),
              ),
            ],
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
                'v6.6.0 Enterprise Master • Platform-Aware Network Architecture',
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
