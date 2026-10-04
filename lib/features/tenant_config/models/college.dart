class College {
  final String id;
  final String tenantId;
  final String name;
  final String code;
  final String slug;
  final bool isActive;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  const College({
    required this.id,
    required this.tenantId,
    required this.name,
    required this.code,
    required this.slug,
    required this.isActive,
    this.createdAt,
    this.updatedAt,
  });

  factory College.fromJson(Map<String, dynamic> json) {
    return College(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      name: json['name'] as String,
      code: json['code'] as String,
      slug: json['slug'] as String,
      isActive: json['is_active'] as bool? ?? true,
      createdAt: json['created_at'] == null
          ? null
          : DateTime.tryParse(
              json['created_at'].toString(),
            ),
      updatedAt: json['updated_at'] == null
          ? null
          : DateTime.tryParse(
              json['updated_at'].toString(),
            ),
    );
  }
}