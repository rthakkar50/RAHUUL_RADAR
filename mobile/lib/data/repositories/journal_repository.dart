import 'dart:convert';
import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../../core/network/api_config.dart';
import '../models/journal_model.dart';

class JournalRepository {
  Future<JournalResponseModel> getJournal({int limit = 100}) async {
    final journalUrl = '${ApiConfig.baseUrl}/journal?limit=$limit';
    debugPrint('[RUN-AUDIT] [JournalRepository] Calling URL: $journalUrl | Method: GET');
    debugPrint('[RUN-AUDIT] [JournalRepository] Timeout: ${ApiConfig.timeoutSeconds}s');

    try {
      final response = await http.get(
        Uri.parse(journalUrl),
        headers: ApiConfig.defaultHeaders(),
      ).timeout(const Duration(seconds: ApiConfig.timeoutSeconds));

      debugPrint('[RUN-AUDIT] [JournalRepository] HTTP Status Code: ${response.statusCode}');
      debugPrint('[RUN-AUDIT] [JournalRepository] Response Headers: ${response.headers}');
      debugPrint('[RUN-AUDIT] [JournalRepository] Response Body (first 300 chars): ${response.body.length > 300 ? response.body.substring(0, 300) : response.body}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        debugPrint('[RUN-AUDIT] [JournalRepository] Decoded JSON successfully. Key count: ${data.keys.length}');
        return JournalResponseModel.fromJson(data);
      } else {
        throw Exception('Failed to load journal. Status: ${response.statusCode}');
      }
    } on TimeoutException catch (e, st) {
      debugPrint('[RUN-AUDIT] [JournalRepository] TimeoutException caught: $e');
      debugPrint('[RUN-AUDIT] [JournalRepository] STACKTRACE:\n$st');
      throw Exception('Journal request timed out. Please check server status.');
    } catch (e, st) {
      debugPrint('[RUN-AUDIT] [JournalRepository] EXCEPTION CAUGHT: $e');
      debugPrint('[RUN-AUDIT] [JournalRepository] STACKTRACE:\n$st');
      throw Exception('Network error fetching journal: $e');
    }
  }
}
