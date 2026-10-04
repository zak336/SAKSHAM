import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../data/models/attendance_summary.dart';
import '../data/repository/attendance_repository.dart';

part 'attendance_summary_state.dart';

class AttendanceSummaryCubit extends Cubit<AttendanceSummaryState> {
  AttendanceSummaryCubit({required this.repository})
      : super(const AttendanceSummaryInitial());

  final AttendanceRepository repository;

  Future<void> loadSummary({String? studentId, String? semester}) async {
    emit(const AttendanceSummaryLoading());
    try {
      final summaries = await repository.getAttendanceSummary(
        studentId: studentId,
        semester: semester,
      );
      emit(AttendanceSummaryLoaded(summaries));
    } catch (e) {
      emit(AttendanceSummaryError(e.toString()));
    }
  }
}
