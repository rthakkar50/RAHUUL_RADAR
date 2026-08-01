class UserProfileModel {
  final String userId;
  final String name;
  final String email;
  final String photoUrl;
  final String planTier; // FREE, PRO, PRO+, ENTERPRISE
  final String activeDevice;
  final bool isCloudSyncEnabled;

  const UserProfileModel({
    required this.userId,
    required this.name,
    required this.email,
    required this.photoUrl,
    required this.planTier,
    required this.activeDevice,
    required this.isCloudSyncEnabled,
  });
}

class CloudBackupRecordModel {
  final String backupId;
  final String timestamp;
  final String deviceName;
  final String sizeKb;

  const CloudBackupRecordModel({
    required this.backupId,
    required this.timestamp,
    required this.deviceName,
    required this.sizeKb,
  });
}

class CloudWorkspaceRepository {
  static final CloudWorkspaceRepository _instance =
      CloudWorkspaceRepository._internal();
  factory CloudWorkspaceRepository() => _instance;
  CloudWorkspaceRepository._internal();

  UserProfileModel getCurrentUser() {
    return const UserProfileModel(
      userId: 'USR-884920',
      name: 'Rahuul Thakkar',
      email: 'rahuul@thakkar.com',
      photoUrl: 'https://rahuul-radar.com/avatar.png',
      planTier: 'ENTERPRISE PRO+',
      activeDevice: 'MacBook Pro & iPhone 15 Pro',
      isCloudSyncEnabled: true,
    );
  }

  List<CloudBackupRecordModel> getBackupHistory() {
    return const [
      CloudBackupRecordModel(
        backupId: 'BK-20260801-01',
        timestamp: '2026-08-01 17:45',
        deviceName: 'iPhone 15 Pro',
        sizeKb: '142 KB',
      ),
      CloudBackupRecordModel(
        backupId: 'BK-20260731-04',
        timestamp: '2026-07-31 23:10',
        deviceName: 'MacBook Pro',
        sizeKb: '138 KB',
      ),
    ];
  }

  List<String> getActiveDevices() {
    return const [
      'iPhone 15 Pro (Active - Current Device)',
      'MacBook Pro 16" (Active - Desktop Client)',
      'Chrome Web Terminal (Last seen 2h ago)',
    ];
  }
}
