import 'package:dio/dio.dart';

/// Injects the X-Tenant-ID header when the request
/// has not already specified an explicit tenant.
class TenantInterceptor extends Interceptor {
  TenantInterceptor({
    required this.tenantSlug,
  });

  final String tenantSlug;

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) {
    final existingTenant =
        options.headers['X-Tenant-ID'];

    if (existingTenant == null ||
        existingTenant.toString().isEmpty) {
      if (tenantSlug.isNotEmpty) {
        options.headers['X-Tenant-ID'] = tenantSlug;
      }
    }

    handler.next(options);
  }
}