import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../models/college.dart';
import '../models/patent.dart';
import '../models/tenant.dart';
import '../repository/tenant_config_repository.dart';

class FacultyPatentsScreen extends StatefulWidget {
  final Tenant tenant;
  final College college;
  final String facultyId;
  final String facultyName;

  const FacultyPatentsScreen({
    super.key,
    required this.tenant,
    required this.college,
    required this.facultyId,
    required this.facultyName,
  });

  @override
  State<FacultyPatentsScreen> createState() =>
      _FacultyPatentsScreenState();
}

class _FacultyPatentsScreenState
    extends State<FacultyPatentsScreen> {
  late final TenantConfigRepository _repository;
  late Future<List<Patent>> _patentsFuture;

  @override
  void initState() {
    super.initState();

    _repository = TenantConfigRepository(
      context.read<Dio>(),
    );

    _loadPatents();
  }

  void _loadPatents() {
    _patentsFuture = _repository.getPatents(
      tenantSlug: widget.tenant.slug,
      collegeId: widget.college.id,
      facultyId: widget.facultyId,
    );
  }

  Future<void> _addPatent() async {
    final result = await showDialog<_PatentFormData>(
      context: context,
      builder: (_) => const _PatentFormDialog(),
    );

    if (result == null || !mounted) return;

    try {
      await _repository.createPatent(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        facultyId: widget.facultyId,
        title: result.title,
        patentNumber: result.patentNumber,
        applicationNumber: result.applicationNumber,
        patentType: result.patentType,
        status: result.status,
        filingDate: result.filingDate,
        publicationDate: result.publicationDate,
        grantDate: result.grantDate,
        inventors: result.inventors,
        assignee: result.assignee,
        country: result.country,
        office: result.office,
        description: result.description,
        referenceUrl: result.referenceUrl,
      );

      if (!mounted) return;

      setState(_loadPatents);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Patent added successfully.'),
        ),
      );
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _editPatent(Patent patent) async {
    final result = await showDialog<_PatentFormData>(
      context: context,
      builder: (_) => _PatentFormDialog(
        patent: patent,
      ),
    );

    if (result == null || !mounted) return;

    try {
      await _repository.updatePatent(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        patentId: patent.id,
        title: result.title,
        patentNumber: result.patentNumber,
        applicationNumber: result.applicationNumber,
        patentType: result.patentType,
        status: result.status,
        filingDate: result.filingDate,
        publicationDate: result.publicationDate,
        grantDate: result.grantDate,
        inventors: result.inventors,
        assignee: result.assignee,
        country: result.country,
        office: result.office,
        description: result.description,
        referenceUrl: result.referenceUrl,
      );

      if (!mounted) return;

      setState(_loadPatents);
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _deletePatent(Patent patent) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Patent'),
        content: Text(
          'Delete "${patent.title}"?',
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
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    try {
      await _repository.deletePatent(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        patentId: patent.id,
      );

      if (!mounted) return;

      setState(_loadPatents);
    } catch (error) {
      _showError(error);
    }
  }

  void _showError(Object error) {
    if (!mounted) return;

    String message = error.toString();

    if (error is DioException) {
      final body = error.response?.data;

      if (body is Map<String, dynamic> &&
          body['detail'] != null) {
        message = body['detail'].toString();
      }
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 6),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Patents'),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _addPatent,
        icon: const Icon(Icons.add),
        label: const Text('Add Patent'),
      ),
      body: FutureBuilder<List<Patent>>(
        future: _patentsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState ==
              ConnectionState.waiting) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }

          if (snapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Text(
                  snapshot.error.toString(),
                  textAlign: TextAlign.center,
                ),
              ),
            );
          }

          final patents =
              snapshot.data ?? const <Patent>[];

          if (patents.isEmpty) {
            return const Center(
              child: Text(
                'No patents recorded yet.',
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(24),
            itemCount: patents.length,
            itemBuilder: (context, index) {
              final patent = patents[index];

              return Card(
                margin: const EdgeInsets.only(
                  bottom: 12,
                ),
                child: ListTile(
                  leading: const CircleAvatar(
                    child: Icon(
                      Icons.lightbulb_outline,
                    ),
                  ),
                  title: Text(patent.title),
                  subtitle: Text(
                    [
                      patent.patentType,
                      patent.status,
                      if (patent.patentNumber
                              ?.isNotEmpty ==
                          true)
                        patent.patentNumber!,
                    ].join(' • '),
                  ),
                  trailing: PopupMenuButton<String>(
                    onSelected: (value) {
                      if (value == 'edit') {
                        _editPatent(patent);
                      }
                      if (value == 'delete') {
                        _deletePatent(patent);
                      }
                    },
                    itemBuilder: (context) => const [
                      PopupMenuItem(
                        value: 'edit',
                        child: Text('Edit'),
                      ),
                      PopupMenuItem(
                        value: 'delete',
                        child: Text('Delete'),
                      ),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

class _PatentFormData {
  final String title;
  final String? patentNumber;
  final String? applicationNumber;
  final String patentType;
  final String status;
  final String? filingDate;
  final String? publicationDate;
  final String? grantDate;
  final String? inventors;
  final String? assignee;
  final String? country;
  final String? office;
  final String? description;
  final String? referenceUrl;

  const _PatentFormData({
    required this.title,
    required this.patentNumber,
    required this.applicationNumber,
    required this.patentType,
    required this.status,
    required this.filingDate,
    required this.publicationDate,
    required this.grantDate,
    required this.inventors,
    required this.assignee,
    required this.country,
    required this.office,
    required this.description,
    required this.referenceUrl,
  });
}

class _PatentFormDialog extends StatefulWidget {
  final Patent? patent;

  const _PatentFormDialog({
    this.patent,
  });

  @override
  State<_PatentFormDialog> createState() =>
      _PatentFormDialogState();
}

class _PatentFormDialogState
    extends State<_PatentFormDialog> {
  final _formKey = GlobalKey<FormState>();

  late final TextEditingController _titleController;
  late final TextEditingController _patentNumberController;
  late final TextEditingController _applicationNumberController;
  late final TextEditingController _patentTypeController;
  late final TextEditingController _statusController;
  late final TextEditingController _filingDateController;
  late final TextEditingController _publicationDateController;
  late final TextEditingController _grantDateController;
  late final TextEditingController _inventorsController;
  late final TextEditingController _assigneeController;
  late final TextEditingController _countryController;
  late final TextEditingController _officeController;
  late final TextEditingController _descriptionController;
  late final TextEditingController _urlController;

  @override
  void initState() {
    super.initState();

    final patent = widget.patent;

    _titleController =
        TextEditingController(text: patent?.title ?? '');
    _patentNumberController =
        TextEditingController(
      text: patent?.patentNumber ?? '',
    );
    _applicationNumberController =
        TextEditingController(
      text: patent?.applicationNumber ?? '',
    );
    _patentTypeController =
        TextEditingController(
      text: patent?.patentType ?? '',
    );
    _statusController =
        TextEditingController(
      text: patent?.status ?? '',
    );
    _filingDateController =
        TextEditingController(
      text: patent?.filingDate ?? '',
    );
    _publicationDateController =
        TextEditingController(
      text: patent?.publicationDate ?? '',
    );
    _grantDateController =
        TextEditingController(
      text: patent?.grantDate ?? '',
    );
    _inventorsController =
        TextEditingController(
      text: patent?.inventors ?? '',
    );
    _assigneeController =
        TextEditingController(
      text: patent?.assignee ?? '',
    );
    _countryController =
        TextEditingController(
      text: patent?.country ?? '',
    );
    _officeController =
        TextEditingController(
      text: patent?.office ?? '',
    );
    _descriptionController =
        TextEditingController(
      text: patent?.description ?? '',
    );
    _urlController =
        TextEditingController(
      text: patent?.referenceUrl ?? '',
    );
  }

  @override
  void dispose() {
    _titleController.dispose();
    _patentNumberController.dispose();
    _applicationNumberController.dispose();
    _patentTypeController.dispose();
    _statusController.dispose();
    _filingDateController.dispose();
    _publicationDateController.dispose();
    _grantDateController.dispose();
    _inventorsController.dispose();
    _assigneeController.dispose();
    _countryController.dispose();
    _officeController.dispose();
    _descriptionController.dispose();
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _pickDate(
    TextEditingController controller,
  ) async {
    final initialDate =
        DateTime.tryParse(controller.text) ??
        DateTime.now();

    final picked = await showDatePicker(
      context: context,
      initialDate: initialDate,
      firstDate: DateTime(1950),
      lastDate: DateTime.now(),
    );

    if (picked == null) return;

    final month =
        picked.month.toString().padLeft(2, '0');
    final day =
        picked.day.toString().padLeft(2, '0');

    controller.text =
        '${picked.year}-$month-$day';
  }

  String? _optional(String value) {
    final trimmed = value.trim();
    return trimmed.isEmpty ? null : trimmed;
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    Navigator.of(context).pop(
      _PatentFormData(
        title: _titleController.text.trim(),
        patentNumber:
            _optional(_patentNumberController.text),
        applicationNumber:
            _optional(
              _applicationNumberController.text,
            ),
        patentType:
            _patentTypeController.text.trim(),
        status: _statusController.text.trim(),
        filingDate:
            _optional(_filingDateController.text),
        publicationDate:
            _optional(
              _publicationDateController.text,
            ),
        grantDate:
            _optional(_grantDateController.text),
        inventors:
            _optional(_inventorsController.text),
        assignee:
            _optional(_assigneeController.text),
        country:
            _optional(_countryController.text),
        office:
            _optional(_officeController.text),
        description:
            _optional(_descriptionController.text),
        referenceUrl:
            _optional(_urlController.text),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final editing = widget.patent != null;

    return AlertDialog(
      title: Text(
        editing
            ? 'Edit Patent'
            : 'Add Patent',
      ),
      content: SizedBox(
        width: 560,
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  controller: _titleController,
                  decoration: const InputDecoration(
                    labelText: 'Title',
                  ),
                  validator: (value) {
                    if (value == null ||
                        value.trim().length < 2) {
                      return 'Enter a valid title';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _patentNumberController,
                  decoration: const InputDecoration(
                    labelText: 'Patent Number',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _applicationNumberController,
                  decoration: const InputDecoration(
                    labelText: 'Application Number',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _patentTypeController,
                  decoration: const InputDecoration(
                    labelText: 'Patent Type',
                    hintText: 'Indian / International',
                  ),
                  validator: (value) {
                    if (value == null ||
                        value.trim().length < 2) {
                      return 'Enter patent type';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _statusController,
                  decoration: const InputDecoration(
                    labelText: 'Status',
                    hintText:
                        'Filed / Published / Granted',
                  ),
                  validator: (value) {
                    if (value == null ||
                        value.trim().length < 2) {
                      return 'Enter patent status';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _filingDateController,
                  readOnly: true,
                  decoration: const InputDecoration(
                    labelText: 'Filing Date',
                    suffixIcon:
                        Icon(Icons.calendar_today),
                  ),
                  onTap: () => _pickDate(
                    _filingDateController,
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _publicationDateController,
                  readOnly: true,
                  decoration: const InputDecoration(
                    labelText: 'Publication Date',
                    suffixIcon:
                        Icon(Icons.calendar_today),
                  ),
                  onTap: () => _pickDate(
                    _publicationDateController,
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _grantDateController,
                  readOnly: true,
                  decoration: const InputDecoration(
                    labelText: 'Grant Date',
                    suffixIcon:
                        Icon(Icons.calendar_today),
                  ),
                  onTap: () => _pickDate(
                    _grantDateController,
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _inventorsController,
                  decoration: const InputDecoration(
                    labelText: 'Inventors',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _assigneeController,
                  decoration: const InputDecoration(
                    labelText: 'Assignee',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _countryController,
                  decoration: const InputDecoration(
                    labelText: 'Country',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _officeController,
                  decoration: const InputDecoration(
                    labelText: 'Patent Office',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _descriptionController,
                  decoration: const InputDecoration(
                    labelText: 'Description',
                  ),
                  maxLines: 3,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _urlController,
                  decoration: const InputDecoration(
                    labelText: 'Reference URL',
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
              Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: _submit,
          child: Text(
            editing ? 'Save' : 'Create',
          ),
        ),
      ],
    );
  }
}