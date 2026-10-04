import 'dart:async';

import 'package:dio/dio.dart';

/// Adds the access token to requests and transparently refreshes
/// an expired access token.
///
/// If the refresh token is no longer valid, [onSessionExpired]
/// clears the authenticated session.
class AuthInterceptor extends Interceptor {
  AuthInterceptor({
    required this.accessToken,
    required this.onRefreshToken,
    required this.onSessionExpired,
    required this.dio,
  });

  String? accessToken;

  final Future<String?> Function() onRefreshToken;
  final Future<void> Function() onSessionExpired;
  final Dio dio;

  Future<String?>? _refreshFuture;

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) {
    final token = accessToken;

    if (token != null && token.isNotEmpty) {
      options.headers['Authorization'] =
          'Bearer $token';
    }

    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final response = err.response;

    if (response?.statusCode != 401) {
      handler.next(err);
      return;
    }

    final request = err.requestOptions;

    // Never try to refresh the refresh request itself.
    final isRefreshRequest =
        request.path.endsWith('/auth/refresh');

    if (isRefreshRequest) {
      handler.next(err);
      return;
    }

    // Never retry the same request more than once.
    final alreadyRetried =
        request.extra['auth_retry'] == true;

    if (alreadyRetried) {
      handler.next(err);
      return;
    }

    try {
      final newToken = await _getFreshToken();

      if (newToken == null || newToken.isEmpty) {
        handler.next(err);
        return;
      }

      request.extra['auth_retry'] = true;
      request.headers['Authorization'] =
          'Bearer $newToken';

      final retryResponse =
          await dio.fetch<dynamic>(request);

      handler.resolve(retryResponse);
    } catch (_) {
      handler.next(err);
    }
  }

  Future<String?> _getFreshToken() {
    final existing = _refreshFuture;

    if (existing != null) {
      return existing;
    }

    final future = _performRefresh();

    _refreshFuture = future;

    future.whenComplete(() {
      if (identical(_refreshFuture, future)) {
        _refreshFuture = null;
      }
    });

    return future;
  }

  Future<String?> _performRefresh() async {
    try {
      final newToken = await onRefreshToken();

      if (newToken == null || newToken.isEmpty) {
        await onSessionExpired();
        return null;
      }

      accessToken = newToken;

      return newToken;
    } catch (_) {
      await onSessionExpired();
      return null;
    }
  }
}