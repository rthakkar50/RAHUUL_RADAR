import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;
import '../../core/network/api_config.dart';
import '../models/journal_model.dart';

class JournalRepository {
  Future<JournalResponseModel> getJournal({int limit = 100}) async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}/journal?limit=$limit'),
      ).timeout(const Duration(seconds: ApiConfig.timeoutSeconds));

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        return JournalResponseModel.fromJson(data);
      } else {
        throw Exception('Failed to load journal. Status: ${response.statusCode}');
      }
    } on TimeoutException {
      throw Exception('Journal request timed out. Please check server status.');
    } catch (e) {
      throw Exception('Network error fetching journal: $e');
    }
  }
}
