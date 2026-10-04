import 'package:flutter_bloc/flutter_bloc.dart';

import '../../features/auth/data/repository/auth_repository.dart';
import 'auth_state.dart';
import 'token_storage.dart';

/// Manages the global authentication state.
/// Holds the access token in memory; persists the refresh token via [TokenStorage].
class AuthCubit extends Cubit<AuthState> {
  AuthCubit({required this.tokenStorage, required this.authRepository})
    : super(const AuthInitial());

  final TokenStorage tokenStorage;
  final AuthRepository authRepository;

  String? _accessToken;
  String? _tenantSlug;

  String? get accessToken => _accessToken;
  String? get tenantSlug => _tenantSlug;

  /// Called at app start — tries to restore session from stored refresh token.
  Future<void> checkSession() async {
    final refreshToken = await tokenStorage.readRefreshToken();
    final slug = await tokenStorage.readTenantSlug();

    if (refreshToken == null || slug == null) {
      emit(const AuthUnauthenticated());
      return;
    }

    try {
      final newAccessToken = await authRepository.refresh(
        refreshToken: refreshToken,
      );
      final profile = await authRepository.getMe(accessToken: newAccessToken,);
      _accessToken = newAccessToken;
      _tenantSlug = slug;
      emit(
        AuthAuthenticated(
          accessToken: newAccessToken,
          tenantSlug: slug,
          role: profile.role,
        ),
      );
    } catch (_) {
      // Refresh failed — token likely expired, clear storage
      await tokenStorage.clear();
      emit(const AuthUnauthenticated());
    }
  }

  /// Called after a successful login response.
  Future<void> onLoginSuccess({
    required String accessToken,
    required String refreshToken,
    required String tenantSlug,
    required String role,
  }) async {
    _accessToken = accessToken;
    _tenantSlug = tenantSlug;
    await tokenStorage.saveRefreshToken(refreshToken);
    await tokenStorage.saveTenantSlug(tenantSlug);
    emit(
      AuthAuthenticated(
        accessToken: accessToken,
        tenantSlug: tenantSlug,
        role: role,
      ),
    );
  }

  /// Clears all session data and returns to unauthenticated state.
  Future<void> logout() async {
    final refreshToken = await tokenStorage.readRefreshToken();
    if (refreshToken != null) {
      try {
        await authRepository.logout(refreshToken: refreshToken);
      } catch (_) {
        // Best effort
      }
    }
    _accessToken = null;
    _tenantSlug = null;
    await tokenStorage.clear();
    emit(const AuthUnauthenticated());
  }

  Future<void> expireSession() async {
    _accessToken = null;
    _tenantSlug = null;

    await tokenStorage.clear();

    emit(const AuthUnauthenticated());
  }
}
