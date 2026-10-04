import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../models/book_chapter.dart';
import '../models/college.dart';
import '../models/tenant.dart';
import '../repository/tenant_config_repository.dart';

class FacultyBookChaptersScreen
    extends StatefulWidget {
  final Tenant tenant;
  final College college;
  final String facultyId;
  final String facultyName;

  const FacultyBookChaptersScreen({
    super.key,
    required this.tenant,
    required this.college,
    required this.facultyId,
    required this.facultyName,
  });

  @override
  State<FacultyBookChaptersScreen>
      createState() =>
          _FacultyBookChaptersScreenState();
}

class _FacultyBookChaptersScreenState
    extends State<FacultyBookChaptersScreen> {
  late final TenantConfigRepository _repository;
  late Future<List<BookChapter>>
      _chaptersFuture;

  @override
  void initState() {
    super.initState();

    _repository =
        TenantConfigRepository(
      context.read<Dio>(),
    );

    _loadChapters();
  }

  void _loadChapters() {
    _chaptersFuture =
        _repository.getBookChapters(
      tenantSlug: widget.tenant.slug,
      collegeId: widget.college.id,
      facultyId: widget.facultyId,
    );
  }

  Future<void> _addChapter() async {
    final result =
        await showDialog<_BookChapterFormData>(
      context: context,
      builder: (_) =>
          const _BookChapterFormDialog(),
    );

    if (result == null || !mounted) return;

    try {
      await _repository.createBookChapter(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        facultyId: widget.facultyId,
        chapterTitle:
            result.chapterTitle,
        bookTitle: result.bookTitle,
        publisher: result.publisher,
        publicationDate:
            result.publicationDate,
        isbn: result.isbn,
        edition: result.edition,
        chapterNumber:
            result.chapterNumber,
        pages: result.pages,
        editors: result.editors,
        doi: result.doi,
        url: result.url,
        description:
            result.description,
      );

      if (!mounted) return;

      setState(_loadChapters);

      ScaffoldMessenger.of(context)
          .showSnackBar(
        const SnackBar(
          content: Text(
            'Book chapter added successfully.',
          ),
        ),
      );
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _editChapter(
    BookChapter chapter,
  ) async {
    final result =
        await showDialog<_BookChapterFormData>(
      context: context,
      builder: (_) =>
          _BookChapterFormDialog(
        chapter: chapter,
      ),
    );

    if (result == null || !mounted) return;

    try {
      await _repository.updateBookChapter(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        chapterId: chapter.id,
        chapterTitle:
            result.chapterTitle,
        bookTitle: result.bookTitle,
        publisher: result.publisher,
        publicationDate:
            result.publicationDate,
        isbn: result.isbn,
        edition: result.edition,
        chapterNumber:
            result.chapterNumber,
        pages: result.pages,
        editors: result.editors,
        doi: result.doi,
        url: result.url,
        description:
            result.description,
      );

      if (!mounted) return;

      setState(_loadChapters);
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _deleteChapter(
    BookChapter chapter,
  ) async {
    final confirmed =
        await showDialog<bool>(
      context: context,
      builder: (context) =>
          AlertDialog(
        title: const Text(
          'Delete Book Chapter',
        ),
        content: Text(
          'Delete "${chapter.chapterTitle}"?',
        ),
        actions: [
          TextButton(
            onPressed: () =>
                Navigator.of(context)
                    .pop(false),
            child:
                const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () =>
                Navigator.of(context)
                    .pop(true),
            child:
                const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed != true ||
        !mounted) {
      return;
    }

    try {
      await _repository.deleteBookChapter(
        tenantSlug: widget.tenant.slug,
        collegeId: widget.college.id,
        chapterId: chapter.id,
      );

      if (!mounted) return;

      setState(_loadChapters);
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

    ScaffoldMessenger.of(context)
        .showSnackBar(
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
        title:
            const Text('Book Chapters'),
      ),
      floatingActionButton:
          FloatingActionButton.extended(
        onPressed: _addChapter,
        icon: const Icon(Icons.add),
        label:
            const Text('Add Chapter'),
      ),
      body:
          FutureBuilder<List<BookChapter>>(
        future: _chaptersFuture,
        builder:
            (context, snapshot) {
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
                child: Text(
                  snapshot.error
                      .toString(),
                  textAlign:
                      TextAlign.center,
                ),
              ),
            );
          }

          final chapters =
              snapshot.data ??
                  const <BookChapter>[];

          if (chapters.isEmpty) {
            return const Center(
              child: Padding(
                padding:
                    EdgeInsets.all(32),
                child: Text(
                  'No book chapters recorded yet.',
                ),
              ),
            );
          }

          return ListView.builder(
            padding:
                const EdgeInsets.all(24),
            itemCount:
                chapters.length,
            itemBuilder:
                (context, index) {
              final chapter =
                  chapters[index];

              return Card(
                margin:
                    const EdgeInsets.only(
                  bottom: 12,
                ),
                child: ListTile(
                  leading:
                      const CircleAvatar(
                    child: Icon(
                      Icons
                          .menu_book_outlined,
                    ),
                  ),
                  title: Text(
                    chapter.chapterTitle,
                  ),
                  subtitle: Text(
                    [
                      chapter.bookTitle,
                      if (chapter.publisher
                              ?.isNotEmpty ==
                          true)
                        chapter.publisher!,
                      if (chapter.publicationDate
                              ?.isNotEmpty ==
                          true)
                        chapter.publicationDate!,
                    ].join(' • '),
                  ),
                  trailing:
                      PopupMenuButton<String>(
                    onSelected: (value) {
                      if (value ==
                          'edit') {
                        _editChapter(
                          chapter,
                        );
                      }

                      if (value ==
                          'delete') {
                        _deleteChapter(
                          chapter,
                        );
                      }
                    },
                    itemBuilder:
                        (context) =>
                            const [
                      PopupMenuItem(
                        value: 'edit',
                        child:
                            Text('Edit'),
                      ),
                      PopupMenuItem(
                        value: 'delete',
                        child:
                            Text('Delete'),
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

class _BookChapterFormData {
  final String chapterTitle;
  final String bookTitle;
  final String? publisher;
  final String? publicationDate;
  final String? isbn;
  final String? edition;
  final String? chapterNumber;
  final String? pages;
  final String? editors;
  final String? doi;
  final String? url;
  final String? description;

  const _BookChapterFormData({
    required this.chapterTitle,
    required this.bookTitle,
    required this.publisher,
    required this.publicationDate,
    required this.isbn,
    required this.edition,
    required this.chapterNumber,
    required this.pages,
    required this.editors,
    required this.doi,
    required this.url,
    required this.description,
  });
}

class _BookChapterFormDialog
    extends StatefulWidget {
  final BookChapter? chapter;

  const _BookChapterFormDialog({
    this.chapter,
  });

  @override
  State<_BookChapterFormDialog>
      createState() =>
          _BookChapterFormDialogState();
}

class _BookChapterFormDialogState
    extends State<_BookChapterFormDialog> {
  final _formKey =
      GlobalKey<FormState>();

  late final TextEditingController
      _chapterTitleController;
  late final TextEditingController
      _bookTitleController;
  late final TextEditingController
      _publisherController;
  late final TextEditingController
      _dateController;
  late final TextEditingController
      _isbnController;
  late final TextEditingController
      _editionController;
  late final TextEditingController
      _chapterNumberController;
  late final TextEditingController
      _pagesController;
  late final TextEditingController
      _editorsController;
  late final TextEditingController
      _doiController;
  late final TextEditingController
      _urlController;
  late final TextEditingController
      _descriptionController;

  @override
  void initState() {
    super.initState();

    final chapter =
        widget.chapter;

    _chapterTitleController =
        TextEditingController(
      text:
          chapter?.chapterTitle ?? '',
    );

    _bookTitleController =
        TextEditingController(
      text:
          chapter?.bookTitle ?? '',
    );

    _publisherController =
        TextEditingController(
      text:
          chapter?.publisher ?? '',
    );

    _dateController =
        TextEditingController(
      text:
          chapter?.publicationDate ??
              '',
    );

    _isbnController =
        TextEditingController(
      text: chapter?.isbn ?? '',
    );

    _editionController =
        TextEditingController(
      text:
          chapter?.edition ?? '',
    );

    _chapterNumberController =
        TextEditingController(
      text:
          chapter?.chapterNumber ??
              '',
    );

    _pagesController =
        TextEditingController(
      text:
          chapter?.pages ?? '',
    );

    _editorsController =
        TextEditingController(
      text:
          chapter?.editors ?? '',
    );

    _doiController =
        TextEditingController(
      text: chapter?.doi ?? '',
    );

    _urlController =
        TextEditingController(
      text:
          chapter?.url ?? '',
    );

    _descriptionController =
        TextEditingController(
      text:
          chapter?.description ??
              '',
    );
  }

  @override
  void dispose() {
    _chapterTitleController
        .dispose();
    _bookTitleController
        .dispose();
    _publisherController
        .dispose();
    _dateController.dispose();
    _isbnController.dispose();
    _editionController.dispose();
    _chapterNumberController
        .dispose();
    _pagesController.dispose();
    _editorsController.dispose();
    _doiController.dispose();
    _urlController.dispose();
    _descriptionController
        .dispose();

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
      initialDate:
          initialDate,
      firstDate:
          DateTime(1950),
      lastDate:
          DateTime.now(),
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

    _dateController.text =
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

    Navigator.of(context).pop(
      _BookChapterFormData(
        chapterTitle:
            _chapterTitleController
                .text
                .trim(),
        bookTitle:
            _bookTitleController
                .text
                .trim(),
        publisher:
            _optional(
          _publisherController.text,
        ),
        publicationDate:
            _optional(
          _dateController.text,
        ),
        isbn:
            _optional(
          _isbnController.text,
        ),
        edition:
            _optional(
          _editionController.text,
        ),
        chapterNumber:
            _optional(
          _chapterNumberController
              .text,
        ),
        pages:
            _optional(
          _pagesController.text,
        ),
        editors:
            _optional(
          _editorsController.text,
        ),
        doi:
            _optional(
          _doiController.text,
        ),
        url:
            _optional(
          _urlController.text,
        ),
        description:
            _optional(
          _descriptionController.text,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final editing =
        widget.chapter != null;

    return AlertDialog(
      title: Text(
        editing
            ? 'Edit Book Chapter'
            : 'Add Book Chapter',
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
                TextFormField(
                  controller:
                      _chapterTitleController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Chapter Title',
                  ),
                  validator:
                      (value) {
                    if (value ==
                            null ||
                        value
                                .trim()
                                .length <
                            2) {
                      return 'Enter a valid chapter title';
                    }
                    return null;
                  },
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _bookTitleController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Book Title',
                  ),
                  validator:
                      (value) {
                    if (value ==
                            null ||
                        value
                                .trim()
                                .length <
                            2) {
                      return 'Enter a valid book title';
                    }
                    return null;
                  },
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _publisherController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Publisher',
                  ),
                ),
                const SizedBox(
                  height: 12,
                ),
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
                  onTap:
                      _pickDate,
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _isbnController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'ISBN',
                  ),
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _editionController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Edition',
                  ),
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _chapterNumberController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Chapter Number',
                  ),
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _pagesController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Pages',
                  ),
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _editorsController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Editors',
                  ),
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _doiController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'DOI',
                  ),
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _urlController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'URL',
                  ),
                ),
                const SizedBox(
                  height: 12,
                ),
                TextFormField(
                  controller:
                      _descriptionController,
                  decoration:
                      const InputDecoration(
                    labelText:
                        'Description',
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