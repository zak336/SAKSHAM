import 'package:json_annotation/json_annotation.dart';

part 'student_profile.g.dart';

@JsonSerializable()
class StudentProfile {
  const StudentProfile({
    required this.id,
    required this.tenantId,
    required this.userId,
    required this.departmentId,
    required this.rollNumber,
    required this.batchYear,
    required this.currentSemester,
  });

  final String id;

  @JsonKey(name: 'tenant_id')
  final String tenantId;

  @JsonKey(name: 'user_id')
  final String userId;

  @JsonKey(name: 'department_id')
  final String departmentId;

  @JsonKey(name: 'roll_number')
  final String rollNumber;

  @JsonKey(name: 'batch_year')
  final int batchYear;

  @JsonKey(name: 'current_semester')
  final int currentSemester;

  factory StudentProfile.fromJson(Map<String, dynamic> json) =>
      _$StudentProfileFromJson(json);

  Map<String, dynamic> toJson() => _$StudentProfileToJson(this);
}

@JsonSerializable()
class StudentDetailProfile extends StudentProfile {
  const StudentDetailProfile({
    required super.id,
    required super.tenantId,
    required super.userId,
    required super.departmentId,
    required super.rollNumber,
    required super.batchYear,
    required super.currentSemester,
    required this.studentName,
    required this.email,
    required this.departmentName,
    required this.departmentCode,
  });

  @JsonKey(name: 'student_name')
  final String studentName;

  final String email;

  @JsonKey(name: 'department_name')
  final String departmentName;

  @JsonKey(name: 'department_code')
  final String departmentCode;

  factory StudentDetailProfile.fromJson(Map<String, dynamic> json) =>
      _$StudentDetailProfileFromJson(json);

  @override
  Map<String, dynamic> toJson() => _$StudentDetailProfileToJson(this);
}
