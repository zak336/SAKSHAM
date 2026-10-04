class BookChapter {
  final String id;
  final String tenantId;
  final String collegeId;
  final String facultyId;
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

  const BookChapter({
    required this.id,
    required this.tenantId,
    required this.collegeId,
    required this.facultyId,
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

  factory BookChapter.fromJson(
    Map<String, dynamic> json,
  ) {
    return BookChapter(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      collegeId: json['college_id'] as String,
      facultyId: json['faculty_id'] as String,
      chapterTitle: json['chapter_title'] as String,
      bookTitle: json['book_title'] as String,
      publisher: json['publisher'] as String?,
      publicationDate:
          json['publication_date'] as String?,
      isbn: json['isbn'] as String?,
      edition: json['edition'] as String?,
      chapterNumber:
          json['chapter_number'] as String?,
      pages: json['pages'] as String?,
      editors: json['editors'] as String?,
      doi: json['doi'] as String?,
      url: json['url'] as String?,
      description:
          json['description'] as String?,
    );
  }
}