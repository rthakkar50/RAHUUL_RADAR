import 'package:flutter/material.dart';
import '../../../data/repositories/cloud_workspace_repository.dart';

class UserProfileScreen extends StatefulWidget {
  const UserProfileScreen({super.key});

  @override
  State<UserProfileScreen> createState() => _UserProfileScreenState();
}

class _UserProfileScreenState extends State<UserProfileScreen> with SingleTickerProviderStateMixin {
  final CloudWorkspaceRepository _repo = CloudWorkspaceRepository();
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
    final user = _repo.getCurrentUser();
    final backups = _repo.getBackupHistory();
    final devices = _repo.getActiveDevices();

    return Scaffold(
      backgroundColor: const Color(0xFF0B0E14),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B0E14),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Colors.cyanAccent, Colors.blueAccent]),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.cloud_done, color: Colors.black, size: 18),
            ),
            const SizedBox(width: 8),
            const Text('Cloud Workspace & Profile Hub', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17)),
          ],
        ),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Profile'),
            Tab(text: 'Devices'),
            Tab(text: 'Backup'),
            Tab(text: 'License'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildProfileTab(user),
          _buildDevicesTab(devices),
          _buildBackupTab(backups),
          _buildLicenseTab(user),
        ],
      ),
    );
  }

  Widget _buildProfileTab(UserProfileModel user) {
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
          child: Row(
            children: [
              const CircleAvatar(
                radius: 28,
                backgroundColor: Colors.cyanAccent,
                child: Icon(Icons.person, color: Colors.black, size: 32),
              ),
              const SizedBox(width: 14),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(user.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                  Text(user.email, style: const TextStyle(color: Colors.grey, fontSize: 12)),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(color: Colors.purpleAccent.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(4)),
                    child: Text(user.planTier, style: const TextStyle(color: Colors.purpleAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDevicesTab(List<String> devices) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: devices.length,
      itemBuilder: (ctx, i) {
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 10),
          child: ListTile(
            leading: const Icon(Icons.devices, color: Colors.cyanAccent),
            title: Text(devices[i], style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
          ),
        );
      },
    );
  }

  Widget _buildBackupTab(List<CloudBackupRecordModel> backups) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: backups.length,
      itemBuilder: (ctx, i) {
        final bk = backups[i];
        return Card(
          color: const Color(0xFF161B22),
          margin: const EdgeInsets.only(bottom: 10),
          child: ListTile(
            title: Text('${bk.backupId} (${bk.sizeKb})', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
            subtitle: Text('Device: ${bk.deviceName} • Saved: ${bk.timestamp}', style: const TextStyle(color: Colors.grey, fontSize: 11)),
            trailing: const Icon(Icons.cloud_download_outlined, color: Colors.greenAccent),
          ),
        );
      },
    );
  }

  Widget _buildLicenseTab(UserProfileModel user) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF161B22),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Colors.purpleAccent.withValues(alpha: 0.4)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Module 6 — Active License: ${user.planTier}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
              const SizedBox(height: 10),
              const Text(
                '• Unlimited Multi-Broker Connections.\n'
                '• AI Master Decision Engine AMD v1 Enabled.\n'
                '• Real-time Encrypted Cloud Sync across 5 devices.\n'
                '• 24/7 Priority SLA & Dedicated Cloud Instance.',
                style: TextStyle(color: Colors.white70, fontSize: 12, height: 1.4),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
