import 'tenant_branding.dart';
import 'tenant_module.dart';

class TenantConfig {
  final String tenantId;
  final TenantBranding branding;
  final List<TenantModule> modules;

  const TenantConfig({
    required this.tenantId,
    required this.branding,
    required this.modules,
  });

  factory TenantConfig.fromJson(Map<String, dynamic> json) {
    return TenantConfig(
      tenantId: json['tenant_id'] as String,
      branding: TenantBranding.fromJson(
        json['branding'] as Map<String, dynamic>,
      ),
      modules: (json['modules'] as List<dynamic>)
          .map(
            (item) => TenantModule.fromJson(
              item as Map<String, dynamic>,
            ),
          )
          .toList(),
    );
  }

  bool isModuleEnabled(String key) {
    return modules.any(
      (module) =>
          module.key == key &&
          module.enabled &&
          module.isActive,
    );
  }

  List<TenantModule> get enabledModules {
    return modules
        .where(
          (module) => module.enabled && module.isActive,
        )
        .toList();
  }
}