// Placeholder for result models
class FactResult {
  final String statement;
  final String verdict; // YES | NO | SKIPPED_SUBJECTIVE

  FactResult({required this.statement, required this.verdict});

  factory FactResult.fromJson(Map<String, dynamic> j) =>
      FactResult(statement: j['statement'] ?? '', verdict: j['verdict'] ?? '');
}

