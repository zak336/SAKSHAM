import 'package:equatable/equatable.dart';

/// Authentication states used by [AuthCubit].
sealed class AuthState extends Equatable {
  const AuthState();

  @override
  List<Object?> get props => [];
}

/// Initial state — checking secure storage for an existing session.
final class AuthInitial extends AuthState {
  const AuthInitial();
}

/// A valid session exists (token has been refreshed or user just logged in).
final class AuthAuthenticated extends AuthState {
  const AuthAuthenticated({
    required this.accessToken,
    required this.tenantSlug,
    required this.role,
  });

  final String accessToken;
  final String tenantSlug;
  final String role;

  @override
  List<Object?> get props => [accessToken, tenantSlug, role];
}

/// No session — user must log in.
final class AuthUnauthenticated extends AuthState {
  const AuthUnauthenticated();
}

/// A login or refresh operation is in progress.
final class AuthLoading extends AuthState {
  const AuthLoading();
}

/// Login failed.
final class AuthError extends AuthState {
  const AuthError(this.message);

  final String message;

  @override
  List<Object?> get props => [message];
}
