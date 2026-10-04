import 'package:json_annotation/json_annotation.dart';

part 'attendance_session.g.dart';

@JsonSerializable()
class AttendanceSession {
  const AttendanceSession({
    required this.id,
    required this.courseId,
    required this.courseName,
    required this.heldOn,
    required this.period,
  });

  final String id;
  final String courseId;
  final String courseName;
  final DateTime heldOn;
  final int period;

  factory AttendanceSession.fromJson(Map<String, dynamic> json) =>
      _$AttendanceSessionFromJson(json);

  Map<String, dynamic> toJson() => _$AttendanceSessionToJson(this);
}
