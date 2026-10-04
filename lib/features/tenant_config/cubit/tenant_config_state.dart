import '../models/tenant.dart';
import '../models/tenant_config.dart';

abstract class TenantConfigState {
  const TenantConfigState();
}

class TenantConfigInitial extends TenantConfigState {
  const TenantConfigInitial();
}

class TenantConfigLoading extends TenantConfigState {
  const TenantConfigLoading();
}

class TenantConfigLoaded extends TenantConfigState {
  final TenantConfig config;

  const TenantConfigLoaded(this.config);
}

class TenantConfigError extends TenantConfigState {
  final String message;

  const TenantConfigError(this.message);
}

class TenantListLoading extends TenantConfigState {
  const TenantListLoading();
}

class TenantListLoaded extends TenantConfigState {
  final List<Tenant> tenants;

  const TenantListLoaded(this.tenants);
}

class TenantCreating extends TenantConfigState {
  const TenantCreating();
}

class TenantCreated extends TenantConfigState {
  final Tenant tenant;

  const TenantCreated(this.tenant);
}

class TenantActionSuccess extends TenantConfigState {
  final String message;

  const TenantActionSuccess(this.message);
}