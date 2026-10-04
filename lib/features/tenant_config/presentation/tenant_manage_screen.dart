import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../cubit/tenant_config_cubit.dart';
import '../cubit/tenant_config_state.dart';
import '../models/college.dart';
import '../models/tenant.dart';
import 'college_manage_screen.dart';
import '../repository/tenant_config_repository.dart';

class TenantManageScreen extends StatefulWidget {
  final Tenant tenant;

  const TenantManageScreen({super.key, required this.tenant});

  @override
  State<TenantManageScreen> createState() => _TenantManageScreenState();
}

class _TenantManageScreenState extends State<TenantManageScreen> {
  late final TenantConfigRepository _repository;
  late Future<List<College>> _collegesFuture;

  @override
  void initState() {
    super.initState();

    _repository = TenantConfigRepository(context.read<Dio>());

    _loadColleges();

    Future.microtask(() {
      if (!mounted) return;

      context.read<TenantConfigCubit>().loadTenantConfig(
        tenantId: widget.tenant.id,
      );
    });
  }

  void _loadColleges() {
    _collegesFuture = _repository.getColleges(tenantId: widget.tenant.id);
  }

  Future<void> _createCollege() async {
    final data = await showDialog<_CollegeFormData>(
      context: context,
      builder: (_) => const _CollegeFormDialog(),
    );

    if (data == null || !mounted) return;

    try {
      await _repository.createCollege(
        tenantId: widget.tenant.id,
        name: data.name,
        code: data.code,
        slug: data.slug,
      );

      if (!mounted) return;

      setState(_loadColleges);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('College created successfully.')),
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
      appBar: AppBar(title: Text(widget.tenant.name)),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _createCollege,
        icon: const Icon(Icons.add_business),
        label: const Text('Add College'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Text('Organization', style: Theme.of(context).textTheme.labelLarge),
          const SizedBox(height: 4),
          Text(
            widget.tenant.name,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 4),
          Text(widget.tenant.slug),
          const SizedBox(height: 32),

          Text('Colleges', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 12),

          FutureBuilder<List<College>>(
            future: _collegesFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(
                  child: Padding(
                    padding: EdgeInsets.all(32),
                    child: CircularProgressIndicator(),
                  ),
                );
              }

              if (snapshot.hasError) {
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        Text(
                          snapshot.error.toString(),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 12),
                        FilledButton(
                          onPressed: () {
                            setState(_loadColleges);
                          },
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                );
              }

              final colleges = snapshot.data ?? const <College>[];

              if (colleges.isEmpty) {
                return const Card(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Text('No colleges created yet.'),
                  ),
                );
              }

              return Column(
                children: [
                  for (final college in colleges)
                    Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ListTile(
                        leading: CircleAvatar(
                          child: Text(
                            college.name.isNotEmpty
                                ? college.name[0].toUpperCase()
                                : '?',
                          ),
                        ),
                        title: Text(college.name),
                        subtitle: Text('${college.code} • ${college.slug}'),
                        trailing: Icon(
                          college.isActive ? Icons.check_circle : Icons.cancel,
                          color: college.isActive ? Colors.green : Colors.red,
                        ),
                        onTap: () async {
                          await Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => CollegeManageScreen(
                                tenant: widget.tenant,
                                college: college,
                              ),
                            ),
                          );

                          if (!mounted) return;

                          setState(_loadColleges);
                        },
                      ),
                    ),
                ],
              );
            },
          ),

          const SizedBox(height: 32),

          BlocBuilder<TenantConfigCubit, TenantConfigState>(
            builder: (context, state) {
              if (state is! TenantConfigLoaded) {
                return const SizedBox();
              }

              final config = state.config;

              return ExpansionTile(
                title: const Text('Enabled Modules'),
                children: [
                  for (final module in config.enabledModules)
                    ListTile(
                      leading: const Icon(Icons.check_circle),
                      title: Text(module.name),
                      subtitle: Text(module.key),
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

class _CollegeFormData {
  final String name;
  final String code;
  final String slug;

  const _CollegeFormData({
    required this.name,
    required this.code,
    required this.slug,
  });
}

class _CollegeFormDialog extends StatefulWidget {
  const _CollegeFormDialog();

  @override
  State<_CollegeFormDialog> createState() => _CollegeFormDialogState();
}

class _CollegeFormDialogState extends State<_CollegeFormDialog> {
  final _formKey = GlobalKey<FormState>();

  final _nameController = TextEditingController();
  final _codeController = TextEditingController();
  final _slugController = TextEditingController();

  @override
  void dispose() {
    _nameController.dispose();
    _codeController.dispose();
    _slugController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    Navigator.of(context).pop(
      _CollegeFormData(
        name: _nameController.text.trim(),
        code: _codeController.text.trim().toUpperCase(),
        slug: _slugController.text.trim().toLowerCase(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Add College'),
      content: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'College Name',
                  hintText: 'Chhattisgarh Institute of Technology',
                ),
                validator: (value) {
                  if (value == null || value.trim().length < 2) {
                    return 'Enter a valid college name';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _codeController,
                decoration: const InputDecoration(
                  labelText: 'College Code',
                  hintText: 'CGIT',
                ),
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'Enter a college code';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _slugController,
                decoration: const InputDecoration(
                  labelText: 'College Slug',
                  hintText: 'cgit-raipur',
                ),
                validator: (value) {
                  if (value == null || value.trim().length < 2) {
                    return 'Enter a valid slug';
                  }

                  final regex = RegExp(r'^[a-z0-9\-]+$');

                  if (!regex.hasMatch(value.trim().toLowerCase())) {
                    return 'Use lowercase letters, numbers and hyphens only';
                  }

                  return null;
                },
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
        FilledButton(onPressed: _submit, child: const Text('Create')),
      ],
    );
  }
}
