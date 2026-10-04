import 'package:json_annotation/json_annotation.dart';

part 'attendance_summary.g.dart';

@JsonSerializable()
class AttendanceSummary {
  const AttendanceSummary({
    required this.courseId,
    required this.courseName,
    required this.totalSessions,
    required this.attendedSessions,
    required this.percentage,
    required this.belowThreshold,
  });

  @JsonKey(name: 'course_id')
  final String courseId;
  @JsonKey(name: 'course_name')
  final String courseName;
  @JsonKey(name: 'total_sessions')
  final int totalSessions;
  @JsonKey(name: 'attended_sessions')
  final int attendedSessions;
  final double percentage;
  @JsonKey(name: 'below_threshold')
  final bool belowThreshold;

  factory AttendanceSummary.fromJson(Map<String, dynamic> json) =>
      _$AttendanceSummaryFromJson(json);

  Map<String, dynamic> toJson() => _$AttendanceSummaryToJson(this);
}
