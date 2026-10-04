import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Wraps flutter_secure_storage for token persistence.
/// Access tokens are held in memory by the AuthCubit; only the refresh token
/// is written to secure storage so it survives app restarts.
class TokenStorage {
  TokenStorage() : _storage = const FlutterSecureStorage();

  final FlutterSecureStorage _storage;

  static const _kRefreshToken = 'refresh_token';
  static const _kTenantSlug = 'tenant_slug';

  Future<void> saveRefreshToken(String token) =>
      _storage.write(key: _kRefreshToken, value: token);

  Future<String?> readRefreshToken() => _storage.read(key: _kRefreshToken);

  Future<void> deleteRefreshToken() => _storage.delete(key: _kRefreshToken);

  Future<void> saveTenantSlug(String slug) =>
      _storage.write(key: _kTenantSlug, value: slug);

  Future<String?> readTenantSlug() => _storage.read(key: _kTenantSlug);

  Future<void> clear() => _storage.deleteAll();
}
