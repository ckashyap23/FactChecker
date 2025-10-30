// Placeholder for results table
import 'package:flutter/material.dart';
import '../../data/models.dart';

class ResultsTable extends StatelessWidget {
  final List<FactResult> results;
  const ResultsTable({super.key, required this.results});

  Color _chipColor(String v) => switch (v) {
        'YES' => const Color(0xFF388E3C), // green.shade700
        'NO' => const Color(0xFFD32F2F), // red.shade700
        'SKIPPED_SUBJECTIVE' => const Color(0xFFF57C00), // orange.shade700
        _ => const Color(0xFF616161), // grey.shade700
      };

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.vertical,
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Statement')),
          DataColumn(label: Text('Verdict')),
        ],
        rows: results
            .map((r) => DataRow(cells: [
                  DataCell(SelectableText(r.statement)),
                  DataCell(Chip(
                    label: Text(r.verdict),
                    backgroundColor: _chipColor(r.verdict).withOpacity(0.15),
                    labelStyle: TextStyle(
                      color: _chipColor(r.verdict),
                      fontWeight: FontWeight.w600,
                    ),
                  )),
                ]))
            .toList(),
      ),
    );
  }
}


