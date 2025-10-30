// Placeholder main file for Flutter app
import 'package:flutter/material.dart';
import 'features/factcheck/presentation/pages/factcheck_page.dart';

void main() => runApp(const FactApp());

class FactApp extends StatelessWidget {
  const FactApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Fact Checker',
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.indigo),
      home: const FactCheckPage(),
    );
  }
}


