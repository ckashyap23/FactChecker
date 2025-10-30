// Placeholder for HTTP client (upload CSV)
import 'dart:typed_data';
import 'package:dio/dio.dart';
import '../../../core/constants.dart';
import 'models.dart';

class FactApi {
  final Dio _dio = Dio(BaseOptions(baseUrl: kApiBase));

  Future<List<FactResult>> uploadCsv(
    Uint8List bytes, {
    String filename = 'statements.csv',
  }) async {
    final form = FormData.fromMap({
      'file': MultipartFile.fromBytes(bytes, filename: filename),
    });
    final r = await _dio.post('/factcheck/upload', data: form);
    final list = (r.data['results'] as List).cast<Map<String, dynamic>>();
    return list.map(FactResult.fromJson).toList();
  }
}


