class Patent {
  final String id;
  final String tenantId;
  final String collegeId;
  final String facultyId;
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

  const Patent({
    required this.id,
    required this.tenantId,
    required this.collegeId,
    required this.facultyId,
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

  factory Patent.fromJson(Map<String, dynamic> json) {
    return Patent(
      id: json['id'] as String,
      tenantId: json['tenant_id'] as String,
      collegeId: json['college_id'] as String,
      facultyId: json['faculty_id'] as String,
      title: json['title'] as String,
      patentNumber: json['patent_number'] as String?,
      applicationNumber: json['application_number'] as String?,
      patentType: json['patent_type'] as String,
      status: json['status'] as String,
      filingDate: json['filing_date'] as String?,
      publicationDate: json['publication_date'] as String?,
      grantDate: json['grant_date'] as String?,
      inventors: json['inventors'] as String?,
      assignee: json['assignee'] as String?,
      country: json['country'] as String?,
      office: json['office'] as String?,
      description: json['description'] as String?,
      referenceUrl: json['reference_url'] as String?,
    );
  }
}