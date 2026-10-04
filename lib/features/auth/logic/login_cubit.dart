import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/api/api_exception.dart';
import '../../../core/auth/auth_cubit.dart';
import '../data/repository/auth_repository.dart';

part 'login_state.dart';

class LoginCubit extends Cubit<LoginState> {
  LoginCubit({
    required this.authRepository,
    required this.authCubit,
  }) : super(const LoginInitial());

  final AuthRepository authRepository;
  final AuthCubit authCubit;

  Future<void> login({
    required String email,
    required String password,
    required String tenantSlug,
  }) async {
    if (state is LoginLoading) return;
    emit(const LoginLoading());
    try {
      final response = await authRepository.login(
        email: email,
        password: password,
        tenantSlug: tenantSlug,
      );

      // Fetch user profile — pass the token explicitly since the interceptor
      // is not yet configured at this point
      final profile = await authRepository.getMe(
        accessToken: response.accessToken,
      );

      await authCubit.onLoginSuccess(
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
        tenantSlug: tenantSlug,
        role: profile.role,
      );

      emit(const LoginSuccess());
    } on ApiException catch (e) {
      emit(LoginFailure(e.message));
    } catch (_) {
      emit(const LoginFailure('An unexpected error occurred.'));
    }
  }
}
