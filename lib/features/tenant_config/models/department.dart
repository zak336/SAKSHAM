class Department {
  final String id;
  final String tenantId;
  final String collegeId;
  final String name;
  final String code;
  final bool isActive;

  const Department({
    required this.id,
    required this.tenantId,
    required this.collegeId,
    required this.name,
    required this.code,
    required this.isActive,
  });

  factory Department.fromJson(Map<String, dynamic> json) {
    return Department(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      collegeId: json['college_id'] as String,
      name: json['name'] as String,
      code: json['code'] as String,
      isActive: json['is_active'] as bool? ?? true,
    );
  }
}