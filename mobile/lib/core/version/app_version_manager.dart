import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../network/api_config.dart';

class AppVersionModel {
  final String appName;
  final String currentVersion;
  final String minimumSupportedVersion;
  final int buildNumber;
  final String releaseDate;
  final bool updateAvailable;
  final bool forceUpdate;
  final List<String> releaseNotes;
  final String downloadUrlAndroid;
  final String downloadUrlIos;

  const AppVersionModel({
    required this.appName,
    required this.currentVersion,
    required this.minimumSupportedVersion,
    required this.buildNumber,
    required this.releaseDate,
    required this.updateAvailable,
    required this.forceUpdate,
    required this.releaseNotes,
    required this.downloadUrlAndroid,
    required this.downloadUrlIos,
  });

  factory AppVersionModel.fromJson(Map<String, dynamic> json) {
    final rawNotes = json['release_notes'] as List<dynamic>? ?? [];
    final notes = rawNotes.map((e) => e.toString()).toList();

    return AppVersionModel(
      appName: json['app_name'] ?? 'RAHUUL_RADAR',
      currentVersion: json['current_version'] ?? '1.0.0',
      minimumSupportedVersion: json['minimum_supported_version'] ?? '1.0.0',
      buildNumber: (json['build_number'] as num?)?.toInt() ?? 100,
      releaseDate: json['release_date'] ?? '2026-08-05',
      updateAvailable: json['update_available'] == true,
      forceUpdate: json['force_update'] == true,
      releaseNotes: notes,
      downloadUrlAndroid: json['download_url_android'] ?? '',
      downloadUrlIos: json['download_url_ios'] ?? '',
    );
  }
}

class AppVersionManager {
  static final AppVersionManager _instance = AppVersionManager._internal();
  static AppVersionManager get instance => _instance;
  AppVersionManager._internal();

  static const String installedVersion = '1.0.0';
  static const int installedBuildNumber = 100;

  Future<AppVersionModel?> checkAppVersion() async {
    final url = '${ApiConfig.baseUrl}/version';
    debugPrint('[RUN-AUDIT] [AppVersionManager] Checking app version from: $url');

    try {
      final response = await http
          .get(Uri.parse(url), headers: ApiConfig.defaultHeaders())
          .timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        final model = AppVersionModel.fromJson(data);
        debugPrint('[RUN-AUDIT] [AppVersionManager] Server version: ${model.currentVersion}, Update available: ${model.updateAvailable}');
        return model;
      }
    } catch (e) {
      debugPrint('[RUN-AUDIT] [AppVersionManager] Non-blocking version check exception: $e');
    }
    return null;
  }

  void promptUpdateIfAvailable(BuildContext context, AppVersionModel versionModel) {
    if (!versionModel.updateAvailable && !versionModel.forceUpdate) return;

    showDialog(
      context: context,
      barrierDismissible: !versionModel.forceUpdate,
      builder: (ctx) => PopScope(
        canPop: !versionModel.forceUpdate,
        child: AlertDialog(
          backgroundColor: const Color(0xFF161B22),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: BorderSide(
              color: versionModel.forceUpdate ? Colors.redAccent : Colors.cyanAccent,
            ),
          ),
          title: Row(
            children: [
              Icon(
                versionModel.forceUpdate ? Icons.system_update_sharp : Icons.new_releases,
                color: versionModel.forceUpdate ? Colors.redAccent : Colors.cyanAccent,
              ),
              const SizedBox(width: 8),
              Text(
                versionModel.forceUpdate ? 'Mandatory Update Required' : 'New Version Available (${versionModel.currentVersion})',
                style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Release Notes (${versionModel.releaseDate}):',
                style: const TextStyle(color: Colors.white70, fontWeight: FontWeight.bold, fontSize: 12),
              ),
              const SizedBox(height: 6),
              ...versionModel.releaseNotes.map(
                (note) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 2),
                  child: Text('• $note', style: const TextStyle(color: Colors.white60, fontSize: 11)),
                ),
              ),
              if (versionModel.forceUpdate) ...[
                const SizedBox(height: 12),
                const Text(
                  'Your installed version is no longer supported. Please update to continue using RAHUUL_RADAR.',
                  style: TextStyle(color: Colors.redAccent, fontSize: 11, fontWeight: FontWeight.bold),
                ),
              ],
            ],
          ),
          actions: [
            if (!versionModel.forceUpdate)
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Later', style: TextStyle(color: Colors.grey)),
              ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: versionModel.forceUpdate ? Colors.redAccent : Colors.cyanAccent,
              ),
              onPressed: () {
                Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      'Redirecting to download package: ${Theme.of(context).platform == TargetPlatform.iOS ? versionModel.downloadUrlIos : versionModel.downloadUrlAndroid}',
                    ),
                  ),
                );
              },
              child: Text(
                'Update Now',
                style: TextStyle(color: versionModel.forceUpdate ? Colors.white : Colors.black, fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
