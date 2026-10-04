class Achievement {
  final String id;
  final String tenantId;
  final String collegeId;
  final String facultyId;
  final String title;
  final String category;
  final String? description;
  final String? issuingOrganization;
  final String? achievementDate;
  final String? referenceUrl;

  const Achievement({
    required this.id,
    required this.tenantId,
    required this.collegeId,
    required this.facultyId,
    required this.title,
    required this.category,
    required this.description,
    required this.issuingOrganization,
    required this.achievementDate,
    required this.referenceUrl,
  });

  factory Achievement.fromJson(Map<String, dynamic> json) {
    return Achievement(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      collegeId: json['college_id'] as String,
      facultyId: json['faculty_id'] as String,
      title: json['title'] as String,
      category: json['category'] as String,
      description: json['description'] as String?,
      issuingOrganization:
          json['issuing_organization'] as String?,
      achievementDate:
          json['achievement_date'] as String?,
      referenceUrl:
          json['reference_url'] as String?,
    );
  }
}