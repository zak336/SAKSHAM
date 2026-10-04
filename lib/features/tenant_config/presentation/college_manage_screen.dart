import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../models/college.dart';
import '../models/department.dart';
import '../models/faculty.dart';
import '../models/tenant.dart';
import '../models/user.dart';
import '../repository/tenant_config_repository.dart';
import 'faculty_profile_screen.dart';

class CollegeManageScreen extends StatefulWidget {
  final Tenant tenant;
  final College college;

  const CollegeManageScreen({
    super.key,
    required this.tenant,
    required this.college,
  });

  @override
  State<CollegeManageScreen> createState() => _CollegeManageScreenState();
}

class _CollegeManageScreenState extends State<CollegeManageScreen> {
  late final TenantConfigRepository _repository;

  late Future<List<Department>> _departmentsFuture;
  late Future<_CollegeData> _collegeDataFuture;

  @override
  void initState() {
    super.initState();

    _repository = TenantConfigRepository(context.read<Dio>());

    _loadData();
  }

  void _loadData() {
    _departmentsFuture = _repository.getDepartments(
      tenantSlug: widget.tenant.slug,
      collegeId: widget.college.id,
    );

    _collegeDataFuture = _loadCollegeData();
  }

  Future<_CollegeData> _loadCollegeData() async {
    final results = await Future.wait([
      _repository.getFaculty(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
      ),
      _repository.getUsers(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
      ),
    ]);

    return _CollegeData(
      faculty: results[0] as List<Faculty>,
      users: results[1] as List<User>,
    );
  }

  void _reload() {
    setState(_loadData);
  }

  Future<void> _createDepartment() async {
    final data = await showDialog<_DepartmentFormData>(
      context: context,
      builder: (_) => const _DepartmentFormDialog(),
    );

    if (data == null || !mounted) return;

    try {
      await _repository.createDepartment(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        name: data.name,
        code: data.code,
      );

      if (!mounted) return;

      _reload();

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Department created successfully.')),
      );
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _createFaculty() async {
    final departments = await _departmentsFuture;

    if (!mounted) return;

    if (departments.isEmpty) {
      _showError('Create a department before adding faculty.');
      return;
    }

    final data = await showDialog<_FacultyFormData>(
      context: context,
      builder: (_) => _FacultyFormDialog(departments: departments),
    );

    if (data == null || !mounted) return;

    try {
      final user = await _repository.createUser(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        name: data.name,
        email: data.email,
        password: data.password,
        phone: data.phone,
        role: 'faculty',
      );

      await _repository.createFaculty(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        userId: user.id,
        departmentId: data.departmentId,
        designation: data.designation,
        qualification: data.qualification,
        joiningDate: data.joiningDate,
        researchInterests: data.researchInterests,
        bio: data.bio,
      );

      if (!mounted) return;

      _reload();

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Faculty created successfully.')),
      );
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _createCollegeAdmin() async {
    final data = await showDialog<_CollegeAdminFormData>(
      context: context,
      builder: (_) => const _CollegeAdminFormDialog(),
    );

    if (data == null || !mounted) return;

    try {
      await _repository.createUser(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        name: data.name,
        email: data.email,
        password: data.password,
        phone: data.phone,
        role: 'admin',
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('College Admin created successfully.')),
      );
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _toggleFaculty(User user) async {
    final nextState = !user.isActive;

    try {
      await _repository.updateUser(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        userId: user.id,
        isActive: nextState,
      );

      if (!mounted) return;

      _reload();

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            nextState ? '${user.name} activated.' : '${user.name} deactivated.',
          ),
        ),
      );
    } catch (error) {
      _showError(error);
    }
  }

  void _showError(Object error) {
    if (!mounted) return;

    String message = error.toString();

    if (error is DioException) {
      final body = error.response?.data;

      if (body is Map<String, dynamic> && body['detail'] != null) {
        message = body['detail'].toString();
      }
    }

    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.college.name)),
      floatingActionButton: PopupMenuButton<String>(
        onSelected: (value) {
          switch (value) {
            case 'department':
              _createDepartment();
              break;
            case 'faculty':
              _createFaculty();
              break;
            case 'admin':
              _createCollegeAdmin();
              break;
          }
        },
        itemBuilder: (context) => const [
          PopupMenuItem(value: 'department', child: Text('Add Department')),
          PopupMenuItem(value: 'faculty', child: Text('Add Faculty')),
          PopupMenuItem(value: 'admin', child: Text('Add College Admin')),
        ],
        child: FloatingActionButton.extended(
          onPressed: null,
          icon: const Icon(Icons.add),
          label: const Text('Add'),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Text(
            widget.college.name,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 4),
          Text('${widget.college.code} • ${widget.college.slug}'),
          const SizedBox(height: 32),

          Text('Departments', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 12),

          FutureBuilder<List<Department>>(
            future: _departmentsFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Card(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Center(child: CircularProgressIndicator()),
                  ),
                );
              }

              if (snapshot.hasError) {
                return _ErrorCard(error: snapshot.error!, onRetry: _reload);
              }

              final departments = snapshot.data ?? const <Department>[];

              if (departments.isEmpty) {
                return const Card(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Text('No departments created yet.'),
                  ),
                );
              }

              return Column(
                children: [
                  for (final department in departments)
                    Card(
                      margin: const EdgeInsets.only(bottom: 10),
                      child: ListTile(
                        leading: CircleAvatar(
                          child: Text(
                            department.code.isNotEmpty
                                ? department.code[0]
                                : '?',
                          ),
                        ),
                        title: Text(department.name),
                        subtitle: Text(department.code),
                        trailing: Icon(
                          department.isActive
                              ? Icons.check_circle
                              : Icons.cancel,
                          color: department.isActive
                              ? Colors.green
                              : Colors.red,
                        ),
                      ),
                    ),
                ],
              );
            },
          ),

          const SizedBox(height: 32),

          Row(
            children: [
              Text('Faculty', style: Theme.of(context).textTheme.titleLarge),
              const Spacer(),
              FilledButton.icon(
                onPressed: _createFaculty,
                icon: const Icon(Icons.person_add),
                label: const Text('Add Faculty'),
              ),
            ],
          ),

          const SizedBox(height: 12),

          FutureBuilder<_CollegeData>(
            future: _collegeDataFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Card(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Center(child: CircularProgressIndicator()),
                  ),
                );
              }

              if (snapshot.hasError) {
                return _ErrorCard(error: snapshot.error!, onRetry: _reload);
              }

              final data = snapshot.data!;

              if (data.faculty.isEmpty) {
                return const Card(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Text('No faculty profiles created yet.'),
                  ),
                );
              }

              return Column(
                children: [
                  for (final faculty in data.faculty)
                    Builder(
                      builder: (context) {
                        User? user;

                        for (final item in data.users) {
                          if (item.id == faculty.userId) {
                            user = item;
                            break;
                          }
                        }

                        if (user == null) {
                          return const SizedBox.shrink();
                        }

                        final facultyUser = user;

                        return Card(
                          margin: const EdgeInsets.only(bottom: 10),
                          child: ListTile(
                            leading: const CircleAvatar(
                              child: Icon(Icons.person),
                            ),

                            title: Text(facultyUser.name),

                            subtitle: Text(
                              [
                                if (faculty.designation?.isNotEmpty == true)
                                  faculty.designation!,
                                if (faculty.qualification?.isNotEmpty == true)
                                  faculty.qualification!,
                              ].join(' • '),
                            ),

                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(
                                  facultyUser.isActive
                                      ? Icons.check_circle
                                      : Icons.cancel,
                                  color: facultyUser.isActive
                                      ? Colors.green
                                      : Colors.red,
                                ),
                                const SizedBox(width: 8),
                                Switch(
                                  value: facultyUser.isActive,
                                  onChanged: (_) {
                                    _toggleFaculty(facultyUser);
                                  },
                                ),
                                const SizedBox(width: 4),
                                const Icon(Icons.chevron_right),
                              ],
                            ),

                            onTap: () {
                              Navigator.of(context).push(
                                MaterialPageRoute(
                                  builder: (_) => FacultyProfileScreen(
                                    tenant: widget.tenant,
                                    college: widget.college,
                                    facultyId: faculty.id,
                                    facultyName: facultyUser.name,
                                  ),
                                ),
                              );
                            },
                          ),
                        );
                      },
                    ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}

class _CollegeData {
  final List<Faculty> faculty;
  final List<User> users;

  const _CollegeData({required this.faculty, required this.users});
}

class _ErrorCard extends StatelessWidget {
  final Object error;
  final VoidCallback onRetry;

  const _ErrorCard({required this.error, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Text(error.toString(), textAlign: TextAlign.center),
            const SizedBox(height: 12),
            FilledButton(onPressed: onRetry, child: const Text('Retry')),
          ],
        ),
      ),
    );
  }
}

class _DepartmentFormData {
  final String name;
  final String code;

  const _DepartmentFormData({required this.name, required this.code});
}

class _DepartmentFormDialog extends StatefulWidget {
  const _DepartmentFormDialog();

  @override
  State<_DepartmentFormDialog> createState() => _DepartmentFormDialogState();
}

class _DepartmentFormDialogState extends State<_DepartmentFormDialog> {
  final _formKey = GlobalKey<FormState>();

  final _nameController = TextEditingController();

  final _codeController = TextEditingController();

  @override
  void dispose() {
    _nameController.dispose();
    _codeController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    Navigator.of(context).pop(
      _DepartmentFormData(
        name: _nameController.text.trim(),
        code: _codeController.text.trim().toUpperCase(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Add Department'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(labelText: 'Department Name'),
              validator: (value) {
                if (value == null || value.trim().length < 2) {
                  return 'Enter a valid department name';
                }
                return null;
              },
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _codeController,
              decoration: const InputDecoration(labelText: 'Department Code'),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Enter a department code';
                }
                return null;
              },
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        FilledButton(onPressed: _submit, child: const Text('Create')),
      ],
    );
  }
}

class _FacultyFormData {
  final String name;
  final String email;
  final String password;
  final String? phone;
  final String departmentId;
  final String? designation;
  final String? qualification;
  final String? joiningDate;
  final String? researchInterests;
  final String? bio;

  const _FacultyFormData({
    required this.name,
    required this.email,
    required this.password,
    required this.phone,
    required this.departmentId,
    required this.designation,
    required this.qualification,
    required this.joiningDate,
    required this.researchInterests,
    required this.bio,
  });
}

class _FacultyFormDialog extends StatefulWidget {
  final List<Department> departments;

  const _FacultyFormDialog({required this.departments});

  @override
  State<_FacultyFormDialog> createState() => _FacultyFormDialogState();
}

class _FacultyFormDialogState extends State<_FacultyFormDialog> {
  final _formKey = GlobalKey<FormState>();

  final _nameController = TextEditingController();

  final _emailController = TextEditingController();

  final _passwordController = TextEditingController();

  final _phoneController = TextEditingController();

  final _designationController = TextEditingController();

  final _qualificationController = TextEditingController();

  final _joiningDateController = TextEditingController();

  final _researchController = TextEditingController();

  final _bioController = TextEditingController();

  late String _departmentId;

  @override
  void initState() {
    super.initState();

    _departmentId = widget.departments.first.id;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _phoneController.dispose();
    _designationController.dispose();
    _qualificationController.dispose();
    _joiningDateController.dispose();
    _researchController.dispose();
    _bioController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    Navigator.of(context).pop(
      _FacultyFormData(
        name: _nameController.text.trim(),
        email: _emailController.text.trim(),
        password: _passwordController.text,
        phone: _phoneController.text.trim().isEmpty
            ? null
            : _phoneController.text.trim(),
        departmentId: _departmentId,
        designation: _designationController.text.trim().isEmpty
            ? null
            : _designationController.text.trim(),
        qualification: _qualificationController.text.trim().isEmpty
            ? null
            : _qualificationController.text.trim(),
        joiningDate: _joiningDateController.text.trim().isEmpty
            ? null
            : _joiningDateController.text.trim(),
        researchInterests: _researchController.text.trim().isEmpty
            ? null
            : _researchController.text.trim(),
        bio: _bioController.text.trim().isEmpty
            ? null
            : _bioController.text.trim(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Add Faculty'),
      content: SizedBox(
        width: 520,
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: _nameController,
                  decoration: const InputDecoration(labelText: 'Name'),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Enter a name';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _emailController,
                  decoration: const InputDecoration(labelText: 'Email'),
                  keyboardType: TextInputType.emailAddress,
                  validator: (value) {
                    if (value == null || !value.contains('@')) {
                      return 'Enter a valid email';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _passwordController,
                  decoration: const InputDecoration(labelText: 'Password'),
                  obscureText: true,
                  validator: (value) {
                    if (value == null || value.length < 8) {
                      return 'Password must be at least 8 characters';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _phoneController,
                  decoration: const InputDecoration(labelText: 'Phone'),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: _departmentId,
                  decoration: const InputDecoration(labelText: 'Department'),
                  items: widget.departments
                      .map(
                        (department) => DropdownMenuItem(
                          value: department.id,
                          child: Text(department.name),
                        ),
                      )
                      .toList(),
                  onChanged: (value) {
                    if (value == null) return;

                    setState(() {
                      _departmentId = value;
                    });
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _designationController,
                  decoration: const InputDecoration(labelText: 'Designation'),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _qualificationController,
                  decoration: const InputDecoration(labelText: 'Qualification'),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _joiningDateController,
                  decoration: const InputDecoration(
                    labelText: 'Joining Date (YYYY-MM-DD)',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _researchController,
                  decoration: const InputDecoration(
                    labelText: 'Research Interests',
                  ),
                  maxLines: 2,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _bioController,
                  decoration: const InputDecoration(labelText: 'Bio'),
                  maxLines: 3,
                ),
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        FilledButton(onPressed: _submit, child: const Text('Create Faculty')),
      ],
    );
  }
}

class _CollegeAdminFormData {
  final String name;
  final String email;
  final String password;
  final String? phone;

  const _CollegeAdminFormData({
    required this.name,
    required this.email,
    required this.password,
    required this.phone,
  });
}

class _CollegeAdminFormDialog extends StatefulWidget {
  const _CollegeAdminFormDialog();

  @override
  State<_CollegeAdminFormDialog> createState() =>
      _CollegeAdminFormDialogState();
}

class _CollegeAdminFormDialogState extends State<_CollegeAdminFormDialog> {
  final _formKey = GlobalKey<FormState>();

  final _nameController = TextEditingController();

  final _emailController = TextEditingController();

  final _passwordController = TextEditingController();

  final _phoneController = TextEditingController();

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    Navigator.of(context).pop(
      _CollegeAdminFormData(
        name: _nameController.text.trim(),
        email: _emailController.text.trim(),
        password: _passwordController.text,
        phone: _phoneController.text.trim().isEmpty
            ? null
            : _phoneController.text.trim(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Add College Admin'),
      content: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Name'),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Enter a name';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(labelText: 'Email'),
                validator: (value) {
                  if (value == null || !value.contains('@')) {
                    return 'Enter a valid email';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _passwordController,
                obscureText: true,
                decoration: const InputDecoration(labelText: 'Password'),
                validator: (value) {
                  if (value == null || value.length < 8) {
                    return 'Password must be at least 8 characters';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _phoneController,
                decoration: const InputDecoration(labelText: 'Phone'),
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        FilledButton(onPressed: _submit, child: const Text('Create Admin')),
      ],
    );
  }
}
