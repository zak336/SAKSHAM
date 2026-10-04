class User {
  final String id;
  final String tenantId;
  final String? collegeId;
  final String name;
  final String email;
  final String? phone;
  final String role;
  final bool isActive;

  const User({
    required this.id,
    required this.tenantId,
    required this.collegeId,
    required this.name,
    required this.email,
    required this.phone,
    required this.role,
    required this.isActive,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      collegeId: json['college_id'] as String?,
      name: json['name'] as String,
      email: json['email'] as String,
      phone: json['phone'] as String?,
      role: json['role'] as String,
      isActive: json['is_active'] as bool? ?? true,
    );
  }
}