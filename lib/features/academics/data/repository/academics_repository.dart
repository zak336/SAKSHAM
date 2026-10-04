import 'package:dio/dio.dart';

import '../models/course.dart';
import '../models/department.dart';
import '../models/student_profile.dart';

class AcademicsRepository {
  AcademicsRepository({required this.dio});

  final Dio dio;

  // ── Departments ────────────────────────────────────────────────────────────

  Future<List<Department>> getDepartments() async {
    final response = await dio.get<List<dynamic>>('/departments');
    return (response.data ?? [])
        .map((e) => Department.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Department> createDepartment({
    required String name,
    required String code,
  }) async {
    final response = await dio.post<Map<String, dynamic>>(
      '/departments',
      data: {'name': name, 'code': code},
    );
    return Department.fromJson(response.data!);
  }

  // ── Courses ────────────────────────────────────────────────────────────────

  Future<List<Course>> getCourses({
    String? departmentId,
    int? semester,
  }) async {
    final response = await dio.get<List<dynamic>>(
      '/courses',
      queryParameters: {
        'department_id': departmentId,
        'semester': semester,
      }..removeWhere((_, v) => v == null),
    );
    return (response.data ?? [])
        .map((e) => Course.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Course> createCourse({
    required String name,
    required String code,
    required String departmentId,
    required int semester,
    int credits = 3,
    String? facultyId,
  }) async {
    final response = await dio.post<Map<String, dynamic>>(
      '/courses',
      data: {
        'name': name,
        'code': code,
        'department_id': departmentId,
        'semester': semester,
        'credits': credits,
        'faculty_id': facultyId,
      }..removeWhere((_, v) => v == null),
    );
    return Course.fromJson(response.data!);
  }

  // ── Students ───────────────────────────────────────────────────────────────

  Future<List<StudentProfile>> getStudents({
    String? departmentId,
    int? semester,
    int? batchYear,
  }) async {
    final response = await dio.get<List<dynamic>>(
      '/students',
      queryParameters: {
        'department_id': departmentId,
        'semester': semester,
        'batch_year': batchYear,
      }..removeWhere((_, v) => v == null),
    );
    return (response.data ?? [])
        .map((e) => StudentProfile.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<StudentDetailProfile> getStudentDetail(String studentId) async {
    final response =
        await dio.get<Map<String, dynamic>>('/students/$studentId');
    return StudentDetailProfile.fromJson(response.data!);
  }

  Future<StudentDetailProfile> getMyStudentProfile() async {
    final response = await dio.get<Map<String, dynamic>>('/students/me');
    return StudentDetailProfile.fromJson(response.data!);
  }

  Future<StudentProfile> createStudent({
    required String userId,
    required String departmentId,
    required String rollNumber,
    required int batchYear,
    required int currentSemester,
  }) async {
    final response = await dio.post<Map<String, dynamic>>(
      '/students',
      data: {
        'user_id': userId,
        'department_id': departmentId,
        'roll_number': rollNumber,
        'batch_year': batchYear,
        'current_semester': currentSemester,
      },
    );
    return StudentProfile.fromJson(response.data!);
  }
}
