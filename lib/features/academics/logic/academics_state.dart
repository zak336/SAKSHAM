part of 'academics_cubit.dart';

sealed class AcademicsState extends Equatable {
  const AcademicsState();

  @override
  List<Object?> get props => [];
}

final class AcademicsInitial extends AcademicsState {
  const AcademicsInitial();
}

final class AcademicsLoading extends AcademicsState {
  const AcademicsLoading();
}

final class AcademicsLoaded extends AcademicsState {
  const AcademicsLoaded({
    required this.departments,
    required this.courses,
  });

  final List<Department> departments;
  final List<Course> courses;

  @override
  List<Object?> get props => [departments, courses];
}

final class AcademicsError extends AcademicsState {
  const AcademicsError(this.message);
  final String message;

  @override
  List<Object?> get props => [message];
}
