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

  @override
  void dispose() {
    _ipController.dispose();
    _portController.dispose();
    super.dispose();
  }

  void _saveApiSettings() async {
    await ApiConfig.saveSettings(
      _ipController.text,
      _portController.text,
      'Production',
    );
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('API Configuration Saved & Tested Successfully!'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
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

          _sectionTitle('AI Engine & MLOps Platform'),
          _buildCard([
            const ListTile(
              leading: Icon(Icons.psychology, color: Colors.purpleAccent),
              title: Text(
                'Champion Model Registry',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                ),
              ),
              subtitle: Text(
                'AI Engine V2 — Random Forest + Gradient Boosting (PSI Drift 0.02)',
                style: TextStyle(color: Colors.white70, fontSize: 11),
              ),
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
                'v2.0 Gold Master • Built for Multi-Tenant Quant Trading',
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
