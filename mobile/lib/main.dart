import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';
import 'presentation/screens/splash/splash_screen.dart';
import 'core/network/api_config.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await ApiConfig.init();
  runApp(const RahuulRadarApp());
}

class RahuulRadarApp extends StatelessWidget {
  const RahuulRadarApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Rahuul Radar',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const SplashScreen(),
    );
  }
}
