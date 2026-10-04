import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../data/models/course.dart';
import '../data/models/department.dart';
import '../data/repository/academics_repository.dart';

part 'academics_state.dart';

class AcademicsCubit extends Cubit<AcademicsState> {
  AcademicsCubit({required this.repository}) : super(const AcademicsInitial());

  final AcademicsRepository repository;

  Future<void> load({String? departmentId, int? semester}) async {
    emit(const AcademicsLoading());
    try {
      final results = await Future.wait([
        repository.getDepartments(),
        repository.getCourses(
          departmentId: departmentId,
          semester: semester,
        ),
      ]);
      emit(AcademicsLoaded(
        departments: results[0] as List<Department>,
        courses: results[1] as List<Course>,
      ));
    } catch (e) {
      emit(AcademicsError(e.toString()));
    }
  }
}
