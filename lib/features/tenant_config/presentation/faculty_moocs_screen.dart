import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../models/college.dart';
import '../models/mooc_completion.dart';
import '../models/tenant.dart';
import '../repository/tenant_config_repository.dart';

class FacultyMoocsScreen extends StatefulWidget {
  final Tenant tenant;
  final College college;
  final String userId;
  final String facultyName;

  const FacultyMoocsScreen({
    super.key,
    required this.tenant,
    required this.college,
    required this.userId,
    required this.facultyName,
  });

  @override
  State<FacultyMoocsScreen> createState() =>
      _FacultyMoocsScreenState();
}

class _FacultyMoocsScreenState
    extends State<FacultyMoocsScreen> {
  late final TenantConfigRepository _repository;
  late Future<List<MoocCompletion>> _moocsFuture;

  @override
  void initState() {
    super.initState();

    _repository = TenantConfigRepository(
      context.read<Dio>(),
    );

    _loadMoocs();
  }

  void _loadMoocs() {
    _moocsFuture = _repository.getMoocsForUser(
      tenantSlug: widget.tenant.slug,
      collegeId: widget.college.id,
      userId: widget.userId,
    );
  }

  Future<void> _addMooc() async {
    final data = await showDialog<_MoocFormData>(
      context: context,
      builder: (_) => const _MoocFormDialog(),
    );

    if (data == null || !mounted) return;

    try {
      await _repository.createMooc(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        userId: widget.userId,
        courseTitle: data.courseTitle,
        provider: data.provider,
        platform: data.platform,
        courseIdentifier: data.courseIdentifier,
        durationHours: data.durationHours,
        enrolledOn: data.enrolledOn,
        completedOn: data.completedOn,
        certificateId: data.certificateId,
        certificateUrl: data.certificateUrl,
        score: data.score,
        status: data.status,
        description: data.description,
      );

      if (!mounted) return;

      setState(_loadMoocs);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'MOOC completion added successfully.',
          ),
        ),
      );
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _editMooc(
    MoocCompletion mooc,
  ) async {
    final data = await showDialog<_MoocFormData>(
      context: context,
      builder: (_) => _MoocFormDialog(
        mooc: mooc,
      ),
    );

    if (data == null || !mounted) return;

    try {
      await _repository.updateMooc(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        completionId: mooc.id,
        courseTitle: data.courseTitle,
        provider: data.provider,
        platform: data.platform,
        courseIdentifier: data.courseIdentifier,
        durationHours: data.durationHours,
        enrolledOn: data.enrolledOn,
        completedOn: data.completedOn,
        certificateId: data.certificateId,
        certificateUrl: data.certificateUrl,
        score: data.score,
        status: data.status,
        description: data.description,
      );

      if (!mounted) return;

      setState(_loadMoocs);
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _deleteMooc(
    MoocCompletion mooc,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete MOOC Completion'),
        content: Text(
          'Delete "${mooc.courseTitle}"?',
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

    if (confirmed != true || !mounted) {
      return;
    }

    try {
      await _repository.deleteMooc(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        completionId: mooc.id,
      );

      if (!mounted) return;

      setState(_loadMoocs);
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
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('MOOC Completions'),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _addMooc,
        icon: const Icon(Icons.add),
        label: const Text('Add MOOC'),
      ),
      body: FutureBuilder<List<MoocCompletion>>(
        future: _moocsFuture,
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
                        setState(_loadMoocs);
                      },
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            );
          }

          final moocs =
              snapshot.data ?? const <MoocCompletion>[];

          if (moocs.isEmpty) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: Text(
                  'No MOOC completions recorded yet.',
                ),
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(24),
            itemCount: moocs.length,
            itemBuilder: (context, index) {
              final mooc = moocs[index];

              return Card(
                margin: const EdgeInsets.only(
                  bottom: 12,
                ),
                child: ListTile(
                  leading: const CircleAvatar(
                    child: Icon(
                      Icons.ondemand_video_outlined,
                    ),
                  ),
                  title: Text(mooc.courseTitle),
                  subtitle: Text(
                    [
                      if (mooc.provider?.isNotEmpty == true)
                        mooc.provider!,
                      if (mooc.platform?.isNotEmpty == true)
                        mooc.platform!,
                      if (mooc.completedOn?.isNotEmpty == true)
                        'Completed ${mooc.completedOn}',
                      if (mooc.score != null)
                        'Score ${mooc.score!.toStringAsFixed(1)}%',
                    ].join(' • '),
                  ),
                  trailing: PopupMenuButton<String>(
                    onSelected: (value) {
                      if (value == 'edit') {
                        _editMooc(mooc);
                      }

                      if (value == 'delete') {
                        _deleteMooc(mooc);
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

class _MoocFormData {
  final String courseTitle;
  final String? provider;
  final String? platform;
  final String? courseIdentifier;
  final double? durationHours;
  final String? enrolledOn;
  final String? completedOn;
  final String? certificateId;
  final String? certificateUrl;
  final double? score;
  final String status;
  final String? description;

  const _MoocFormData({
    required this.courseTitle,
    required this.provider,
    required this.platform,
    required this.courseIdentifier,
    required this.durationHours,
    required this.enrolledOn,
    required this.completedOn,
    required this.certificateId,
    required this.certificateUrl,
    required this.score,
    required this.status,
    required this.description,
  });
}

class _MoocFormDialog extends StatefulWidget {
  final MoocCompletion? mooc;

  const _MoocFormDialog({
    this.mooc,
  });

  @override
  State<_MoocFormDialog> createState() =>
      _MoocFormDialogState();
}

class _MoocFormDialogState
    extends State<_MoocFormDialog> {
  final _formKey = GlobalKey<FormState>();

  late final TextEditingController _courseTitleController;
  late final TextEditingController _providerController;
  late final TextEditingController _platformController;
  late final TextEditingController _identifierController;
  late final TextEditingController _durationController;
  late final TextEditingController _enrolledController;
  late final TextEditingController _completedController;
  late final TextEditingController _certificateIdController;
  late final TextEditingController _certificateUrlController;
  late final TextEditingController _scoreController;
  late final TextEditingController _descriptionController;

  String _status = 'completed';

  @override
  void initState() {
    super.initState();

    final mooc = widget.mooc;

    _courseTitleController = TextEditingController(
      text: mooc?.courseTitle ?? '',
    );
    _providerController = TextEditingController(
      text: mooc?.provider ?? '',
    );
    _platformController = TextEditingController(
      text: mooc?.platform ?? '',
    );
    _identifierController = TextEditingController(
      text: mooc?.courseIdentifier ?? '',
    );
    _durationController = TextEditingController(
      text: mooc?.durationHours?.toString() ?? '',
    );
    _enrolledController = TextEditingController(
      text: mooc?.enrolledOn ?? '',
    );
    _completedController = TextEditingController(
      text: mooc?.completedOn ?? '',
    );
    _certificateIdController = TextEditingController(
      text: mooc?.certificateId ?? '',
    );
    _certificateUrlController = TextEditingController(
      text: mooc?.certificateUrl ?? '',
    );
    _scoreController = TextEditingController(
      text: mooc?.score?.toString() ?? '',
    );
    _descriptionController = TextEditingController(
      text: mooc?.description ?? '',
    );

    _status = mooc?.status ?? 'completed';
  }

  @override
  void dispose() {
    _courseTitleController.dispose();
    _providerController.dispose();
    _platformController.dispose();
    _identifierController.dispose();
    _durationController.dispose();
    _enrolledController.dispose();
    _completedController.dispose();
    _certificateIdController.dispose();
    _certificateUrlController.dispose();
    _scoreController.dispose();
    _descriptionController.dispose();
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
      lastDate: DateTime(2100),
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

  final durationText =
      _durationController.text.trim();

  final scoreText =
      _scoreController.text.trim();

  final duration = durationText.isEmpty
      ? null
      : double.tryParse(durationText);

  if (durationText.isNotEmpty &&
      (duration == null || duration < 0)) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
          'Duration must be a valid number greater than or equal to 0.',
        ),
      ),
    );
    return;
  }

  final score = scoreText.isEmpty
      ? null
      : double.tryParse(scoreText);

  if (scoreText.isNotEmpty &&
      (score == null || score < 0 || score > 100)) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
          'Score must be a number between 0 and 100.',
        ),
      ),
    );
    return;
  }

  Navigator.of(context).pop(
    _MoocFormData(
      courseTitle:
          _courseTitleController.text.trim(),
      provider:
          _optional(_providerController.text),
      platform:
          _optional(_platformController.text),
      courseIdentifier:
          _optional(_identifierController.text),
      durationHours: duration,
      enrolledOn:
          _optional(_enrolledController.text),
      completedOn:
          _optional(_completedController.text),
      certificateId:
          _optional(_certificateIdController.text),
      certificateUrl:
          _optional(_certificateUrlController.text),
      score: score,
      status: _status,
      description:
          _optional(_descriptionController.text),
    ),
  );
}

  @override
  Widget build(BuildContext context) {
    final editing = widget.mooc != null;

    return AlertDialog(
      title: Text(
        editing
            ? 'Edit MOOC Completion'
            : 'Add MOOC Completion',
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
                  controller: _courseTitleController,
                  decoration: const InputDecoration(
                    labelText: 'Course Title',
                  ),
                  validator: (value) {
                    if (value == null ||
                        value.trim().length < 2) {
                      return 'Enter a valid course title';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _providerController,
                  decoration: const InputDecoration(
                    labelText: 'Provider',
                    hintText: 'NPTEL',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _platformController,
                  decoration: const InputDecoration(
                    labelText: 'Platform',
                    hintText: 'SWAYAM',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _identifierController,
                  decoration: const InputDecoration(
                    labelText: 'Course Identifier',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _durationController,
                  keyboardType:
                      const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: const InputDecoration(
                    labelText: 'Duration Hours',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _enrolledController,
                  readOnly: true,
                  decoration: const InputDecoration(
                    labelText: 'Enrolled On',
                    suffixIcon:
                        Icon(Icons.calendar_today),
                  ),
                  onTap: () =>
                      _pickDate(_enrolledController),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _completedController,
                  readOnly: true,
                  decoration: const InputDecoration(
                    labelText: 'Completed On',
                    suffixIcon:
                        Icon(Icons.calendar_today),
                  ),
                  onTap: () =>
                      _pickDate(_completedController),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _certificateIdController,
                  decoration: const InputDecoration(
                    labelText: 'Certificate ID',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _certificateUrlController,
                  decoration: const InputDecoration(
                    labelText: 'Certificate URL',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _scoreController,
                  keyboardType:
                      const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: const InputDecoration(
                    labelText: 'Score',
                    hintText: '0-100',
                  ),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: _status,
                  decoration: const InputDecoration(
                    labelText: 'Status',
                  ),
                  items: const [
                    DropdownMenuItem(
                      value: 'completed',
                      child: Text('Completed'),
                    ),
                    DropdownMenuItem(
                      value: 'in_progress',
                      child: Text('In Progress'),
                    ),
                    DropdownMenuItem(
                      value: 'enrolled',
                      child: Text('Enrolled'),
                    ),
                  ],
                  onChanged: (value) {
                    if (value == null) return;

                    setState(() {
                      _status = value;
                    });
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _descriptionController,
                  decoration: const InputDecoration(
                    labelText: 'Description',
                  ),
                  maxLines: 4,
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