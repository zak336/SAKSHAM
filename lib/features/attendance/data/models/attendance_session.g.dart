// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'attendance_session.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AttendanceSession _$AttendanceSessionFromJson(Map<String, dynamic> json) =>
    AttendanceSession(
      id: json['id'] as String,
      courseId: json['courseId'] as String,
      courseName: json['courseName'] as String,
      heldOn: DateTime.parse(json['heldOn'] as String),
      period: (json['period'] as num).toInt(),
    );

Map<String, dynamic> _$AttendanceSessionToJson(AttendanceSession instance) =>
    <String, dynamic>{
      'id': instance.id,
      'courseId': instance.courseId,
      'courseName': instance.courseName,
      'heldOn': instance.heldOn.toIso8601String(),
      'period': instance.period,
    };
