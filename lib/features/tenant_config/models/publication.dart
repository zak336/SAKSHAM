class Publication {
  final String id;
  final String tenantId;
  final String collegeId;
  final String facultyId;
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

  const Publication({
    required this.id,
    required this.tenantId,
    required this.collegeId,
    required this.facultyId,
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

  factory Publication.fromJson(
    Map<String, dynamic> json,
  ) {
    return Publication(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      collegeId: json['college_id'] as String,
      facultyId: json['faculty_id'] as String,
      title: json['title'] as String,
      publicationType:
          json['publication_type'] as String,
      journalOrConference:
          json['journal_or_conference'] as String?,
      publisher: json['publisher'] as String?,
      publicationDate:
          json['publication_date'] as String?,
      volume: json['volume'] as String?,
      issue: json['issue'] as String?,
      pages: json['pages'] as String?,
      doi: json['doi'] as String?,
      indexing: json['indexing'] as String?,
      url: json['url'] as String?,
      abstractText:
          json['abstract'] as String?,
    );
  }
}