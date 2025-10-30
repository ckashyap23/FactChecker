// Placeholder ChangeNotifier for loading/error/data state
import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../data/fact_api.dart';
import '../data/models.dart';

class FactController extends ChangeNotifier {
  final FactApi api;
  FactController(this.api);

  bool loading = false;
  String? error;
  List<FactResult> results = [];
  Uint8List? fileBytes;
  String? fileName;

  void setFile(Uint8List bytes, String name) {
    fileBytes = bytes;
    fileName = name;
    results = [];
    error = null;
    notifyListeners();
  }

  Future<void> runCheck() async {
    if (fileBytes == null) {
      error = 'Please select a CSV with a "statement" column.';
      notifyListeners();
      return;
    }
    loading = true; error = null; results = [];
    notifyListeners();
    try {
      results = await api.uploadCsv(fileBytes!, filename: fileName ?? 'statements.csv');
    } catch (e) {
      error = 'Failed: $e';
    } finally {
      loading = false;
      notifyListeners();
    }
  }
}


