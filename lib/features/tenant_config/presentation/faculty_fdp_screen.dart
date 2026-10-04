import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../models/college.dart';
import '../models/faculty_development_program.dart';
import '../models/tenant.dart';
import '../repository/tenant_config_repository.dart';

class FacultyFdpScreen extends StatefulWidget {
  final Tenant tenant;
  final College college;
  final String facultyId;
  final String facultyName;

  const FacultyFdpScreen({
    super.key,
    required this.tenant,
    required this.college,
    required this.facultyId,
    required this.facultyName,
  });

  @override
  State<FacultyFdpScreen> createState() =>
      _FacultyFdpScreenState();
}

class _FacultyFdpScreenState
    extends State<FacultyFdpScreen> {
  late final TenantConfigRepository _repository;
  late Future<List<FacultyDevelopmentProgram>> _fdpsFuture;

  @override
  void initState() {
    super.initState();

    _repository = TenantConfigRepository(
      context.read<Dio>(),
    );

    _loadFdps();
  }

  void _loadFdps() {
    _fdpsFuture = _repository.getFdps(
      tenantSlug: widget.tenant.slug,
      collegeId: widget.college.id,
      facultyId: widget.facultyId,
    );
  }

  Future<void> _addFdp() async {
    final data = await showDialog<_FdpFormData>(
      context: context,
      builder: (_) => const _FdpFormDialog(),
    );

    if (data == null || !mounted) return;

    try {
      await _repository.createFdp(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        facultyId: widget.facultyId,
        title: data.title,
        organizer: data.organizer,
        programType: data.programType,
        mode: data.mode,
        venue: data.venue,
        startDate: data.startDate,
        endDate: data.endDate,
        durationHours: data.durationHours,
        certificateNumber: data.certificateNumber,
        certificateUrl: data.certificateUrl,
        description: data.description,
      );

      if (!mounted) return;

      setState(_loadFdps);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Faculty development program added successfully.',
          ),
        ),
      );
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _editFdp(
    FacultyDevelopmentProgram fdp,
  ) async {
    final data = await showDialog<_FdpFormData>(
      context: context,
      builder: (_) => _FdpFormDialog(
        fdp: fdp,
      ),
    );

    if (data == null || !mounted) return;

    try {
      await _repository.updateFdp(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        fdpId: fdp.id,
        title: data.title,
        organizer: data.organizer,
        programType: data.programType,
        mode: data.mode,
        venue: data.venue,
        startDate: data.startDate,
        endDate: data.endDate,
        durationHours: data.durationHours,
        certificateNumber: data.certificateNumber,
        certificateUrl: data.certificateUrl,
        description: data.description,
      );

      if (!mounted) return;

      setState(_loadFdps);
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _deleteFdp(
    FacultyDevelopmentProgram fdp,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text(
          'Delete FDP',
        ),
        content: Text(
          'Delete "${fdp.title}"?',
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
      await _repository.deleteFdp(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        fdpId: fdp.id,
      );

      if (!mounted) return;

      setState(_loadFdps);
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
        title: const Text(
          'Faculty Development Programs',
        ),
      ),
      floatingActionButton:
          FloatingActionButton.extended(
        onPressed: _addFdp,
        icon: const Icon(Icons.add),
        label: const Text('Add FDP'),
      ),
      body:
          FutureBuilder<List<FacultyDevelopmentProgram>>(
        future: _fdpsFuture,
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
                        setState(_loadFdps);
                      },
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            );
          }

          final fdps =
              snapshot.data ??
                  const <FacultyDevelopmentProgram>[];

          if (fdps.isEmpty) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: Text(
                  'No faculty development programs recorded yet.',
                ),
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(24),
            itemCount: fdps.length,
            itemBuilder: (context, index) {
              final fdp = fdps[index];

              return Card(
                margin: const EdgeInsets.only(
                  bottom: 12,
                ),
                child: ListTile(
                  leading: const CircleAvatar(
                    child: Icon(
                      Icons.workspace_premium_outlined,
                    ),
                  ),
                  title: Text(fdp.title),
                  subtitle: Text(
                    [
                      if (fdp.organizer?.isNotEmpty == true)
                        fdp.organizer!,
                      if (fdp.programType?.isNotEmpty == true)
                        fdp.programType!,
                      if (fdp.mode?.isNotEmpty == true)
                        fdp.mode!,
                      if (fdp.startDate?.isNotEmpty == true)
                        fdp.startDate!,
                      if (fdp.endDate?.isNotEmpty == true)
                        fdp.endDate!,
                      if (fdp.durationHours != null)
                        '${fdp.durationHours} hrs',
                    ].join(' • '),
                  ),
                  trailing: PopupMenuButton<String>(
                    onSelected: (value) {
                      if (value == 'edit') {
                        _editFdp(fdp);
                      }

                      if (value == 'delete') {
                        _deleteFdp(fdp);
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

class _FdpFormData {
  final String title;
  final String? organizer;
  final String? programType;
  final String? mode;
  final String? venue;
  final String? startDate;
  final String? endDate;
  final double? durationHours;
  final String? certificateNumber;
  final String? certificateUrl;
  final String? description;

  const _FdpFormData({
    required this.title,
    required this.organizer,
    required this.programType,
    required this.mode,
    required this.venue,
    required this.startDate,
    required this.endDate,
    required this.durationHours,
    required this.certificateNumber,
    required this.certificateUrl,
    required this.description,
  });
}

class _FdpFormDialog extends StatefulWidget {
  final FacultyDevelopmentProgram? fdp;

  const _FdpFormDialog({
    this.fdp,
  });

  @override
  State<_FdpFormDialog> createState() =>
      _FdpFormDialogState();
}

class _FdpFormDialogState
    extends State<_FdpFormDialog> {
  final _formKey =
      GlobalKey<FormState>();

  late final TextEditingController _titleController;
  late final TextEditingController _organizerController;
  late final TextEditingController _programTypeController;
  late final TextEditingController _modeController;
  late final TextEditingController _venueController;
  late final TextEditingController _startDateController;
  late final TextEditingController _endDateController;
  late final TextEditingController _durationController;
  late final TextEditingController _certificateNumberController;
  late final TextEditingController _certificateUrlController;
  late final TextEditingController _descriptionController;

  @override
  void initState() {
    super.initState();

    final fdp = widget.fdp;

    _titleController = TextEditingController(
      text: fdp?.title ?? '',
    );

    _organizerController = TextEditingController(
      text: fdp?.organizer ?? '',
    );

    _programTypeController = TextEditingController(
      text: fdp?.programType ?? '',
    );

    _modeController = TextEditingController(
      text: fdp?.mode ?? '',
    );

    _venueController = TextEditingController(
      text: fdp?.venue ?? '',
    );

    _startDateController = TextEditingController(
      text: fdp?.startDate ?? '',
    );

    _endDateController = TextEditingController(
      text: fdp?.endDate ?? '',
    );

    _durationController = TextEditingController(
      text: fdp?.durationHours?.toString() ?? '',
    );

    _certificateNumberController =
        TextEditingController(
      text: fdp?.certificateNumber ?? '',
    );

    _certificateUrlController =
        TextEditingController(
      text: fdp?.certificateUrl ?? '',
    );

    _descriptionController =
        TextEditingController(
      text: fdp?.description ?? '',
    );
  }

  @override
  void dispose() {
    _titleController.dispose();
    _organizerController.dispose();
    _programTypeController.dispose();
    _modeController.dispose();
    _venueController.dispose();
    _startDateController.dispose();
    _endDateController.dispose();
    _durationController.dispose();
    _certificateNumberController.dispose();
    _certificateUrlController.dispose();
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

    return trimmed.isEmpty
        ? null
        : trimmed;
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final durationText =
        _durationController.text.trim();

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

    Navigator.of(context).pop(
      _FdpFormData(
        title: _titleController.text.trim(),
        organizer:
            _optional(_organizerController.text),
        programType:
            _optional(_programTypeController.text),
        mode:
            _optional(_modeController.text),
        venue:
            _optional(_venueController.text),
        startDate:
            _optional(_startDateController.text),
        endDate:
            _optional(_endDateController.text),
        durationHours: duration,
        certificateNumber:
            _optional(
          _certificateNumberController.text,
        ),
        certificateUrl:
            _optional(
          _certificateUrlController.text,
        ),
        description:
            _optional(_descriptionController.text),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final editing = widget.fdp != null;

    return AlertDialog(
      title: Text(
        editing
            ? 'Edit FDP'
            : 'Add Faculty Development Program',
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
                  controller: _organizerController,
                  decoration: const InputDecoration(
                    labelText: 'Organizer',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _programTypeController,
                  decoration: const InputDecoration(
                    labelText: 'Program Type',
                    hintText: 'FDP',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _modeController,
                  decoration: const InputDecoration(
                    labelText: 'Mode',
                    hintText: 'Online / Offline / Hybrid',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _venueController,
                  decoration: const InputDecoration(
                    labelText: 'Venue',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _startDateController,
                  readOnly: true,
                  decoration: const InputDecoration(
                    labelText: 'Start Date',
                    suffixIcon:
                        Icon(Icons.calendar_today),
                  ),
                  onTap: () =>
                      _pickDate(
                    _startDateController,
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _endDateController,
                  readOnly: true,
                  decoration: const InputDecoration(
                    labelText: 'End Date',
                    suffixIcon:
                        Icon(Icons.calendar_today),
                  ),
                  onTap: () =>
                      _pickDate(
                    _endDateController,
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
                  validator: (value) {
                    final text =
                        value?.trim() ?? '';

                    if (text.isEmpty) {
                      return null;
                    }

                    final number =
                        double.tryParse(text);

                    if (number == null ||
                        number < 0) {
                      return 'Enter a valid duration';
                    }

                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _certificateNumberController,
                  decoration: const InputDecoration(
                    labelText: 'Certificate Number',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _certificateUrlController,
                  decoration: const InputDecoration(
                    labelText: 'Certificate URL',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _descriptionController,
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
            editing
                ? 'Save'
                : 'Create',
          ),
        ),
      ],
    );
  }
}