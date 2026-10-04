import 'package:dio/dio.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';

import '../config/app_config.dart';
import 'interceptors/auth_interceptor.dart';
import 'interceptors/tenant_interceptor.dart';

/// Singleton Dio instance used by all repository classes.
/// Interceptors are attached in order: tenant → auth → logger.
Dio createApiClient({
  required String tenantSlug,
  required String? accessToken,
  required Future<String?> Function() onRefreshToken,
  required Future<void> Function() onSessionExpired,
}) {
  final dio = Dio(
    BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
      },
    ),
  );

  dio.interceptors.addAll([
    TenantInterceptor(
      tenantSlug: tenantSlug,
    ),
    AuthInterceptor(
      accessToken: accessToken,
      onRefreshToken: onRefreshToken,
      onSessionExpired: onSessionExpired,
      dio: dio,
    ),
    PrettyDioLogger(
      requestHeader: false,
      requestBody: true,
      responseBody: true,
      compact: true,
    ),
  ]);

  return dio;
}
