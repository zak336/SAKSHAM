class FacultyCourseAssignment {
  final String id;
  final String tenantId;
  final String collegeId;
  final String facultyId;
  final String courseId;
  final String academicYear;
  final int semester;
  final String? section;
  final String teachingRole;
  final String? assignedFrom;
  final String? assignedUntil;

  const FacultyCourseAssignment({
    required this.id,
    required this.tenantId,
    required this.collegeId,
    required this.facultyId,
    required this.courseId,
    required this.academicYear,
    required this.semester,
    required this.section,
    required this.teachingRole,
    required this.assignedFrom,
    required this.assignedUntil,
  });

  factory FacultyCourseAssignment.fromJson(
    Map<String, dynamic> json,
  ) {
    return FacultyCourseAssignment(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      collegeId: json['college_id'] as String,
      facultyId: json['faculty_id'] as String,
      courseId: json['course_id'] as String,
      academicYear: json['academic_year'] as String,
      semester: json['semester'] as int,
      section: json['section'] as String?,
      teachingRole:
          json['teaching_role'] as String,
      assignedFrom:
          json['assigned_from'] as String?,
      assignedUntil:
          json['assigned_until'] as String?,
    );
  }
}