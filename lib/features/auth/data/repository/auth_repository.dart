import 'package:dio/dio.dart';

import '../../../../core/api/api_exception.dart';
import '../models/auth_response.dart';

class AuthRepository {
  AuthRepository({required this.dio});

  final Dio dio;

  Future<AuthTokenResponse> login({
    required String email,
    required String password,
    required String tenantSlug,
  }) async {
    try {
      final response = await dio.post<Map<String, dynamic>>(
        '/auth/login',
        data: {'email': email, 'password': password, 'tenant_slug': tenantSlug},
      );
      return AuthTokenResponse.fromJson(response.data!);
    } on DioException catch (e) {
      throw _mapError(e);
    }
  }

  Future<String> refresh({required String refreshToken}) async {
    try {
      final response = await dio.post<Map<String, dynamic>>(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
        options: Options(extra: {'skipAuthRefresh': true}),
      );
      return response.data!['access_token'] as String;
    } on DioException catch (e) {
      throw _mapError(e);
    }
  }

  Future<void> logout({required String refreshToken}) async {
    try {
      await dio.post<void>(
        '/auth/logout',
        data: {'refresh_token': refreshToken},
      );
    } on DioException catch (_) {
      // Best-effort — ignore errors on logout
    }
  }

  /// Fetch the authenticated user's profile.
  /// Pass [accessToken] explicitly at login time before the Dio interceptor
  /// has been configured with the token.
  Future<UserProfile> getMe({String? accessToken}) async {
    try {
      final response = await dio.get<Map<String, dynamic>>(
        '/auth/me',
        options: accessToken != null
            ? Options(headers: {'Authorization': 'Bearer $accessToken'})
            : null,
      );
      return UserProfile.fromJson(response.data!);
    } on DioException catch (e) {
      throw _mapError(e);
    }
  }

  ApiException _mapError(DioException e) {
    final status = e.response?.statusCode;
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout ||
        e.type == DioExceptionType.connectionError) {
      return const NetworkException();
    }
    return switch (status) {
      401 => const UnauthorisedException(),
      403 => const ForbiddenException(),
      404 => const NotFoundException(),
      400 || 422 => ValidationException(
        _extractMessage(e.response?.data) ?? 'Invalid request.',
      ),
      _ => const ServerException(),
    };
  }

  String? _extractMessage(dynamic data) {
    if (data is Map) {
      final detail = data['detail'];
      if (detail is Map) return detail['message'] as String?;
      if (detail is String) return detail;
      final error = data['error'];
      if (error is Map) return error['message'] as String?;
    }
    return null;
  }
}
