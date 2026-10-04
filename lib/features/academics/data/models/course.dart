import 'package:json_annotation/json_annotation.dart';

part 'course.g.dart';

@JsonSerializable()
class Course {
  const Course({
    required this.id,
    required this.tenantId,
    required this.departmentId,
    required this.name,
    required this.code,
    required this.semester,
    required this.credits,
    required this.isActive,
    this.facultyId,
  });

  final String id;

  @JsonKey(name: 'tenant_id')
  final String tenantId;

  @JsonKey(name: 'department_id')
  final String departmentId;

  @JsonKey(name: 'faculty_id')
  final String? facultyId;

  final String name;
  final String code;
  final int semester;
  final int credits;

  @JsonKey(name: 'is_active')
  final bool isActive;

  factory Course.fromJson(Map<String, dynamic> json) => _$CourseFromJson(json);

  Map<String, dynamic> toJson() => _$CourseToJson(this);
}
