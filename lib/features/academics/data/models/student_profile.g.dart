// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'student_profile.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StudentProfile _$StudentProfileFromJson(Map<String, dynamic> json) =>
    StudentProfile(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      userId: json['user_id'] as String,
      departmentId: json['department_id'] as String,
      rollNumber: json['roll_number'] as String,
      batchYear: (json['batch_year'] as num).toInt(),
      currentSemester: (json['current_semester'] as num).toInt(),
    );

Map<String, dynamic> _$StudentProfileToJson(StudentProfile instance) =>
    <String, dynamic>{
      'id': instance.id,
      'tenant_id': instance.tenantId,
      'user_id': instance.userId,
      'department_id': instance.departmentId,
      'roll_number': instance.rollNumber,
      'batch_year': instance.batchYear,
      'current_semester': instance.currentSemester,
    };

StudentDetailProfile _$StudentDetailProfileFromJson(
  Map<String, dynamic> json,
) => StudentDetailProfile(
  id: json['id'] as String,
  tenantId: json['tenant_id'] as String,
  userId: json['user_id'] as String,
  departmentId: json['department_id'] as String,
  rollNumber: json['roll_number'] as String,
  batchYear: (json['batch_year'] as num).toInt(),
  currentSemester: (json['current_semester'] as num).toInt(),
  studentName: json['student_name'] as String,
  email: json['email'] as String,
  departmentName: json['department_name'] as String,
  departmentCode: json['department_code'] as String,
);

Map<String, dynamic> _$StudentDetailProfileToJson(
  StudentDetailProfile instance,
) => <String, dynamic>{
  'id': instance.id,
  'tenant_id': instance.tenantId,
  'user_id': instance.userId,
  'department_id': instance.departmentId,
  'roll_number': instance.rollNumber,
  'batch_year': instance.batchYear,
  'current_semester': instance.currentSemester,
  'student_name': instance.studentName,
  'email': instance.email,
  'department_name': instance.departmentName,
  'department_code': instance.departmentCode,
};
