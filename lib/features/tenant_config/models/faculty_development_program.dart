class FacultyDevelopmentProgram {
  final String id;
  final String tenantId;
  final String collegeId;
  final String facultyId;
  final String title;
  final String? organizer;
  final String? programType;
  final String? mode;
  final String? venue;
  final String? startDate;
  final String? endDate;
  final double? durationHours;
  final String? certificateNumber;
  final String? certificateUrl;
  final String? description;

  const FacultyDevelopmentProgram({
    required this.id,
    required this.tenantId,
    required this.collegeId,
    required this.facultyId,
    required this.title,
    required this.organizer,
    required this.programType,
    required this.mode,
    required this.venue,
    required this.startDate,
    required this.endDate,
    required this.durationHours,
    required this.certificateNumber,
    required this.certificateUrl,
    required this.description,
  });

  factory FacultyDevelopmentProgram.fromJson(
    Map<String, dynamic> json,
  ) {
    return FacultyDevelopmentProgram(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      collegeId: json['college_id'] as String,
      facultyId: json['faculty_id'] as String,
      title: json['title'] as String,
      organizer: json['organizer'] as String?,
      programType: json['program_type'] as String?,
      mode: json['mode'] as String?,
      venue: json['venue'] as String?,
      startDate: json['start_date'] as String?,
      endDate: json['end_date'] as String?,
      durationHours:
          (json['duration_hours'] as num?)?.toDouble(),
      certificateNumber:
          json['certificate_number'] as String?,
      certificateUrl:
          json['certificate_url'] as String?,
      description:
          json['description'] as String?,
    );
  }
}