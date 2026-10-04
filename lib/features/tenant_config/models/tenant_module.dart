class TenantModule {
  final String id;
  final String key;
  final String name;
  final String? description;
  final bool isCore;
  final bool isActive;
  final bool enabled;

  const TenantModule({
    required this.id,
    required this.key,
    required this.name,
    this.description,
    required this.isCore,
    required this.isActive,
    required this.enabled,
  });

  factory TenantModule.fromJson(Map<String, dynamic> json) {
    return TenantModule(
      id: json['id'] as String,
      key: json['key'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      isCore: json['is_core'] as bool? ?? false,
      isActive: json['is_active'] as bool? ?? false,
      enabled: json['enabled'] as bool? ?? false,
    );
  }
}