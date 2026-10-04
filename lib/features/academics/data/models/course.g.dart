// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'course.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Course _$CourseFromJson(Map<String, dynamic> json) => Course(
  id: json['id'] as String,
  tenantId: json['tenant_id'] as String,
  departmentId: json['department_id'] as String,
  name: json['name'] as String,
  code: json['code'] as String,
  semester: (json['semester'] as num).toInt(),
  credits: (json['credits'] as num).toInt(),
  isActive: json['is_active'] as bool,
  facultyId: json['faculty_id'] as String?,
);

Map<String, dynamic> _$CourseToJson(Course instance) => <String, dynamic>{
  'id': instance.id,
  'tenant_id': instance.tenantId,
  'department_id': instance.departmentId,
  'faculty_id': instance.facultyId,
  'name': instance.name,
  'code': instance.code,
  'semester': instance.semester,
  'credits': instance.credits,
  'is_active': instance.isActive,
};
