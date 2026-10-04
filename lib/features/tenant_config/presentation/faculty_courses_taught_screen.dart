import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../academics/data/models/course.dart';
import '../models/college.dart';
import '../models/faculty_course_assignment.dart';
import '../models/tenant.dart';
import '../repository/tenant_config_repository.dart';

class FacultyCoursesTaughtScreen
    extends StatefulWidget {
  final Tenant tenant;
  final College college;
  final String facultyId;
  final String facultyName;

  const FacultyCoursesTaughtScreen({
    super.key,
    required this.tenant,
    required this.college,
    required this.facultyId,
    required this.facultyName,
  });

  @override
  State<FacultyCoursesTaughtScreen> createState() =>
      _FacultyCoursesTaughtScreenState();
}

class _FacultyCoursesTaughtScreenState
    extends State<FacultyCoursesTaughtScreen> {
  late final TenantConfigRepository _repository;

  late Future<_CoursesTaughtData>
      _dataFuture;

  @override
  void initState() {
    super.initState();

    _repository =
        TenantConfigRepository(
      context.read<Dio>(),
    );

    _loadData();
  }

  void _loadData() {
    _dataFuture = _loadCoursesTaughtData();
  }

  Future<_CoursesTaughtData>
      _loadCoursesTaughtData() async {
    final results = await Future.wait([
      _repository.getCourseAssignments(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        facultyId: widget.facultyId,
      ),
      _repository.getCollegeCourses(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
      ),
    ]);

    return _CoursesTaughtData(
      assignments:
          results[0]
              as List<FacultyCourseAssignment>,
      courses:
          results[1] as List<Course>,
    );
  }

  Future<void> _addAssignment(
    List<Course> courses,
  ) async {
    if (courses.isEmpty) {
      _showError(
        'Create a course before assigning it to faculty.',
      );
      return;
    }

    final result =
        await showDialog<_CourseAssignmentFormData>(
      context: context,
      builder: (_) =>
          _CourseAssignmentFormDialog(
        courses: courses,
      ),
    );

    if (result == null || !mounted) return;

    try {
      await _repository.createCourseAssignment(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        facultyId: widget.facultyId,
        courseId: result.courseId,
        academicYear: result.academicYear,
        semester: result.semester,
        section: result.section,
        teachingRole: result.teachingRole,
        assignedFrom: result.assignedFrom,
        assignedUntil: result.assignedUntil,
      );

      if (!mounted) return;

      setState(_loadData);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Course assignment added successfully.',
          ),
        ),
      );
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _editAssignment(
    FacultyCourseAssignment assignment,
    List<Course> courses,
  ) async {
    final result =
        await showDialog<_CourseAssignmentFormData>(
      context: context,
      builder: (_) =>
          _CourseAssignmentFormDialog(
        courses: courses,
        assignment: assignment,
      ),
    );

    if (result == null || !mounted) return;

    try {
      await _repository.updateCourseAssignment(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        assignmentId: assignment.id,
        courseId: result.courseId,
        academicYear: result.academicYear,
        semester: result.semester,
        section: result.section,
        teachingRole: result.teachingRole,
        assignedFrom: result.assignedFrom,
        assignedUntil: result.assignedUntil,
      );

      if (!mounted) return;

      setState(_loadData);
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _deleteAssignment(
    FacultyCourseAssignment assignment,
  ) async {
    final confirmed =
        await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text(
          'Remove Course Assignment',
        ),
        content: const Text(
          'Remove this course from the faculty teaching record?',
        ),
        actions: [
          TextButton(
            onPressed: () =>
                Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () =>
                Navigator.of(context).pop(true),
            child: const Text('Remove'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) {
      return;
    }

    try {
      await _repository.deleteCourseAssignment(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        assignmentId: assignment.id,
      );

      if (!mounted) return;

      setState(_loadData);
    } catch (error) {
      _showError(error);
    }
  }

  void _showError(Object error) {
    if (!mounted) return;

    String message =
        error.toString();

    if (error is DioException) {
      final body =
          error.response?.data;

      if (body is Map<String, dynamic> &&
          body['detail'] != null) {
        message =
            body['detail'].toString();
      }
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration:
            const Duration(seconds: 6),
      ),
    );
  }

  String _courseLabel(
    FacultyCourseAssignment assignment,
    List<Course> courses,
  ) {
    for (final course in courses) {
      if (course.id == assignment.courseId) {
        return '${course.code} • ${course.name}';
      }
    }

    return 'Unknown course';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Courses Taught',
        ),
      ),
      body:
          FutureBuilder<_CoursesTaughtData>(
        future: _dataFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState ==
              ConnectionState.waiting) {
            return const Center(
              child:
                  CircularProgressIndicator(),
            );
          }

          if (snapshot.hasError) {
            return Center(
              child: Padding(
                padding:
                    const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize:
                      MainAxisSize.min,
                  children: [
                    Text(
                      snapshot.error
                          .toString(),
                      textAlign:
                          TextAlign.center,
                    ),
                    const SizedBox(
                      height: 16,
                    ),
                    FilledButton(
                      onPressed: () {
                        setState(
                          _loadData,
                        );
                      },
                      child:
                          const Text(
                        'Retry',
                      ),
                    ),
                  ],
                ),
              ),
            );
          }

          final data =
              snapshot.data!;

          return ListView(
            padding:
                const EdgeInsets.all(24),
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      'Courses Taught',
                      style: Theme.of(
                        context,
                      )
                          .textTheme
                          .titleLarge,
                    ),
                  ),
                  FilledButton.icon(
                    onPressed: () =>
                        _addAssignment(
                      data.courses,
                    ),
                    icon:
                        const Icon(
                      Icons.add,
                    ),
                    label:
                        const Text(
                      'Add Course',
                    ),
                  ),
                ],
              ),
              const SizedBox(
                height: 16,
              ),

              if (data.assignments.isEmpty)
                const Card(
                  child: Padding(
                    padding:
                        EdgeInsets.all(24),
                    child: Text(
                      'No courses assigned yet.',
                    ),
                  ),
                )
              else
                for (final assignment
                    in data.assignments)
                  Card(
                    margin:
                        const EdgeInsets.only(
                      bottom: 12,
                    ),
                    child: ListTile(
                      leading:
                          const CircleAvatar(
                        child: Icon(
                          Icons
                              .school_outlined,
                        ),
                      ),
                      title: Text(
                        _courseLabel(
                          assignment,
                          data.courses,
                        ),
                      ),
                      subtitle: Text(
                        [
                          'AY ${assignment.academicYear}',
                          'Semester ${assignment.semester}',
                          if (assignment
                                  .section
                                  ?.isNotEmpty ==
                              true)
                            'Section ${assignment.section}',
                          assignment.teachingRole,
                        ].join(' • '),
                      ),
                      trailing:
                          PopupMenuButton<
                              String>(
                        onSelected:
                            (value) {
                          if (value ==
                              'edit') {
                            _editAssignment(
                              assignment,
                              data.courses,
                            );
                          }

                          if (value ==
                              'delete') {
                            _deleteAssignment(
                              assignment,
                            );
                          }
                        },
                        itemBuilder:
                            (context) =>
                                const [
                          PopupMenuItem(
                            value: 'edit',
                            child:
                                Text(
                              'Edit',
                            ),
                          ),
                          PopupMenuItem(
                            value: 'delete',
                            child:
                                Text(
                              'Remove',
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
            ],
          );
        },
      ),
    );
  }
}

class _CoursesTaughtData {
  final List<FacultyCourseAssignment>
      assignments;
  final List<Course> courses;

  const _CoursesTaughtData({
    required this.assignments,
    required this.courses,
  });
}

class _CourseAssignmentFormData {
  final String courseId;
  final String academicYear;
  final int semester;
  final String? section;
  final String teachingRole;
  final String? assignedFrom;
  final String? assignedUntil;

  const _CourseAssignmentFormData({
    required this.courseId,
    required this.academicYear,
    required this.semester,
    required this.section,
    required this.teachingRole,
    required this.assignedFrom,
    required this.assignedUntil,
  });
}

class _CourseAssignmentFormDialog
    extends StatefulWidget {
  final List<Course> courses;
  final FacultyCourseAssignment? assignment;

  const _CourseAssignmentFormDialog({
    required this.courses,
    this.assignment,
  });

  @override
  State<_CourseAssignmentFormDialog>
      createState() =>
          _CourseAssignmentFormDialogState();
}

class _CourseAssignmentFormDialogState
    extends State<_CourseAssignmentFormDialog> {
  final _formKey =
      GlobalKey<FormState>();

  late String _courseId;

  final _academicYearController =
      TextEditingController();

  final _semesterController =
      TextEditingController();

  final _sectionController =
      TextEditingController();

  final _teachingRoleController =
      TextEditingController();

  final _assignedFromController =
      TextEditingController();

  final _assignedUntilController =
      TextEditingController();

  @override
  void initState() {
    super.initState();

    final assignment =
        widget.assignment;

    _courseId =
        assignment?.courseId ??
            widget.courses.first.id;

    _academicYearController.text =
        assignment?.academicYear ?? '';

    _semesterController.text =
        assignment?.semester.toString() ??
            '';

    _sectionController.text =
        assignment?.section ?? '';

    _teachingRoleController.text =
        assignment?.teachingRole ??
            'primary';

    _assignedFromController.text =
        assignment?.assignedFrom ?? '';

    _assignedUntilController.text =
        assignment?.assignedUntil ?? '';
  }

  @override
  void dispose() {
    _academicYearController
        .dispose();
    _semesterController.dispose();
    _sectionController.dispose();
    _teachingRoleController
        .dispose();
    _assignedFromController
        .dispose();
    _assignedUntilController
        .dispose();
    super.dispose();
  }

  Future<void> _pickDate(
    TextEditingController controller,
  ) async {
    final initialDate =
        DateTime.tryParse(
              controller.text,
            ) ??
            DateTime.now();

    final picked =
        await showDatePicker(
      context: context,
      initialDate: initialDate,
      firstDate:
          DateTime(2000),
      lastDate:
          DateTime(2100),
    );

    if (picked == null) {
      return;
    }

    final month =
        picked.month
            .toString()
            .padLeft(2, '0');

    final day =
        picked.day
            .toString()
            .padLeft(2, '0');

    controller.text =
        '${picked.year}-$month-$day';
  }

  String? _optional(
    String value,
  ) {
    final trimmed =
        value.trim();

    return trimmed.isEmpty
        ? null
        : trimmed;
  }

  void _submit() {
    if (!_formKey.currentState!
        .validate()) {
      return;
    }

    final semester =
        int.tryParse(
      _semesterController.text.trim(),
    );

    if (semester == null ||
        semester < 1 ||
        semester > 20) {
      return;
    }

    Navigator.of(context).pop(
      _CourseAssignmentFormData(
        courseId: _courseId,
        academicYear:
            _academicYearController
                .text
                .trim(),
        semester: semester,
        section:
            _optional(
          _sectionController.text,
        ),
        teachingRole:
            _teachingRoleController.text
                .trim(),
        assignedFrom:
            _optional(
          _assignedFromController
              .text,
        ),
        assignedUntil:
            _optional(
          _assignedUntilController
              .text,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final editing =
        widget.assignment != null;

    return AlertDialog(
      title: Text(
        editing
            ? 'Edit Course Assignment'
            : 'Add Course Taught',
      ),
      content: SizedBox(
        width: 560,
        child: Form(
          key: _formKey,
          child:
              SingleChildScrollView(
            child: Column(
              mainAxisSize:
                  MainAxisSize.min,
              children: [
                DropdownButtonFormField<
                    String>(
                  initialValue:
                      _courseId,
                  decoration:
                      const InputDecoration(
                    labelText: 'Course',
                  ),
                  items: widget.courses
                      .map(
                        (course) =>
                            DropdownMenuItem(
                          value:
                              course.id,
                          child: Text(
                            '${course.code} • ${course.name}',
                          ),
                        ),
                      )
                      .toList(),
                  onChanged: (value) {
                    if (value ==
                        null) {
                      return;
                    }

                    setState(() {
                      _courseId =
                          value;
                    });
                  },
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _academicYearController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Academic Year',
                    hintText:
                        '2026-27',
                  ),
                  validator:
                      (value) {
                    if (value ==
                            null ||
                        value.trim()
                                .length <
                            4) {
                      return 'Enter academic year';
                    }
                    return null;
                  },
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _semesterController,
                  keyboardType:
                      TextInputType.number,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Semester',
                  ),
                  validator:
                      (value) {
                    final semester =
                        int.tryParse(
                      value?.trim() ??
                          '',
                    );

                    if (semester ==
                            null ||
                        semester < 1 ||
                        semester > 20) {
                      return 'Enter semester 1-20';
                    }

                    return null;
                  },
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _sectionController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Section',
                    hintText:
                        'A',
                  ),
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _teachingRoleController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Teaching Role',
                    hintText:
                        'primary',
                  ),
                  validator:
                      (value) {
                    if (value ==
                            null ||
                        value.trim()
                                .length <
                            2) {
                      return 'Enter teaching role';
                    }

                    return null;
                  },
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _assignedFromController,
                  readOnly: true,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Assigned From',
                    suffixIcon:
                        Icon(
                      Icons
                          .calendar_today,
                    ),
                  ),
                  onTap: () =>
                      _pickDate(
                    _assignedFromController,
                  ),
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _assignedUntilController,
                  readOnly: true,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Assigned Until',
                    suffixIcon:
                        Icon(
                      Icons
                          .calendar_today,
                    ),
                  ),
                  onTap: () =>
                      _pickDate(
                    _assignedUntilController,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () =>
              Navigator.of(context)
                  .pop(),
          child:
              const Text('Cancel'),
        ),
        FilledButton(
          onPressed: _submit,
          child: Text(
            editing
                ? 'Save'
                : 'Create',
          ),
        ),
      ],
    );
  }
}