// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'attendance_summary.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AttendanceSummary _$AttendanceSummaryFromJson(Map<String, dynamic> json) =>
    AttendanceSummary(
      courseId: json['course_id'] as String,
      courseName: json['course_name'] as String,
      totalSessions: (json['total_sessions'] as num).toInt(),
      attendedSessions: (json['attended_sessions'] as num).toInt(),
      percentage: (json['percentage'] as num).toDouble(),
      belowThreshold: json['below_threshold'] as bool,
    );

Map<String, dynamic> _$AttendanceSummaryToJson(AttendanceSummary instance) =>
    <String, dynamic>{
      'course_id': instance.courseId,
      'course_name': instance.courseName,
      'total_sessions': instance.totalSessions,
      'attended_sessions': instance.attendedSessions,
      'percentage': instance.percentage,
      'below_threshold': instance.belowThreshold,
    };
