class MoocCompletion {
  final String id;
  final String tenantId;
  final String collegeId;
  final String userId;
  final String courseTitle;
  final String? provider;
  final String? platform;
  final String? courseIdentifier;
  final double? durationHours;
  final String? enrolledOn;
  final String? completedOn;
  final String? certificateId;
  final String? certificateUrl;
  final double? score;
  final String status;
  final String? description;

  const MoocCompletion({
    required this.id,
    required this.tenantId,
    required this.collegeId,
    required this.userId,
    required this.courseTitle,
    required this.provider,
    required this.platform,
    required this.courseIdentifier,
    required this.durationHours,
    required this.enrolledOn,
    required this.completedOn,
    required this.certificateId,
    required this.certificateUrl,
    required this.score,
    required this.status,
    required this.description,
  });

  factory MoocCompletion.fromJson(
    Map<String, dynamic> json,
  ) {
    return MoocCompletion(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      collegeId: json['college_id'] as String,
      userId: json['user_id'] as String,
      courseTitle: json['course_title'] as String,
      provider: json['provider'] as String?,
      platform: json['platform'] as String?,
      courseIdentifier:
          json['course_identifier'] as String?,
      durationHours:
          (json['duration_hours'] as num?)?.toDouble(),
      enrolledOn:
          json['enrolled_on'] as String?,
      completedOn:
          json['completed_on'] as String?,
      certificateId:
          json['certificate_id'] as String?,
      certificateUrl:
          json['certificate_url'] as String?,
      score:
          (json['score'] as num?)?.toDouble(),
      status: json['status'] as String,
      description:
          json['description'] as String?,
    );
  }
}