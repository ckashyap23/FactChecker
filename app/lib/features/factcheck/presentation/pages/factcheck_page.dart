// Placeholder for single-page UI
import 'package:flutter/material.dart';
import '../../data/fact_api.dart';
import '../../state/fact_controller.dart';
import '../widgets/file_picker_tile.dart';
import '../widgets/results_table.dart';

class FactCheckPage extends StatefulWidget {
  const FactCheckPage({super.key});
  @override
  State<FactCheckPage> createState() => _FactCheckPageState();
}

class _FactCheckPageState extends State<FactCheckPage> {
  late final controller = FactController(FactApi());

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        return Scaffold(
          appBar: AppBar(title: const Text('Fact Checker')),
          body: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                FilePickerTile(
                  onPicked: controller.setFile,
                  fileName: controller.fileName,
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    ElevatedButton.icon(
                      onPressed: controller.loading ? null : controller.runCheck,
                      icon: const Icon(Icons.check_circle),
                      label: const Text('Check facts'),
                    ),
                    const SizedBox(width: 12),
                    if (controller.loading) const CircularProgressIndicator(),
                    if (controller.error != null) ...[
                      const SizedBox(width: 12),
                      Text(controller.error!, style: const TextStyle(color: Colors.red)),
                    ],
                  ],
                ),
                const SizedBox(height: 16),
                Expanded(
                  child: controller.results.isEmpty
                      ? const Center(child: Text('Upload a CSV to see results'))
                      : ResultsTable(results: controller.results),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

