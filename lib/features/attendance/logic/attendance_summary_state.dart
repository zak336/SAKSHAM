part of 'attendance_summary_cubit.dart';

sealed class AttendanceSummaryState extends Equatable {
  const AttendanceSummaryState();

  @override
  List<Object?> get props => [];
}

final class AttendanceSummaryInitial extends AttendanceSummaryState {
  const AttendanceSummaryInitial();
}

final class AttendanceSummaryLoading extends AttendanceSummaryState {
  const AttendanceSummaryLoading();
}

final class AttendanceSummaryLoaded extends AttendanceSummaryState {
  const AttendanceSummaryLoaded(this.summaries);
  final List<AttendanceSummary> summaries;

  @override
  List<Object?> get props => [summaries];
}

final class AttendanceSummaryError extends AttendanceSummaryState {
  const AttendanceSummaryError(this.message);
  final String message;

  @override
  List<Object?> get props => [message];
}
