import 'package:dio/dio.dart';

import '../models/attendance_summary.dart';

/// All attendance-related API calls.
class AttendanceRepository {
  AttendanceRepository({required this.dio});

  final Dio dio;

  Future<List<AttendanceSummary>> getAttendanceSummary({
    String? studentId,
    String? semester,
  }) async {
    final response = await dio.get(
      '/attendance/summary',
      queryParameters: {
        'student_id': studentId,
        'semester': semester,
      }..removeWhere((_, v) => v == null),
    );
    final data = response.data['data'] as List<dynamic>;
    return data
        .map((e) => AttendanceSummary.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
