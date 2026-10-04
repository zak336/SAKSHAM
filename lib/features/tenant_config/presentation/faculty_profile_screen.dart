import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/auth/auth_cubit.dart';
import '../models/college.dart';
import '../models/faculty.dart';
import '../models/tenant.dart';
import '../models/department.dart';
import '../repository/tenant_config_repository.dart';
import 'faculty_achievements_screen.dart';
import 'faculty_publications_screen.dart';
import 'faculty_patents_screen.dart';
import 'faculty_book_chapters_screen.dart';
import 'faculty_courses_taught_screen.dart';
import 'faculty_moocs_screen.dart';
import 'faculty_fdp_screen.dart';

class FacultyProfileScreen extends StatefulWidget {
  final Tenant tenant;
  final College college;
  final String facultyId;
  final String facultyName;
  final Faculty? initialFaculty;

  const FacultyProfileScreen({
    super.key,
    required this.tenant,
    required this.college,
    required this.facultyId,
    required this.facultyName,
    this.initialFaculty,
  });

  @override
  State<FacultyProfileScreen> createState() => _FacultyProfileScreenState();
}

class _FacultyProfileScreenState extends State<FacultyProfileScreen> {
  late final TenantConfigRepository _repository;
  late Future<Faculty> _facultyFuture;
  late Future<List<Department>> _departmentsFuture;

  @override
  void initState() {
    super.initState();

    _repository = TenantConfigRepository(context.read<Dio>());

    if (widget.initialFaculty != null) {
      _facultyFuture = Future.value(widget.initialFaculty!);
    } else {
      _loadFaculty();
    }

    _departmentsFuture = _repository.getDepartments(
      tenantSlug: widget.tenant.slug,
      collegeId: widget.college.id,
    );
  }

  String _departmentName(Faculty faculty, List<Department> departments) {
    for (final department in departments) {
      if (department.id == faculty.departmentId) {
        return '${department.name} (${department.code})';
      }
    }

    return 'Department not found';
  }

  void _loadFaculty() {
    _facultyFuture = _repository.getFacultyById(
      tenantSlug: widget.tenant.slug,
      collegeId: widget.college.id,
      facultyId: widget.facultyId,
    );
  }

  Future<void> _editProfile(Faculty faculty) async {
    final result = await showDialog<_FacultyEditData>(
      context: context,
      builder: (_) => _FacultyEditDialog(
        faculty: faculty,
        departmentsFuture: _departmentsFuture,
      ),
    );

    if (result == null || !mounted) return;

    try {
      final updated = await _repository.updateMyFacultyProfile(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        designation: result.designation,
        qualification: result.qualification,
        joiningDate: result.joiningDate,
        researchInterests: result.researchInterests,
        bio: result.bio,
      );

      if (!mounted) return;

      setState(() {
        _facultyFuture = Future.value(updated);
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Profile updated successfully.')),
      );
    } catch (error) {
      if (!mounted) return;

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error.toString())));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Faculty Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: () {
              context.read<AuthCubit>().logout();
            },
          ),
        ],
      ),
      body: FutureBuilder<List<Department>>(
        future: _departmentsFuture,
        builder: (context, departmentSnapshot) {
          if (departmentSnapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (departmentSnapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Text(
                  departmentSnapshot.error.toString(),
                  textAlign: TextAlign.center,
                ),
              ),
            );
          }

          final departments = departmentSnapshot.data ?? const <Department>[];

          return FutureBuilder<Faculty>(
            future: _facultyFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }

              if (snapshot.hasError) {
                return Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          snapshot.error.toString(),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 16),
                        FilledButton(
                          onPressed: () {
                            setState(() {
                              _loadFaculty();
                              _departmentsFuture = _repository.getDepartments(
                                tenantSlug: widget.tenant.slug,
                                collegeId: widget.college.id,
                              );
                            });
                          },
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                );
              }

              final faculty = snapshot.data!;

              return ListView(
                padding: const EdgeInsets.all(24),
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      CircleAvatar(
                        radius: 32,
                        child: Text(
                          widget.facultyName.isNotEmpty
                              ? widget.facultyName[0].toUpperCase()
                              : '?',
                          style: const TextStyle(fontSize: 24),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              widget.facultyName,
                              style: Theme.of(context).textTheme.headlineSmall,
                            ),
                            const SizedBox(height: 4),
                            if (faculty.designation != null)
                              Text(faculty.designation!),
                            if (faculty.qualification != null)
                              Text(faculty.qualification!),
                          ],
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 32),
                  Align(
                    alignment: Alignment.centerRight,
                    child: FilledButton.icon(
                      onPressed: () => _editProfile(faculty),
                      icon: const Icon(Icons.edit_outlined),
                      label: const Text('Edit Profile'),
                    ),
                  ),
                  const SizedBox(height: 16),

                  _InfoCard(
                    title: 'Profile',
                    children: [
                      _InfoRow(
                        label: 'Department',
                        value: _departmentName(faculty, departments),
                      ),
                      _InfoRow(
                        label: 'Joining Date',
                        value: faculty.joiningDate,
                      ),
                    ],
                  ),

                  _InfoCard(
                    title: 'Research Interests',
                    children: [
                      Text(
                        faculty.researchInterests?.trim().isNotEmpty == true
                            ? faculty.researchInterests!
                            : 'Not provided',
                      ),
                    ],
                  ),

                  _InfoCard(
                    title: 'Biography',
                    children: [
                      Text(
                        faculty.bio?.trim().isNotEmpty == true
                            ? faculty.bio!
                            : 'Not provided',
                      ),
                    ],
                  ),

                  const SizedBox(height: 12),

                  Text(
                    'Academic Portfolio',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 12),

                  _PortfolioTile(
                    icon: Icons.emoji_events_outlined,
                    title: 'Achievements',
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => FacultyAchievementsScreen(
                            tenant: widget.tenant,
                            college: widget.college,
                            facultyId: widget.facultyId,
                            facultyName: widget.facultyName,
                          ),
                        ),
                      );
                    },
                  ),
                  _PortfolioTile(
                    icon: Icons.article_outlined,
                    title: 'Publications',
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => FacultyPublicationsScreen(
                            tenant: widget.tenant,
                            college: widget.college,
                            facultyId: widget.facultyId,
                            facultyName: widget.facultyName,
                          ),
                        ),
                      );
                    },
                  ),
                  _PortfolioTile(
                    icon: Icons.lightbulb_outline,
                    title: 'Patents',
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => FacultyPatentsScreen(
                            tenant: widget.tenant,
                            college: widget.college,
                            facultyId: widget.facultyId,
                            facultyName: widget.facultyName,
                          ),
                        ),
                      );
                    },
                  ),
                  _PortfolioTile(
                    icon: Icons.menu_book_outlined,
                    title: 'Book Chapters',
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => FacultyBookChaptersScreen(
                            tenant: widget.tenant,
                            college: widget.college,
                            facultyId: widget.facultyId,
                            facultyName: widget.facultyName,
                          ),
                        ),
                      );
                    },
                  ),
                  _PortfolioTile(
                    icon: Icons.school_outlined,
                    title: 'Courses Taught',
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => FacultyCoursesTaughtScreen(
                            tenant: widget.tenant,
                            college: widget.college,
                            facultyId: widget.facultyId,
                            facultyName: widget.facultyName,
                          ),
                        ),
                      );
                    },
                  ),
                  _PortfolioTile(
                    icon: Icons.ondemand_video_outlined,
                    title: 'MOOC Completions',
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => FacultyMoocsScreen(
                            tenant: widget.tenant,
                            college: widget.college,
                            userId: faculty.userId,
                            facultyName: widget.facultyName,
                          ),
                        ),
                      );
                    },
                  ),
                  _PortfolioTile(
                    icon: Icons.workspace_premium_outlined,
                    title: 'Faculty Development Programs',
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => FacultyFdpScreen(
                            tenant: widget.tenant,
                            college: widget.college,
                            facultyId: widget.facultyId,
                            facultyName: widget.facultyName,
                          ),
                        ),
                      );
                    },
                  ),
                ],
              );
            },
          );
        },
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _InfoCard({required this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            ...children,
          ],
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String? value;

  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(
            child: Text(
              value?.trim().isNotEmpty == true ? value! : 'Not provided',
            ),
          ),
        ],
      ),
    );
  }
}

class _PortfolioTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final VoidCallback onTap;

  const _PortfolioTile({
    required this.icon,
    required this.title,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: Icon(icon),
        title: Text(title),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}

class _FacultyEditData {
  final String departmentId;
  final String? designation;
  final String? qualification;
  final String? joiningDate;
  final String? researchInterests;
  final String? bio;

  const _FacultyEditData({
    required this.departmentId,
    required this.designation,
    required this.qualification,
    required this.joiningDate,
    required this.researchInterests,
    required this.bio,
  });
}

class _FacultyEditDialog extends StatefulWidget {
  final Faculty faculty;
  final Future<List<Department>> departmentsFuture;

  const _FacultyEditDialog({
    required this.faculty,
    required this.departmentsFuture,
  });

  @override
  State<_FacultyEditDialog> createState() => _FacultyEditDialogState();
}

class _FacultyEditDialogState extends State<_FacultyEditDialog> {
  final _formKey = GlobalKey<FormState>();

  late final TextEditingController _designationController;
  late final TextEditingController _qualificationController;
  late final TextEditingController _joiningDateController;
  late final TextEditingController _researchController;
  late final TextEditingController _bioController;

  late String _departmentId;

  @override
  void initState() {
    super.initState();

    _departmentId = widget.faculty.departmentId;

    _designationController = TextEditingController(
      text: widget.faculty.designation ?? '',
    );

    _qualificationController = TextEditingController(
      text: widget.faculty.qualification ?? '',
    );

    _joiningDateController = TextEditingController(
      text: widget.faculty.joiningDate ?? '',
    );

    _researchController = TextEditingController(
      text: widget.faculty.researchInterests ?? '',
    );

    _bioController = TextEditingController(text: widget.faculty.bio ?? '');
  }

  @override
  void dispose() {
    _designationController.dispose();
    _qualificationController.dispose();
    _joiningDateController.dispose();
    _researchController.dispose();
    _bioController.dispose();
    super.dispose();
  }

  String? _optional(String value) {
    final trimmed = value.trim();

    return trimmed.isEmpty ? null : trimmed;
  }

  Future<void> _pickDate() async {
    final initialDate =
        DateTime.tryParse(_joiningDateController.text) ?? DateTime.now();

    final picked = await showDatePicker(
      context: context,
      initialDate: initialDate,
      firstDate: DateTime(1950),
      lastDate: DateTime(2100),
    );

    if (picked == null) return;

    final month = picked.month.toString().padLeft(2, '0');

    final day = picked.day.toString().padLeft(2, '0');

    _joiningDateController.text = '${picked.year}-$month-$day';
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    try {
      final departments = await widget.departmentsFuture;

      if (!mounted) return;

      if (!departments.any((department) => department.id == _departmentId)) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please select a valid department.')),
        );
        return;
      }

      Navigator.of(context).pop(
        _FacultyEditData(
          departmentId: _departmentId,
          designation: _optional(_designationController.text),
          qualification: _optional(_qualificationController.text),
          joiningDate: _optional(_joiningDateController.text),
          researchInterests: _optional(_researchController.text),
          bio: _optional(_bioController.text),
        ),
      );
    } catch (error) {
      if (!mounted) return;

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error.toString())));
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Edit Faculty Profile'),
      content: SizedBox(
        width: 560,
        child: Form(
          key: _formKey,
          child: FutureBuilder<List<Department>>(
            future: widget.departmentsFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const SizedBox(
                  height: 120,
                  child: Center(child: CircularProgressIndicator()),
                );
              }

              if (snapshot.hasError) {
                return Text(snapshot.error.toString());
              }

              final departments = snapshot.data ?? const <Department>[];

              return SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    DropdownButtonFormField<String>(
                      initialValue:
                          departments.any(
                            (department) => department.id == _departmentId,
                          )
                          ? _departmentId
                          : null,
                      decoration: const InputDecoration(
                        labelText: 'Department',
                      ),
                      items: departments
                          .map(
                            (department) => DropdownMenuItem(
                              value: department.id,
                              child: Text(
                                '${department.name} (${department.code})',
                              ),
                            ),
                          )
                          .toList(),
                      onChanged: (value) {
                        if (value == null) return;

                        setState(() {
                          _departmentId = value;
                        });
                      },
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Select a department';
                        }

                        return null;
                      },
                    ),
                    const SizedBox(height: 12),

                    TextFormField(
                      controller: _designationController,
                      decoration: const InputDecoration(
                        labelText: 'Designation',
                      ),
                    ),
                    const SizedBox(height: 12),

                    TextFormField(
                      controller: _qualificationController,
                      decoration: const InputDecoration(
                        labelText: 'Qualification',
                      ),
                    ),
                    const SizedBox(height: 12),

                    TextFormField(
                      controller: _joiningDateController,
                      readOnly: true,
                      decoration: const InputDecoration(
                        labelText: 'Joining Date',
                        suffixIcon: Icon(Icons.calendar_today),
                      ),
                      onTap: _pickDate,
                    ),
                    const SizedBox(height: 12),

                    TextFormField(
                      controller: _researchController,
                      decoration: const InputDecoration(
                        labelText: 'Research Interests',
                      ),
                      maxLines: 3,
                    ),
                    const SizedBox(height: 12),

                    TextFormField(
                      controller: _bioController,
                      decoration: const InputDecoration(labelText: 'Biography'),
                      maxLines: 6,
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        FilledButton(onPressed: _submit, child: const Text('Save Changes')),
      ],
    );
  }
}
