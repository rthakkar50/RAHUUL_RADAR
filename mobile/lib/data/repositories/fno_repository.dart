import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../../core/network/api_config.dart';
import '../models/fno_model.dart';

class FnoRepository {
  Future<FnoOverviewModel> getFnoOverview({String symbol = 'NIFTY'}) async {
    final url = '${ApiConfig.baseUrl}/fno/option-chain?symbol=$symbol';
    debugPrint('[RUN-AUDIT] [FnoRepository] Fetching live option chain for $symbol from: $url');

    try {
      final response = await http
          .get(Uri.parse(url), headers: ApiConfig.defaultHeaders())
          .timeout(const Duration(seconds: ApiConfig.timeoutSeconds));

      debugPrint('[RUN-AUDIT] [FnoRepository] Response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);

        final rawStrikes = data['strikes'] as List<dynamic>? ?? [];
        final List<OptionChainStrikeModel> strikes = [];

        for (var item in rawStrikes) {
          if (item is Map<String, dynamic>) {
            final st = (item['strike'] as num?)?.toDouble() ?? 0.0;
            final callOiChgStr = item['callOiChange']?.toString() ?? '0';
            final putOiChgStr = item['putOiChange']?.toString() ?? '0';
            final callOiChgVal = double.tryParse(callOiChgStr.replaceAll(',', '').replaceAll('+', '')) ?? 0.0;
            final putOiChgVal = double.tryParse(putOiChgStr.replaceAll(',', '').replaceAll('+', '')) ?? 0.0;

            strikes.add(
              OptionChainStrikeModel(
                strike: st,
                callPrice: (item['callLtp'] as num?)?.toDouble() ?? 0.0,
                callOi: (item['callOi'] as num?)?.toDouble() ?? 0.0,
                callOiChange: callOiChgVal,
                callIv: (item['callIv'] as num?)?.toDouble() ?? 14.0,
                callGreeks: OptionGreekModel(
                  delta: (item['callDelta'] as num?)?.toDouble() ?? 0.50,
                  gamma: (item['callGamma'] as num?)?.toDouble() ?? 0.0024,
                  theta: (item['callTheta'] as num?)?.toDouble() ?? -12.4,
                  vega: (item['callVega'] as num?)?.toDouble() ?? 18.5,
                  rho: 0.05,
                ),
                putPrice: (item['putLtp'] as num?)?.toDouble() ?? 0.0,
                putOi: (item['putOi'] as num?)?.toDouble() ?? 0.0,
                putOiChange: putOiChgVal,
                putIv: (item['putIv'] as num?)?.toDouble() ?? 14.0,
                putGreeks: OptionGreekModel(
                  delta: (item['putDelta'] as num?)?.toDouble() ?? -0.50,
                  gamma: (item['putGamma'] as num?)?.toDouble() ?? 0.0024,
                  theta: (item['putTheta'] as num?)?.toDouble() ?? -11.8,
                  vega: (item['putVega'] as num?)?.toDouble() ?? 18.2,
                  rho: -0.04,
                ),
                buildupType: item['isAtm'] == true ? 'Short Covering' : 'Long Build-up',
              ),
            );
          }
        }

        return FnoOverviewModel(
          symbol: data['underlying'] ?? symbol,
          spotPrice: (data['spotPrice'] as num?)?.toDouble() ?? 24850.0,
          pcr: (data['pcr'] as num?)?.toDouble() ?? 1.28,
          maxPain: (data['maxPain'] as num?)?.toDouble() ?? 24850.0,
          ivRank: (data['ivRank'] as num?)?.toDouble() ?? 34.2,
          ivPercentile: (data['ivPercentile'] as num?)?.toDouble() ?? 41.5,
          expiryDate: data['expiry'] ?? '28-AUG-2026',
          marginRequired: (data['marginRequirement'] as num?)?.toDouble() ?? 125000.0,
          optionChain: strikes,
        );
      }
    } catch (e, st) {
      debugPrint('[RUN-AUDIT] [FnoRepository] EXCEPTION: $e\n$st');
    }

    // Clean Empty State model if feed unavailable
    return FnoOverviewModel(
      symbol: symbol,
      spotPrice: 0.0,
      pcr: 0.0,
      maxPain: 0.0,
      ivRank: 0.0,
      ivPercentile: 0.0,
      expiryDate: 'N/A',
      marginRequired: 0.0,
      optionChain: [],
    );
  }
}
