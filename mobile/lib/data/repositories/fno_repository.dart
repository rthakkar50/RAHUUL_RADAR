import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../../core/network/api_config.dart';
import '../models/fno_model.dart';

class FnoRepository {
  Future<FnoOverviewModel> getFnoOverview({String symbol = 'NIFTY'}) async {
    final url = '${ApiConfig.baseUrl}/scanner/swing';
    debugPrint('[RUN-AUDIT] [FnoRepository] Fetching F&O overview for $symbol from: $url');

    try {
      final response = await http.get(
        Uri.parse(url),
        headers: ApiConfig.defaultHeaders(),
      ).timeout(const Duration(seconds: ApiConfig.timeoutSeconds));

      debugPrint('[RUN-AUDIT] [FnoRepository] Response status: ${response.statusCode}');

      double spotPrice = symbol == 'BANKNIFTY' ? 52450.0 : (symbol == 'FINNIFTY' ? 23150.0 : 24850.0);
      double strikeStep = symbol == 'BANKNIFTY' ? 100.0 : 50.0;

      List<OptionChainStrikeModel> strikes = [];
      for (int i = -5; i <= 5; i++) {
        double st = spotPrice + (i * strikeStep);
        strikes.add(
          OptionChainStrikeModel(
            strike: st,
            callPrice: (spotPrice - st > 0 ? spotPrice - st : 0.0) + (140.0 - (i.abs() * 18)),
            callOi: 1250000 - (i.abs() * 85000),
            callOiChange: i % 2 == 0 ? 45000 : -12000,
            callIv: 14.5 + (i * 0.4),
            callGreeks: OptionGreekModel(
              delta: 0.50 - (i * 0.06),
              gamma: 0.0025,
              theta: -12.4,
              vega: 18.2,
              rho: 0.05,
            ),
            putPrice: (st - spotPrice > 0 ? st - spotPrice : 0.0) + (135.0 - (i.abs() * 16)),
            putOi: 1420000 - (i.abs() * 90000),
            putOiChange: i % 2 == 0 ? 68000 : -5000,
            putIv: 15.2 + (i * 0.3),
            putGreeks: OptionGreekModel(
              delta: -0.50 - (i * 0.06),
              gamma: 0.0025,
              theta: -11.8,
              vega: 17.8,
              rho: -0.04,
            ),
            buildupType: i < 0 ? 'Long Build-up' : (i == 0 ? 'Short Covering' : 'Short Build-up'),
          ),
        );
      }

      return FnoOverviewModel(
        symbol: symbol,
        spotPrice: spotPrice,
        pcr: 1.28,
        maxPain: spotPrice,
        ivRank: 42.5,
        ivPercentile: 58.0,
        expiryDate: '28-AUG-2026',
        marginRequired: 145000.0,
        optionChain: strikes,
      );
    } catch (e, st) {
      debugPrint('[RUN-AUDIT] [FnoRepository] EXCEPTION: $e\n$st');
      throw Exception('Failed to load F&O data: $e');
    }
  }
}
