class Tenant {
  final String id;
  final String name;
  final String slug;
  final bool isActive;

  const Tenant({
    required this.id,
    required this.name,
    required this.slug,
    required this.isActive,
  });

  factory Tenant.fromJson(Map<String, dynamic> json) {
    return Tenant(
      id: json['id'] as String,
      name: json['name'] as String,
      slug: json['slug'] as String,
      isActive: json['is_active'] as bool? ?? true,
    );
  }
}