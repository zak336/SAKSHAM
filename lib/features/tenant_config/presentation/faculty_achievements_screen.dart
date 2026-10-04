import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../models/achievement.dart';
import '../models/college.dart';
import '../models/tenant.dart';
import '../repository/tenant_config_repository.dart';

class FacultyAchievementsScreen extends StatefulWidget {
  final Tenant tenant;
  final College college;
  final String facultyId;
  final String facultyName;

  const FacultyAchievementsScreen({
    super.key,
    required this.tenant,
    required this.college,
    required this.facultyId,
    required this.facultyName,
  });

  @override
  State<FacultyAchievementsScreen> createState() =>
      _FacultyAchievementsScreenState();
}

class _FacultyAchievementsScreenState
    extends State<FacultyAchievementsScreen> {
  late final TenantConfigRepository _repository;
  late Future<List<Achievement>> _achievementsFuture;

  @override
  void initState() {
    super.initState();

    _repository = TenantConfigRepository(
      context.read<Dio>(),
    );

    _loadAchievements();
  }

  void _loadAchievements() {
    _achievementsFuture = _repository.getAchievements(
      tenantSlug: widget.tenant.slug,
      collegeId: widget.college.id,
      facultyId: widget.facultyId,
    );
  }

  Future<void> _addAchievement() async {
    final result = await showDialog<_AchievementFormData>(
      context: context,
      builder: (_) => const _AchievementFormDialog(),
    );

    if (result == null || !mounted) return;

    try {
      await _repository.createAchievement(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        facultyId: widget.facultyId,
        title: result.title,
        category: result.category,
        description: result.description,
        issuingOrganization: result.issuingOrganization,
        achievementDate: result.achievementDate,
        referenceUrl: result.referenceUrl,
      );

      if (!mounted) return;

      setState(_loadAchievements);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Achievement added successfully.'),
        ),
      );
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _editAchievement(
    Achievement achievement,
  ) async {
    final result = await showDialog<_AchievementFormData>(
      context: context,
      builder: (_) => _AchievementFormDialog(
        achievement: achievement,
      ),
    );

    if (result == null || !mounted) return;

    try {
      await _repository.updateAchievement(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        achievementId: achievement.id,
        title: result.title,
        category: result.category,
        description: result.description,
        issuingOrganization: result.issuingOrganization,
        achievementDate: result.achievementDate,
        referenceUrl: result.referenceUrl,
      );

      if (!mounted) return;

      setState(_loadAchievements);
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _deleteAchievement(
    Achievement achievement,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Delete Achievement'),
          content: Text(
            'Delete "${achievement.title}"?',
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
        );
      },
    );

    if (confirmed != true || !mounted) return;

    try {
      await _repository.deleteAchievement(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        achievementId: achievement.id,
      );

      if (!mounted) return;

      setState(_loadAchievements);
    } catch (error) {
      _showError(error);
    }
  }

  void _showError(Object error) {
    if (!mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(error.toString()),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Achievements'),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _addAchievement,
        icon: const Icon(Icons.add),
        label: const Text('Add Achievement'),
      ),
      body: FutureBuilder<List<Achievement>>(
        future: _achievementsFuture,
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

          final achievements =
              snapshot.data ??
              const <Achievement>[];

          if (achievements.isEmpty) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: Text(
                  'No achievements recorded yet.',
                ),
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(24),
            itemCount: achievements.length,
            itemBuilder: (context, index) {
              final achievement =
                  achievements[index];

              return Card(
                margin: const EdgeInsets.only(
                  bottom: 12,
                ),
                child: ListTile(
                  leading: const CircleAvatar(
                    child: Icon(
                      Icons.emoji_events_outlined,
                    ),
                  ),
                  title: Text(achievement.title),
                  subtitle: Text(
                    [
                      achievement.category,
                      if (achievement
                              .issuingOrganization
                              ?.isNotEmpty ==
                          true)
                        achievement
                            .issuingOrganization!,
                      if (achievement
                              .achievementDate
                              ?.isNotEmpty ==
                          true)
                        achievement.achievementDate!,
                    ].join(' • '),
                  ),
                  trailing: PopupMenuButton<String>(
                    onSelected: (value) {
                      if (value == 'edit') {
                        _editAchievement(
                          achievement,
                        );
                      }

                      if (value == 'delete') {
                        _deleteAchievement(
                          achievement,
                        );
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

class _AchievementFormData {
  final String title;
  final String category;
  final String? description;
  final String? issuingOrganization;
  final String? achievementDate;
  final String? referenceUrl;

  const _AchievementFormData({
    required this.title,
    required this.category,
    required this.description,
    required this.issuingOrganization,
    required this.achievementDate,
    required this.referenceUrl,
  });
}

class _AchievementFormDialog
    extends StatefulWidget {
  final Achievement? achievement;

  const _AchievementFormDialog({
    this.achievement,
  });

  @override
  State<_AchievementFormDialog> createState() =>
      _AchievementFormDialogState();
}

class _AchievementFormDialogState
    extends State<_AchievementFormDialog> {
  final _formKey =
      GlobalKey<FormState>();

  late final TextEditingController _titleController;
  late final TextEditingController _categoryController;
  late final TextEditingController _descriptionController;
  late final TextEditingController _organizationController;
  late final TextEditingController _dateController;
  late final TextEditingController _urlController;

  @override
  void initState() {
    super.initState();

    final achievement = widget.achievement;

    _titleController = TextEditingController(
      text: achievement?.title ?? '',
    );
    _categoryController = TextEditingController(
      text: achievement?.category ?? '',
    );
    _descriptionController =
        TextEditingController(
      text: achievement?.description ?? '',
    );
    _organizationController =
        TextEditingController(
      text: achievement?.issuingOrganization ?? '',
    );
    _dateController = TextEditingController(
      text: achievement?.achievementDate ?? '',
    );
    _urlController = TextEditingController(
      text: achievement?.referenceUrl ?? '',
    );
  }

  @override
  void dispose() {
    _titleController.dispose();
    _categoryController.dispose();
    _descriptionController.dispose();
    _organizationController.dispose();
    _dateController.dispose();
    _urlController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    Navigator.of(context).pop(
      _AchievementFormData(
        title: _titleController.text.trim(),
        category: _categoryController.text.trim(),
        description:
            _descriptionController.text.trim().isEmpty
                ? null
                : _descriptionController.text.trim(),
        issuingOrganization:
            _organizationController.text.trim().isEmpty
                ? null
                : _organizationController.text.trim(),
        achievementDate:
            _dateController.text.trim().isEmpty
                ? null
                : _dateController.text.trim(),
        referenceUrl:
            _urlController.text.trim().isEmpty
                ? null
                : _urlController.text.trim(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final editing = widget.achievement != null;

    return AlertDialog(
      title: Text(
        editing
            ? 'Edit Achievement'
            : 'Add Achievement',
      ),
      content: SizedBox(
        width: 520,
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
                  controller:
                      _categoryController,
                  decoration: const InputDecoration(
                    labelText: 'Category',
                  ),
                  validator: (value) {
                    if (value == null ||
                        value.trim().length < 2) {
                      return 'Enter a category';
                    }

                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _organizationController,
                  decoration: const InputDecoration(
                    labelText:
                        'Issuing Organization',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _dateController,
                  decoration: const InputDecoration(
                    labelText:
                        'Achievement Date (YYYY-MM-DD)',
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