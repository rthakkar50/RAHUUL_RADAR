import 'package:flutter/material.dart';
import '../../../core/network/api_config.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _ipController = TextEditingController();
  final _portController = TextEditingController();
  String _selectedEnv = 'Production';

  final List<String> _environments = ['Development', 'Staging', 'Production'];

  @override
  void initState() {
    super.initState();
    _ipController.text = ApiConfig.localIp;
    _portController.text = ApiConfig.port;
    _selectedEnv = ApiConfig.env;
  }

  @override
  void dispose() {
    _ipController.dispose();
    _portController.dispose();
    super.dispose();
  }

  Future<void> _saveSettings() async {
    await ApiConfig.saveSettings(
      _ipController.text.trim(),
      _portController.text.trim(),
      _selectedEnv,
    );
    
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('API Settings Saved Successfully'),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  void _applyPreset(String ip, String port) {
    setState(() {
      _ipController.text = ip;
      _portController.text = port;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('API Settings'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Environment',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              initialValue: _selectedEnv,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                filled: true,
              ),
              items: _environments.map((env) {
                return DropdownMenuItem(value: env, child: Text(env));
              }).toList(),
              onChanged: (val) {
                if (val != null) setState(() => _selectedEnv = val);
              },
            ),
            const SizedBox(height: 24),
            const Text(
              'Server Configuration',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _ipController,
              decoration: const InputDecoration(
                labelText: 'IP Address / Domain',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.computer),
              ),
              keyboardType: TextInputType.url,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _portController,
              decoration: const InputDecoration(
                labelText: 'Port',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.settings_ethernet),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 24),
            const Text(
              'Quick Presets',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8.0,
              children: [
                ActionChip(
                  label: const Text('Production VM (Oracle)'),
                  onPressed: () => _applyPreset('137.23.34.223', '8000'),
                ),
                ActionChip(
                  label: const Text('Android Emulator'),
                  onPressed: () => _applyPreset('10.0.2.2', '8000'),
                ),
                ActionChip(
                  label: const Text('iOS Simulator / Local'),
                  onPressed: () => _applyPreset('127.0.0.1', '8000'),
                ),
                ActionChip(
                  label: const Text('Physical Device (LAN)'),
                  onPressed: () => _applyPreset('192.168.1.100', '8000'),
                ),
              ],
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _saveSettings,
                child: const Text('Save Settings', style: TextStyle(fontSize: 16)),
              ),
            ),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blueAccent.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.blueAccent),
              ),
              child: const Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.blueAccent),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Changes apply immediately on the next API call. You do not need to restart the app.',
                      style: TextStyle(fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
