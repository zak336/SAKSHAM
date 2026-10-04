/// Typed API failure surfaced to the repository layer.
sealed class ApiException implements Exception {
  const ApiException(this.message);
  final String message;
}

/// 401 — token missing/invalid/expired and refresh failed.
final class UnauthorisedException extends ApiException {
  const UnauthorisedException([super.message = 'Session expired. Please log in again.']);
}

/// 403 — authenticated but not allowed.
final class ForbiddenException extends ApiException {
  const ForbiddenException([super.message = 'You do not have permission to perform this action.']);
}

/// 404 — resource not found.
final class NotFoundException extends ApiException {
  const NotFoundException([super.message = 'The requested resource was not found.']);
}

/// 400 / 422 — request or business-rule validation failed.
final class ValidationException extends ApiException {
  const ValidationException(super.message);
}

/// 5xx or network failure.
final class ServerException extends ApiException {
  const ServerException([super.message = 'A server error occurred. Please try again.']);
}

/// No internet / connection timeout.
final class NetworkException extends ApiException {
  const NetworkException([super.message = 'No internet connection.']);
}
