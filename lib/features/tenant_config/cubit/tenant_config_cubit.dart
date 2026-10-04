import 'package:flutter_bloc/flutter_bloc.dart';

import '../repository/tenant_config_repository.dart';
import 'tenant_config_state.dart';

class TenantConfigCubit extends Cubit<TenantConfigState> {
  final TenantConfigRepository repository;

  TenantConfigCubit(this.repository)
      : super(const TenantConfigInitial());

  Future<void> loadTenants() async {
    emit(const TenantListLoading());

    try {
      final tenants = await repository.getTenants();

      emit(
        TenantListLoaded(tenants),
      );
    } catch (error) {
      emit(
        TenantConfigError(
          error.toString(),
        ),
      );
    }
  }

  Future<void> createTenant({
    required String name,
    required String slug,
  }) async {
    emit(const TenantCreating());

    try {
      final tenant = await repository.createTenant(
        name: name,
        slug: slug,
      );

      emit(
        TenantCreated(tenant),
      );
    } catch (error) {
      emit(
        TenantConfigError(
          error.toString(),
        ),
      );
    }
  }

  /// Load configuration for a specific tenant.
  Future<void> loadTenantConfig({
    required String tenantId,
  }) async {
    emit(const TenantConfigLoading());

    try {
      final config = await repository.getTenantConfig(
        tenantId: tenantId,
      );

      emit(
        TenantConfigLoaded(config),
      );
    } catch (error) {
      emit(
        TenantConfigError(
          error.toString(),
        ),
      );
    }
  }

  Future<void> updateBranding({
    required String tenantId,
    String? displayName,
    String? logoUrl,
    String? faviconUrl,
    String? primaryColor,
    String? secondaryColor,
    String? accentColor,
  }) async {
    try {
      final config = await repository.updateTenantBranding(
        tenantId: tenantId,
        displayName: displayName,
        logoUrl: logoUrl,
        faviconUrl: faviconUrl,
        primaryColor: primaryColor,
        secondaryColor: secondaryColor,
        accentColor: accentColor,
      );

      emit(
        TenantConfigLoaded(config),
      );
    } catch (error) {
      emit(
        TenantConfigError(
          error.toString(),
        ),
      );
    }
  }

  Future<void> updateModule({
    required String tenantId,
    required String moduleKey,
    required bool enabled,
  }) async {
    try {
      await repository.updateModule(
        tenantId: tenantId,
        moduleKey: moduleKey,
        enabled: enabled,
      );

      await loadTenantConfig(
        tenantId: tenantId,
      );
    } catch (error) {
      emit(
        TenantConfigError(
          error.toString(),
        ),
      );
    }
  }

  Future<void> updateTenantStatus({
    required String tenantId,
    required bool isActive,
  }) async {
    try {
      await repository.updateTenant(
        tenantId: tenantId,
        isActive: isActive,
      );

      emit(
        const TenantActionSuccess(
          'Tenant updated successfully.',
        ),
      );
    } catch (error) {
      emit(
        TenantConfigError(
          error.toString(),
        ),
      );
    }
  }

  void clear() {
    emit(const TenantConfigInitial());
  }
}