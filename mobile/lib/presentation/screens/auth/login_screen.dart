import 'package:flutter/material.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _emailController = TextEditingController(text: 'rahuul@thakkar.com');
  final TextEditingController _passwordController = TextEditingController(text: '••••••••••••');
  bool _rememberDevice = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B0E14),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(colors: [Colors.cyanAccent, Colors.blueAccent]),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.radar, color: Colors.black, size: 40),
              ),
              const SizedBox(height: 16),
              const Text('RAHUUL_RADAR Enterprise', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 22)),
              const SizedBox(height: 6),
              const Text('Institutional SaaS & Cloud Workspace v4.0.0', style: TextStyle(color: Colors.grey, fontSize: 12)),
              const SizedBox(height: 32),
              TextField(
                controller: _emailController,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Email Address',
                  labelStyle: const TextStyle(color: Colors.grey),
                  filled: true,
                  fillColor: const Color(0xFF161B22),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                  prefixIcon: const Icon(Icons.email_outlined, color: Colors.cyanAccent),
                ),
              ),
              const SizedBox(height: 14),
              TextField(
                controller: _passwordController,
                obscureText: true,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: 'Password',
                  labelStyle: const TextStyle(color: Colors.grey),
                  filled: true,
                  fillColor: const Color(0xFF161B22),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                  prefixIcon: const Icon(Icons.lock_outline, color: Colors.cyanAccent),
                ),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Checkbox(
                    value: _rememberDevice,
                    onChanged: (val) => setState(() => _rememberDevice = val ?? true),
                    activeColor: Colors.cyanAccent,
                    checkColor: Colors.black,
                  ),
                  const Text('Remember This Device (JWT Encrypted)', style: TextStyle(color: Colors.white70, fontSize: 12)),
                ],
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () => Navigator.of(context).pop(),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.cyanAccent,
                  foregroundColor: Colors.black,
                  minimumSize: const Size(double.infinity, 48),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: const Text('AUTHENTICATE & LAUNCH WORKSPACE', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: () => Navigator.of(context).pop(),
                icon: const Icon(Icons.g_mobiledata, size: 24, color: Colors.white),
                label: const Text('Sign in with Google Enterprise SSO', style: TextStyle(color: Colors.white)),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 44),
                  side: const BorderSide(color: Colors.white24),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
