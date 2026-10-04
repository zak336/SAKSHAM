import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:dio/dio.dart';

import 'core/api/interceptors/auth_interceptor.dart';
import 'core/api/interceptors/tenant_interceptor.dart';
import 'core/auth/auth_cubit.dart';
import 'core/auth/auth_state.dart';
import 'core/auth/token_storage.dart';
import 'core/config/app_config.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/data/repository/auth_repository.dart';
import 'features/auth/logic/login_cubit.dart';
import 'features/tenant_config/cubit/tenant_config_cubit.dart';
import 'features/tenant_config/repository/tenant_config_repository.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Hive.initFlutter();
  AppConfig.init();
  runApp(const ZakCERPApp());
}

class ZakCERPApp extends StatefulWidget {
  const ZakCERPApp({super.key});

  @override
  State<ZakCERPApp> createState() => _ZakCERPAppState();
}

class _ZakCERPAppState extends State<ZakCERPApp> {
  late final TokenStorage _tokenStorage;
  late final AuthCubit _authCubit;
  late final AuthRepository _authRepository;

  // Plain Dio for auth-only calls (login, refresh) — no token interceptor
  late final Dio _authDio;

  // Authenticated Dio for all feature API calls — has token + tenant interceptors
  late final Dio _apiDio;
  late final AuthInterceptor _authInterceptor;

  @override
  void initState() {
    super.initState();

    _tokenStorage = TokenStorage();

    _authDio = Dio(
      BaseOptions(
        baseUrl: AppConfig.apiBaseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 30),
        headers: {'Content-Type': 'application/json'},
      ),
    );

    _authRepository = AuthRepository(dio: _authDio);

    _authCubit = AuthCubit(
      tokenStorage: _tokenStorage,
      authRepository: _authRepository,
    );

    _apiDio = Dio(
      BaseOptions(
        baseUrl: AppConfig.apiBaseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 30),
        headers: {'Content-Type': 'application/json'},
      ),
    );

    // Build the authenticated Dio — interceptors reference AuthCubit state
    _authInterceptor = AuthInterceptor(
      accessToken: null,
      onRefreshToken: () async {
        final refreshToken = await _tokenStorage.readRefreshToken();

        if (refreshToken == null) return null;

        try {
          return await _authRepository.refresh(refreshToken: refreshToken);
        } catch (_) {
          await _authCubit.logout();
          return null;
        }
      },
      onSessionExpired: () async {
        await _authCubit.expireSession();
      },
      dio: _apiDio,
    );

    _apiDio.interceptors.addAll([
      _authInterceptor,
      TenantInterceptor(tenantSlug: ''), // slug updated after login
    ]);

    // Keep the auth interceptor's token in sync with auth state
    _authCubit.stream.listen((state) {
      if (state is AuthAuthenticated) {
        _authInterceptor.accessToken = state.accessToken;
        // Replace tenant interceptor with the correct slug
        _apiDio.interceptors.removeWhere((i) => i is TenantInterceptor);
        _apiDio.interceptors.add(
          TenantInterceptor(tenantSlug: state.tenantSlug),
        );
      } else {
        _authInterceptor.accessToken = null;
      }
    });

    _authCubit.checkSession();
  }

  @override
  void dispose() {
    _authCubit.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider<TokenStorage>.value(value: _tokenStorage),
        RepositoryProvider<AuthRepository>.value(value: _authRepository),
        RepositoryProvider<Dio>.value(value: _apiDio),
      ],
      child: MultiBlocProvider(
        providers: [
          BlocProvider<AuthCubit>.value(value: _authCubit),
          BlocProvider<LoginCubit>(
            create: (ctx) => LoginCubit(
              authRepository: ctx.read<AuthRepository>(),
              authCubit: ctx.read<AuthCubit>(),
            ),
          ),
          BlocProvider<TenantConfigCubit>(
            create: (context) =>
                TenantConfigCubit(TenantConfigRepository(context.read<Dio>())),
          ),
        ],
        child: _AppView(authCubit: _authCubit, apiDio: _apiDio),
      ),
    );
  }
}

class _AppView extends StatefulWidget {
  const _AppView({required this.authCubit, required this.apiDio});
  final AuthCubit authCubit;
  final Dio apiDio;

  @override
  State<_AppView> createState() => _AppViewState();
}

class _AppViewState extends State<_AppView> {
  late final _router = createAppRouter(
    authCubit: widget.authCubit,
    dio: widget.apiDio,
  );

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'ZakCERP',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      routerConfig: _router,
    );
  }
}
