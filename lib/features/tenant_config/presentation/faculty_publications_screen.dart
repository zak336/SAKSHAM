import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../models/college.dart';
import '../models/publication.dart';
import '../models/tenant.dart';
import '../repository/tenant_config_repository.dart';

class FacultyPublicationsScreen
    extends StatefulWidget {
  final Tenant tenant;
  final College college;
  final String facultyId;
  final String facultyName;

  const FacultyPublicationsScreen({
    super.key,
    required this.tenant,
    required this.college,
    required this.facultyId,
    required this.facultyName,
  });

  @override
  State<FacultyPublicationsScreen> createState() =>
      _FacultyPublicationsScreenState();
}

class _FacultyPublicationsScreenState
    extends State<FacultyPublicationsScreen> {
  late final TenantConfigRepository _repository;
  late Future<List<Publication>>
      _publicationsFuture;

  @override
  void initState() {
    super.initState();

    _repository = TenantConfigRepository(
      context.read<Dio>(),
    );

    _loadPublications();
  }

  void _loadPublications() {
    _publicationsFuture =
        _repository.getPublications(
      tenantSlug: widget.tenant.slug,
      collegeId: widget.college.id,
      facultyId: widget.facultyId,
    );
  }

  Future<void> _addPublication() async {
    final result =
        await showDialog<_PublicationFormData>(
      context: context,
      builder: (_) =>
          const _PublicationFormDialog(),
    );

    if (result == null || !mounted) return;

    try {
      await _repository.createPublication(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        facultyId: widget.facultyId,
        title: result.title,
        publicationType:
            result.publicationType,
        journalOrConference:
            result.journalOrConference,
        publisher: result.publisher,
        publicationDate:
            result.publicationDate,
        volume: result.volume,
        issue: result.issue,
        pages: result.pages,
        doi: result.doi,
        indexing: result.indexing,
        url: result.url,
        abstractText: result.abstractText,
      );

      if (!mounted) return;

      setState(_loadPublications);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Publication added successfully.',
          ),
        ),
      );
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _editPublication(
    Publication publication,
  ) async {
    final result =
        await showDialog<_PublicationFormData>(
      context: context,
      builder: (_) =>
          _PublicationFormDialog(
        publication: publication,
      ),
    );

    if (result == null || !mounted) return;

    try {
      await _repository.updatePublication(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        publicationId: publication.id,
        title: result.title,
        publicationType:
            result.publicationType,
        journalOrConference:
            result.journalOrConference,
        publisher: result.publisher,
        publicationDate:
            result.publicationDate,
        volume: result.volume,
        issue: result.issue,
        pages: result.pages,
        doi: result.doi,
        indexing: result.indexing,
        url: result.url,
        abstractText: result.abstractText,
      );

      if (!mounted) return;

      setState(_loadPublications);
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _deletePublication(
    Publication publication,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text(
          'Delete Publication',
        ),
        content: Text(
          'Delete "${publication.title}"?',
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
      await _repository.deletePublication(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        publicationId: publication.id,
      );

      if (!mounted) return;

      setState(_loadPublications);
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
        duration:
            const Duration(seconds: 6),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Publications'),
      ),
      floatingActionButton:
          FloatingActionButton.extended(
        onPressed: _addPublication,
        icon: const Icon(Icons.add),
        label: const Text('Add Publication'),
      ),
      body: FutureBuilder<List<Publication>>(
        future: _publicationsFuture,
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
                padding:
                    const EdgeInsets.all(24),
                child: Text(
                  snapshot.error.toString(),
                  textAlign:
                      TextAlign.center,
                ),
              ),
            );
          }

          final publications =
              snapshot.data ??
              const <Publication>[];

          if (publications.isEmpty) {
            return const Center(
              child: Padding(
                padding:
                    EdgeInsets.all(32),
                child: Text(
                  'No publications recorded yet.',
                ),
              ),
            );
          }

          return ListView.builder(
            padding:
                const EdgeInsets.all(24),
            itemCount: publications.length,
            itemBuilder:
                (context, index) {
              final publication =
                  publications[index];

              return Card(
                margin:
                    const EdgeInsets.only(
                  bottom: 12,
                ),
                child: ListTile(
                  leading:
                      const CircleAvatar(
                    child: Icon(
                      Icons.article_outlined,
                    ),
                  ),
                  title:
                      Text(publication.title),
                  subtitle: Text(
                    [
                      publication
                          .publicationType,
                      if (publication
                              .journalOrConference
                              ?.isNotEmpty ==
                          true)
                        publication
                            .journalOrConference!,
                      if (publication
                              .publicationDate
                              ?.isNotEmpty ==
                          true)
                        publication
                            .publicationDate!,
                    ].join(' • '),
                  ),
                  trailing:
                      PopupMenuButton<String>(
                    onSelected: (value) {
                      if (value == 'edit') {
                        _editPublication(
                          publication,
                        );
                      }

                      if (value == 'delete') {
                        _deletePublication(
                          publication,
                        );
                      }
                    },
                    itemBuilder:
                        (context) => const [
                      PopupMenuItem(
                        value: 'edit',
                        child: Text('Edit'),
                      ),
                      PopupMenuItem(
                        value: 'delete',
                        child: Text(
                          'Delete',
                        ),
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

class _PublicationFormData {
  final String title;
  final String publicationType;
  final String? journalOrConference;
  final String? publisher;
  final String? publicationDate;
  final String? volume;
  final String? issue;
  final String? pages;
  final String? doi;
  final String? indexing;
  final String? url;
  final String? abstractText;

  const _PublicationFormData({
    required this.title,
    required this.publicationType,
    required this.journalOrConference,
    required this.publisher,
    required this.publicationDate,
    required this.volume,
    required this.issue,
    required this.pages,
    required this.doi,
    required this.indexing,
    required this.url,
    required this.abstractText,
  });
}

class _PublicationFormDialog
    extends StatefulWidget {
  final Publication? publication;

  const _PublicationFormDialog({
    this.publication,
  });

  @override
  State<_PublicationFormDialog> createState() =>
      _PublicationFormDialogState();
}

class _PublicationFormDialogState
    extends State<_PublicationFormDialog> {
  final _formKey =
      GlobalKey<FormState>();

  late final TextEditingController
      _titleController;
  late final TextEditingController
      _typeController;
  late final TextEditingController
      _journalController;
  late final TextEditingController
      _publisherController;
  late final TextEditingController
      _dateController;
  late final TextEditingController
      _volumeController;
  late final TextEditingController
      _issueController;
  late final TextEditingController
      _pagesController;
  late final TextEditingController
      _doiController;
  late final TextEditingController
      _indexingController;
  late final TextEditingController
      _urlController;
  late final TextEditingController
      _abstractController;

  @override
  void initState() {
    super.initState();

    final publication =
        widget.publication;

    _titleController =
        TextEditingController(
      text: publication?.title ?? '',
    );
    _typeController =
        TextEditingController(
      text:
          publication?.publicationType ??
              '',
    );
    _journalController =
        TextEditingController(
      text:
          publication
                  ?.journalOrConference ??
              '',
    );
    _publisherController =
        TextEditingController(
      text: publication?.publisher ?? '',
    );
    _dateController =
        TextEditingController(
      text:
          publication?.publicationDate ??
              '',
    );
    _volumeController =
        TextEditingController(
      text: publication?.volume ?? '',
    );
    _issueController =
        TextEditingController(
      text: publication?.issue ?? '',
    );
    _pagesController =
        TextEditingController(
      text: publication?.pages ?? '',
    );
    _doiController =
        TextEditingController(
      text: publication?.doi ?? '',
    );
    _indexingController =
        TextEditingController(
      text: publication?.indexing ?? '',
    );
    _urlController =
        TextEditingController(
      text: publication?.url ?? '',
    );
    _abstractController =
        TextEditingController(
      text: publication?.abstractText ?? '',
    );
  }

  @override
  void dispose() {
    _titleController.dispose();
    _typeController.dispose();
    _journalController.dispose();
    _publisherController.dispose();
    _dateController.dispose();
    _volumeController.dispose();
    _issueController.dispose();
    _pagesController.dispose();
    _doiController.dispose();
    _indexingController.dispose();
    _urlController.dispose();
    _abstractController.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    final initialDate =
        DateTime.tryParse(
              _dateController.text,
            ) ??
            DateTime.now();

    final picked =
        await showDatePicker(
      context: context,
      initialDate: initialDate,
      firstDate: DateTime(1950),
      lastDate: DateTime.now(),
    );

    if (picked == null) return;

    final month = picked.month
        .toString()
        .padLeft(2, '0');
    final day = picked.day
        .toString()
        .padLeft(2, '0');

    _dateController.text =
        '${picked.year}-$month-$day';
  }

  void _submit() {
    if (!_formKey.currentState!
        .validate()) {
      return;
    }

    Navigator.of(context).pop(
      _PublicationFormData(
        title:
            _titleController.text.trim(),
        publicationType:
            _typeController.text.trim(),
        journalOrConference:
            _journalController.text
                    .trim()
                    .isEmpty
                ? null
                : _journalController.text
                    .trim(),
        publisher:
            _publisherController.text
                    .trim()
                    .isEmpty
                ? null
                : _publisherController.text
                    .trim(),
        publicationDate:
            _dateController.text
                    .trim()
                    .isEmpty
                ? null
                : _dateController.text
                    .trim(),
        volume:
            _volumeController.text
                    .trim()
                    .isEmpty
                ? null
                : _volumeController.text
                    .trim(),
        issue:
            _issueController.text
                    .trim()
                    .isEmpty
                ? null
                : _issueController.text
                    .trim(),
        pages:
            _pagesController.text
                    .trim()
                    .isEmpty
                ? null
                : _pagesController.text
                    .trim(),
        doi:
            _doiController.text
                    .trim()
                    .isEmpty
                ? null
                : _doiController.text
                    .trim(),
        indexing:
            _indexingController.text
                    .trim()
                    .isEmpty
                ? null
                : _indexingController.text
                    .trim(),
        url:
            _urlController.text
                    .trim()
                    .isEmpty
                ? null
                : _urlController.text
                    .trim(),
        abstractText:
            _abstractController.text
                    .trim()
                    .isEmpty
                ? null
                : _abstractController.text
                    .trim(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final editing =
        widget.publication != null;

    return AlertDialog(
      title: Text(
        editing
            ? 'Edit Publication'
            : 'Add Publication',
      ),
      content: SizedBox(
        width: 560,
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize:
                  MainAxisSize.min,
              children: [
                TextFormField(
                  controller:
                      _titleController,
                  decoration:
                      const InputDecoration(
                    labelText: 'Title',
                  ),
                  validator: (value) {
                    if (value == null ||
                        value.trim().length <
                            2) {
                      return 'Enter a valid title';
                    }

                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _typeController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Publication Type',
                    hintText:
                        'Journal / Conference / Book',
                  ),
                  validator: (value) {
                    if (value == null ||
                        value.trim().length <
                            2) {
                      return 'Enter publication type';
                    }

                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _journalController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Journal / Conference',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _publisherController,
                  decoration:
                      const InputDecoration(
                    labelText: 'Publisher',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _dateController,
                  readOnly: true,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Publication Date',
                    suffixIcon:
                        Icon(
                      Icons
                          .calendar_today,
                    ),
                  ),
                  onTap: _pickDate,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _volumeController,
                  decoration:
                      const InputDecoration(
                    labelText: 'Volume',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _issueController,
                  decoration:
                      const InputDecoration(
                    labelText: 'Issue',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _pagesController,
                  decoration:
                      const InputDecoration(
                    labelText: 'Pages',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _doiController,
                  decoration:
                      const InputDecoration(
                    labelText: 'DOI',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _indexingController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Indexing',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _urlController,
                  decoration:
                      const InputDecoration(
                    labelText: 'URL',
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller:
                      _abstractController,
                  decoration:
                      const InputDecoration(
                    labelText: 'Abstract',
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