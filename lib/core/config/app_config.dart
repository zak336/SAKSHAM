/// Application-level configuration resolved from compile-time environment
/// variables (--dart-define) or sensible development defaults.
class AppConfig {
  AppConfig._();

  static late final String apiBaseUrl;
  static late final String defaultTenantSlug;

  static void init() {
    apiBaseUrl = const String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://localhost:8000/api/v1', // Windows desktop / host machine
    );
    defaultTenantSlug = const String.fromEnvironment(
      'TENANT_SLUG',
      defaultValue: '',
    );
  }
}
