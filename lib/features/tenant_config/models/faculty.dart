class Faculty {
  final String id;
  final String tenantId;
  final String collegeId;
  final String departmentId;
  final String userId;
  final String? designation;
  final String? qualification;
  final String? joiningDate;
  final String? researchInterests;
  final String? bio;

  const Faculty({
    required this.id,
    required this.tenantId,
    required this.collegeId,
    required this.departmentId,
    required this.userId,
    required this.designation,
    required this.qualification,
    required this.joiningDate,
    required this.researchInterests,
    required this.bio,
  });

  factory Faculty.fromJson(Map<String, dynamic> json) {
    return Faculty(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      collegeId: json['college_id'] as String,
      departmentId: json['department_id'] as String,
      userId: json['user_id'] as String,
      designation: json['designation'] as String?,
      qualification: json['qualification'] as String?,
      joiningDate: json['joining_date'] as String?,
      researchInterests:
          json['research_interests'] as String?,
      bio: json['bio'] as String?,
    );
  }
}