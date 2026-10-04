import 'package:dio/dio.dart';

import '../models/college.dart';
import '../models/tenant.dart';
import '../models/tenant_config.dart';
import '../models/tenant_module.dart';
import '../models/department.dart';
import '../models/user.dart';
import '../models/faculty.dart';
import '../models/achievement.dart';
import '../models/publication.dart';
import '../models/patent.dart';
import '../models/book_chapter.dart';
import '../../academics/data/models/course.dart';
import '../models/faculty_course_assignment.dart';
import '../models/mooc_completion.dart';
import '../models/faculty_development_program.dart';

class TenantConfigRepository {
  final Dio dio;

  TenantConfigRepository(this.dio);

  /// Runtime configuration for the currently selected tenant.
  /// Used by the normal tenant application.
  Future<TenantConfig> getConfig() async {
    final response = await dio.get('/config');

    return TenantConfig.fromJson(response.data as Map<String, dynamic>);
  }

  /// Super admin: get configuration for a specific tenant.
  Future<TenantConfig> getTenantConfig({required String tenantId}) async {
    final response = await dio.get('/tenants/$tenantId/config');

    return TenantConfig.fromJson(response.data as Map<String, dynamic>);
  }

  /// Super admin: get all tenants.
  Future<List<Tenant>> getTenants() async {
    final response = await dio.get('/tenants');

    return (response.data as List<dynamic>)
        .map((item) => Tenant.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  /// Super admin: list colleges belonging to an organization.
  Future<List<College>> getColleges({required String tenantId}) async {
    final response = await dio.get('/tenants/$tenantId/colleges');

    return (response.data as List<dynamic>)
        .map((item) => College.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  /// Super admin: create a college inside an organization.
  Future<College> createCollege({
    required String tenantId,
    required String name,
    required String code,
    required String slug,
  }) async {
    final response = await dio.post(
      '/tenants/$tenantId/colleges',
      data: {'name': name, 'code': code, 'slug': slug},
    );

    return College.fromJson(response.data as Map<String, dynamic>);
  }

  /// Super admin: update a college.
  Future<College> updateCollege({
    required String tenantId,
    required String collegeId,
    String? name,
    String? code,
    bool? isActive,
  }) async {
    final data = <String, dynamic>{};

    if (name != null) {
      data['name'] = name;
    }

    if (code != null) {
      data['code'] = code;
    }

    if (isActive != null) {
      data['is_active'] = isActive;
    }

    final response = await dio.patch(
      '/tenants/$tenantId/colleges/$collegeId',
      data: data,
    );

    return College.fromJson(response.data as Map<String, dynamic>);
  }

  /// admin: gets college.
  Future<College> getMyCollege() async {
    final response = await dio.get('/colleges/me');

    return College.fromJson(response.data as Map<String, dynamic>);
  }

  /// Super admin: create a tenant.
  Future<Tenant> createTenant({
    required String name,
    required String slug,
  }) async {
    final response = await dio.post(
      '/tenants',
      data: {'name': name, 'slug': slug},
    );

    return Tenant.fromJson(response.data as Map<String, dynamic>);
  }

  Future<College> getCollege({
    required String tenantId,
    required String collegeId,
  }) async {
    final response = await dio.get('/tenants/$tenantId/colleges/$collegeId');

    return College.fromJson(response.data as Map<String, dynamic>);
  }

  /// Super admin: update tenant name/status.
  Future<Tenant> updateTenant({
    required String tenantId,
    String? name,
    bool? isActive,
  }) async {
    final data = <String, dynamic>{};

    if (name != null) {
      data['name'] = name;
    }

    if (isActive != null) {
      data['is_active'] = isActive;
    }

    final response = await dio.patch('/tenants/$tenantId', data: data);

    return Tenant.fromJson(response.data as Map<String, dynamic>);
  }

  /// Super admin: update module subscription.
  Future<TenantModule> updateModule({
    required String tenantId,
    required String moduleKey,
    required bool enabled,
    Map<String, dynamic> config = const {},
  }) async {
    final response = await dio.patch(
      '/tenants/$tenantId/modules/$moduleKey',
      data: {'enabled': enabled, 'config': config},
    );

    return TenantModule.fromJson(response.data as Map<String, dynamic>);
  }

  /// Super admin: update branding for a specific tenant.
  Future<TenantConfig> updateTenantBranding({
    required String tenantId,
    String? displayName,
    String? logoUrl,
    String? faviconUrl,
    String? primaryColor,
    String? secondaryColor,
    String? accentColor,
  }) async {
    final response = await dio.patch(
      '/tenants/$tenantId/branding',
      data: {
        'display_name': ?displayName,
        'logo_url': ?logoUrl,
        'favicon_url': ?faviconUrl,
        'primary_color': ?primaryColor,
        'secondary_color': ?secondaryColor,
        'accent_color': ?accentColor,
      },
    );

    return TenantConfig.fromJson(response.data as Map<String, dynamic>);
  }

  /// List departments for a selected organization + college.
  Future<List<Department>> getDepartments({
    required String tenantSlug,
    required String collegeId,
  }) async {
    final response = await dio.get(
      '/departments',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );

    return (response.data as List<dynamic>)
        .map((item) => Department.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  /// Create a department for a selected organization + college.
  Future<Department> createDepartment({
    required String tenantSlug,
    required String collegeId,
    required String name,
    required String code,
  }) async {
    final response = await dio.post(
      '/departments',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: {'name': name, 'code': code},
    );

    return Department.fromJson(response.data as Map<String, dynamic>);
  }

  /// Update a department.
  Future<Department> updateDepartment({
    required String tenantSlug,
    required String collegeId,
    required String departmentId,
    String? name,
    bool? isActive,
  }) async {
    final data = <String, dynamic>{};

    if (name != null) {
      data['name'] = name;
    }

    if (isActive != null) {
      data['is_active'] = isActive;
    }

    final response = await dio.patch(
      '/departments/$departmentId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: data,
    );

    return Department.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<User>> getUsers({
    required String tenantSlug,
    required String collegeId,
  }) async {
    final response = await dio.get(
      '/users',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );

    return (response.data as List<dynamic>)
        .map((item) => User.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<User> createUser({
    required String tenantSlug,
    required String collegeId,
    required String name,
    required String email,
    required String password,
    String? phone,
    required String role,
  }) async {
    final response = await dio.post(
      '/users',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: {
        'name': name,
        'email': email,
        'password': password,
        'phone': phone,
        'role': role,
      },
    );

    return User.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<Faculty>> getFaculty({
    required String tenantSlug,
    required String collegeId,
    String? departmentId,
  }) async {
    final response = await dio.get(
      '/faculty',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      queryParameters: {'department_id': ?departmentId},
    );

    return (response.data as List<dynamic>)
        .map((item) => Faculty.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Faculty> getFacultyById({
    required String tenantSlug,
    required String collegeId,
    required String facultyId,
  }) async {
    final response = await dio.get(
      '/faculty/$facultyId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );

    return Faculty.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Faculty> createFaculty({
    required String tenantSlug,
    required String collegeId,
    required String userId,
    required String departmentId,
    String? designation,
    String? qualification,
    String? joiningDate,
    String? researchInterests,
    String? bio,
  }) async {
    final response = await dio.post(
      '/faculty',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: {
        'user_id': userId,
        'department_id': departmentId,
        'designation': designation,
        'qualification': qualification,
        'joining_date': joiningDate,
        'research_interests': researchInterests,
        'bio': bio,
      },
    );

    return Faculty.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<Achievement>> getAchievements({
    required String tenantSlug,
    required String collegeId,
    required String facultyId,
  }) async {
    final response = await dio.get(
      '/faculty/$facultyId/achievements',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );

    return (response.data as List<dynamic>)
        .map((item) => Achievement.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Achievement> createAchievement({
    required String tenantSlug,
    required String collegeId,
    required String facultyId,
    required String title,
    required String category,
    String? description,
    String? issuingOrganization,
    String? achievementDate,
    String? referenceUrl,
  }) async {
    final response = await dio.post(
      '/faculty/$facultyId/achievements',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: {
        'title': title,
        'category': category,
        'description': description,
        'issuing_organization': issuingOrganization,
        'achievement_date': achievementDate,
        'reference_url': referenceUrl,
      },
    );

    return Achievement.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Achievement> updateAchievement({
    required String tenantSlug,
    required String collegeId,
    required String achievementId,
    String? title,
    String? category,
    String? description,
    String? issuingOrganization,
    String? achievementDate,
    String? referenceUrl,
  }) async {
    final data = <String, dynamic>{};

    if (title != null) {
      data['title'] = title;
    }

    if (category != null) {
      data['category'] = category;
    }

    if (description != null) {
      data['description'] = description;
    }

    if (issuingOrganization != null) {
      data['issuing_organization'] = issuingOrganization;
    }

    if (achievementDate != null) {
      data['achievement_date'] = achievementDate;
    }

    if (referenceUrl != null) {
      data['reference_url'] = referenceUrl;
    }

    final response = await dio.patch(
      '/faculty/achievements/$achievementId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: data,
    );

    return Achievement.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> deleteAchievement({
    required String tenantSlug,
    required String collegeId,
    required String achievementId,
  }) async {
    await dio.delete(
      '/faculty/achievements/$achievementId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );
  }

  Future<List<Publication>> getPublications({
    required String tenantSlug,
    required String collegeId,
    required String facultyId,
  }) async {
    final response = await dio.get(
      '/faculty/$facultyId/publications',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );

    return (response.data as List<dynamic>)
        .map((item) => Publication.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Publication> createPublication({
    required String tenantSlug,
    required String collegeId,
    required String facultyId,
    required String title,
    required String publicationType,
    String? journalOrConference,
    String? publisher,
    String? publicationDate,
    String? volume,
    String? issue,
    String? pages,
    String? doi,
    String? indexing,
    String? url,
    String? abstractText,
  }) async {
    final response = await dio.post(
      '/faculty/$facultyId/publications',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: {
        'title': title,
        'publication_type': publicationType,
        'journal_or_conference': journalOrConference,
        'publisher': publisher,
        'publication_date': publicationDate,
        'volume': volume,
        'issue': issue,
        'pages': pages,
        'doi': doi,
        'indexing': indexing,
        'url': url,
        'abstract': abstractText,
      },
    );

    return Publication.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Publication> updatePublication({
    required String tenantSlug,
    required String collegeId,
    required String publicationId,
    String? title,
    String? publicationType,
    String? journalOrConference,
    String? publisher,
    String? publicationDate,
    String? volume,
    String? issue,
    String? pages,
    String? doi,
    String? indexing,
    String? url,
    String? abstractText,
  }) async {
    final data = <String, dynamic>{};

    if (title != null) {
      data['title'] = title;
    }

    if (publicationType != null) {
      data['publication_type'] = publicationType;
    }

    if (journalOrConference != null) {
      data['journal_or_conference'] = journalOrConference;
    }

    if (publisher != null) {
      data['publisher'] = publisher;
    }

    if (publicationDate != null) {
      data['publication_date'] = publicationDate;
    }

    if (volume != null) {
      data['volume'] = volume;
    }

    if (issue != null) {
      data['issue'] = issue;
    }

    if (pages != null) {
      data['pages'] = pages;
    }

    if (doi != null) {
      data['doi'] = doi;
    }

    if (indexing != null) {
      data['indexing'] = indexing;
    }

    if (url != null) {
      data['url'] = url;
    }

    if (abstractText != null) {
      data['abstract'] = abstractText;
    }

    final response = await dio.patch(
      '/faculty/publications/$publicationId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: data,
    );

    return Publication.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> deletePublication({
    required String tenantSlug,
    required String collegeId,
    required String publicationId,
  }) async {
    await dio.delete(
      '/faculty/publications/$publicationId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );
  }

  Future<List<Patent>> getPatents({
    required String tenantSlug,
    required String collegeId,
    required String facultyId,
  }) async {
    final response = await dio.get(
      '/faculty/$facultyId/patents',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );

    return (response.data as List<dynamic>)
        .map((item) => Patent.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Patent> createPatent({
    required String tenantSlug,
    required String collegeId,
    required String facultyId,
    required String title,
    String? patentNumber,
    String? applicationNumber,
    required String patentType,
    required String status,
    String? filingDate,
    String? publicationDate,
    String? grantDate,
    String? inventors,
    String? assignee,
    String? country,
    String? office,
    String? description,
    String? referenceUrl,
  }) async {
    final response = await dio.post(
      '/faculty/$facultyId/patents',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: {
        'title': title,
        'patent_number': patentNumber,
        'application_number': applicationNumber,
        'patent_type': patentType,
        'status': status,
        'filing_date': filingDate,
        'publication_date': publicationDate,
        'grant_date': grantDate,
        'inventors': inventors,
        'assignee': assignee,
        'country': country,
        'office': office,
        'description': description,
        'reference_url': referenceUrl,
      },
    );

    return Patent.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Patent> updatePatent({
    required String tenantSlug,
    required String collegeId,
    required String patentId,
    String? title,
    String? patentNumber,
    String? applicationNumber,
    String? patentType,
    String? status,
    String? filingDate,
    String? publicationDate,
    String? grantDate,
    String? inventors,
    String? assignee,
    String? country,
    String? office,
    String? description,
    String? referenceUrl,
  }) async {
    final data = <String, dynamic>{};

    if (title != null) data['title'] = title;
    if (patentNumber != null) {
      data['patent_number'] = patentNumber;
    }
    if (applicationNumber != null) {
      data['application_number'] = applicationNumber;
    }
    if (patentType != null) {
      data['patent_type'] = patentType;
    }
    if (status != null) data['status'] = status;
    if (filingDate != null) {
      data['filing_date'] = filingDate;
    }
    if (publicationDate != null) {
      data['publication_date'] = publicationDate;
    }
    if (grantDate != null) {
      data['grant_date'] = grantDate;
    }
    if (inventors != null) {
      data['inventors'] = inventors;
    }
    if (assignee != null) {
      data['assignee'] = assignee;
    }
    if (country != null) {
      data['country'] = country;
    }
    if (office != null) data['office'] = office;
    if (description != null) {
      data['description'] = description;
    }
    if (referenceUrl != null) {
      data['reference_url'] = referenceUrl;
    }

    final response = await dio.patch(
      '/faculty/patents/$patentId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: data,
    );

    return Patent.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> deletePatent({
    required String tenantSlug,
    required String collegeId,
    required String patentId,
  }) async {
    await dio.delete(
      '/faculty/patents/$patentId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );
  }

  Future<List<BookChapter>> getBookChapters({
    required String tenantSlug,
    required String collegeId,
    required String facultyId,
  }) async {
    final response = await dio.get(
      '/faculty/$facultyId/book-chapters',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );

    return (response.data as List<dynamic>)
        .map((item) => BookChapter.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<BookChapter> createBookChapter({
    required String tenantSlug,
    required String collegeId,
    required String facultyId,
    required String chapterTitle,
    required String bookTitle,
    String? publisher,
    String? publicationDate,
    String? isbn,
    String? edition,
    String? chapterNumber,
    String? pages,
    String? editors,
    String? doi,
    String? url,
    String? description,
  }) async {
    final response = await dio.post(
      '/faculty/$facultyId/book-chapters',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: {
        'chapter_title': chapterTitle,
        'book_title': bookTitle,
        'publisher': publisher,
        'publication_date': publicationDate,
        'isbn': isbn,
        'edition': edition,
        'chapter_number': chapterNumber,
        'pages': pages,
        'editors': editors,
        'doi': doi,
        'url': url,
        'description': description,
      },
    );

    return BookChapter.fromJson(response.data as Map<String, dynamic>);
  }

  Future<BookChapter> updateBookChapter({
    required String tenantSlug,
    required String collegeId,
    required String chapterId,
    String? chapterTitle,
    String? bookTitle,
    String? publisher,
    String? publicationDate,
    String? isbn,
    String? edition,
    String? chapterNumber,
    String? pages,
    String? editors,
    String? doi,
    String? url,
    String? description,
  }) async {
    final data = <String, dynamic>{};

    if (chapterTitle != null) {
      data['chapter_title'] = chapterTitle;
    }

    if (bookTitle != null) {
      data['book_title'] = bookTitle;
    }

    if (publisher != null) {
      data['publisher'] = publisher;
    }

    if (publicationDate != null) {
      data['publication_date'] = publicationDate;
    }

    if (isbn != null) {
      data['isbn'] = isbn;
    }

    if (edition != null) {
      data['edition'] = edition;
    }

    if (chapterNumber != null) {
      data['chapter_number'] = chapterNumber;
    }

    if (pages != null) {
      data['pages'] = pages;
    }

    if (editors != null) {
      data['editors'] = editors;
    }

    if (doi != null) {
      data['doi'] = doi;
    }

    if (url != null) {
      data['url'] = url;
    }

    if (description != null) {
      data['description'] = description;
    }

    final response = await dio.patch(
      '/faculty/book-chapters/$chapterId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: data,
    );

    return BookChapter.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> deleteBookChapter({
    required String tenantSlug,
    required String collegeId,
    required String chapterId,
  }) async {
    await dio.delete(
      '/faculty/book-chapters/$chapterId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );
  }

  Future<List<Course>> getCollegeCourses({
    required String tenantSlug,
    required String collegeId,
  }) async {
    final response = await dio.get(
      '/courses',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );

    return (response.data as List<dynamic>)
        .map((item) => Course.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<List<FacultyCourseAssignment>> getCourseAssignments({
    required String tenantSlug,
    required String collegeId,
    required String facultyId,
  }) async {
    final response = await dio.get(
      '/faculty/$facultyId/course-assignments',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );

    return (response.data as List<dynamic>)
        .map(
          (item) =>
              FacultyCourseAssignment.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<FacultyCourseAssignment> createCourseAssignment({
    required String tenantSlug,
    required String collegeId,
    required String facultyId,
    required String courseId,
    required String academicYear,
    required int semester,
    String? section,
    String teachingRole = 'primary',
    String? assignedFrom,
    String? assignedUntil,
  }) async {
    final response = await dio.post(
      '/faculty/$facultyId/course-assignments',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: {
        'course_id': courseId,
        'academic_year': academicYear,
        'semester': semester,
        'section': section,
        'teaching_role': teachingRole,
        'assigned_from': assignedFrom,
        'assigned_until': assignedUntil,
      },
    );

    return FacultyCourseAssignment.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  Future<FacultyCourseAssignment> updateCourseAssignment({
    required String tenantSlug,
    required String collegeId,
    required String assignmentId,
    String? courseId,
    String? academicYear,
    int? semester,
    String? section,
    String? teachingRole,
    String? assignedFrom,
    String? assignedUntil,
  }) async {
    final data = <String, dynamic>{};

    if (courseId != null) {
      data['course_id'] = courseId;
    }

    if (academicYear != null) {
      data['academic_year'] = academicYear;
    }

    if (semester != null) {
      data['semester'] = semester;
    }

    if (section != null) {
      data['section'] = section;
    }

    if (teachingRole != null) {
      data['teaching_role'] = teachingRole;
    }

    if (assignedFrom != null) {
      data['assigned_from'] = assignedFrom;
    }

    if (assignedUntil != null) {
      data['assigned_until'] = assignedUntil;
    }

    final response = await dio.patch(
      '/faculty/course-assignments/$assignmentId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: data,
    );

    return FacultyCourseAssignment.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  Future<void> deleteCourseAssignment({
    required String tenantSlug,
    required String collegeId,
    required String assignmentId,
  }) async {
    await dio.delete(
      '/faculty/course-assignments/$assignmentId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );
  }

  Future<List<MoocCompletion>> getMoocsForUser({
    required String tenantSlug,
    required String collegeId,
    required String userId,
  }) async {
    final response = await dio.get(
      '/moocs/users/$userId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );

    return (response.data as List<dynamic>)
        .map((item) => MoocCompletion.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<MoocCompletion> createMooc({
    required String tenantSlug,
    required String collegeId,
    required String userId,
    required String courseTitle,
    String? provider,
    String? platform,
    String? courseIdentifier,
    double? durationHours,
    String? enrolledOn,
    String? completedOn,
    String? certificateId,
    String? certificateUrl,
    double? score,
    String status = 'completed',
    String? description,
  }) async {
    final response = await dio.post(
      '/moocs',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: {
        'user_id': userId,
        'course_title': courseTitle,
        'provider': provider,
        'platform': platform,
        'course_identifier': courseIdentifier,
        'duration_hours': durationHours,
        'enrolled_on': enrolledOn,
        'completed_on': completedOn,
        'certificate_id': certificateId,
        'certificate_url': certificateUrl,
        'score': score,
        'status': status,
        'description': description,
      },
    );

    return MoocCompletion.fromJson(response.data as Map<String, dynamic>);
  }

  Future<MoocCompletion> updateMooc({
    required String tenantSlug,
    required String collegeId,
    required String completionId,
    String? courseTitle,
    String? provider,
    String? platform,
    String? courseIdentifier,
    double? durationHours,
    String? enrolledOn,
    String? completedOn,
    String? certificateId,
    String? certificateUrl,
    double? score,
    String? status,
    String? description,
  }) async {
    final data = <String, dynamic>{};

    if (courseTitle != null) {
      data['course_title'] = courseTitle;
    }
    if (provider != null) {
      data['provider'] = provider;
    }
    if (platform != null) {
      data['platform'] = platform;
    }
    if (courseIdentifier != null) {
      data['course_identifier'] = courseIdentifier;
    }
    if (durationHours != null) {
      data['duration_hours'] = durationHours;
    }
    if (enrolledOn != null) {
      data['enrolled_on'] = enrolledOn;
    }
    if (completedOn != null) {
      data['completed_on'] = completedOn;
    }
    if (certificateId != null) {
      data['certificate_id'] = certificateId;
    }
    if (certificateUrl != null) {
      data['certificate_url'] = certificateUrl;
    }
    if (score != null) {
      data['score'] = score;
    }
    if (status != null) {
      data['status'] = status;
    }
    if (description != null) {
      data['description'] = description;
    }

    final response = await dio.patch(
      '/moocs/$completionId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: data,
    );

    return MoocCompletion.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> deleteMooc({
    required String tenantSlug,
    required String collegeId,
    required String completionId,
  }) async {
    await dio.delete(
      '/moocs/$completionId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );
  }

  Future<List<FacultyDevelopmentProgram>> getFdps({
    required String tenantSlug,
    required String collegeId,
    required String facultyId,
  }) async {
    final response = await dio.get(
      '/faculty/$facultyId/fdps',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );

    return (response.data as List<dynamic>)
        .map(
          (item) =>
              FacultyDevelopmentProgram.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  Future<FacultyDevelopmentProgram> createFdp({
    required String tenantSlug,
    required String collegeId,
    required String facultyId,
    required String title,
    String? organizer,
    String? programType,
    String? mode,
    String? venue,
    String? startDate,
    String? endDate,
    double? durationHours,
    String? certificateNumber,
    String? certificateUrl,
    String? description,
  }) async {
    final response = await dio.post(
      '/faculty/$facultyId/fdps',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: {
        'title': title,
        'organizer': organizer,
        'program_type': programType,
        'mode': mode,
        'venue': venue,
        'start_date': startDate,
        'end_date': endDate,
        'duration_hours': durationHours,
        'certificate_number': certificateNumber,
        'certificate_url': certificateUrl,
        'description': description,
      },
    );

    return FacultyDevelopmentProgram.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  Future<FacultyDevelopmentProgram> updateFdp({
    required String tenantSlug,
    required String collegeId,
    required String fdpId,
    String? title,
    String? organizer,
    String? programType,
    String? mode,
    String? venue,
    String? startDate,
    String? endDate,
    double? durationHours,
    String? certificateNumber,
    String? certificateUrl,
    String? description,
  }) async {
    final data = <String, dynamic>{};

    if (title != null) {
      data['title'] = title;
    }
    if (organizer != null) {
      data['organizer'] = organizer;
    }
    if (programType != null) {
      data['program_type'] = programType;
    }
    if (mode != null) {
      data['mode'] = mode;
    }
    if (venue != null) {
      data['venue'] = venue;
    }
    if (startDate != null) {
      data['start_date'] = startDate;
    }
    if (endDate != null) {
      data['end_date'] = endDate;
    }
    if (durationHours != null) {
      data['duration_hours'] = durationHours;
    }
    if (certificateNumber != null) {
      data['certificate_number'] = certificateNumber;
    }
    if (certificateUrl != null) {
      data['certificate_url'] = certificateUrl;
    }
    if (description != null) {
      data['description'] = description;
    }

    final response = await dio.patch(
      '/faculty/fdps/$fdpId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: data,
    );

    return FacultyDevelopmentProgram.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  Future<void> deleteFdp({
    required String tenantSlug,
    required String collegeId,
    required String fdpId,
  }) async {
    await dio.delete(
      '/faculty/fdps/$fdpId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
    );
  }

  Future<Faculty> updateFaculty({
    required String tenantSlug,
    required String collegeId,
    required String facultyId,
    String? departmentId,
    String? designation,
    String? qualification,
    String? joiningDate,
    String? researchInterests,
    String? bio,
  }) async {
    final data = <String, dynamic>{};

    if (departmentId != null) {
      data['department_id'] = departmentId;
    }

    if (designation != null) {
      data['designation'] = designation;
    }

    if (qualification != null) {
      data['qualification'] = qualification;
    }

    if (joiningDate != null) {
      data['joining_date'] = joiningDate;
    }

    if (researchInterests != null) {
      data['research_interests'] = researchInterests;
    }

    if (bio != null) {
      data['bio'] = bio;
    }

    final response = await dio.patch(
      '/faculty/$facultyId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: data,
    );

    return Faculty.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Faculty> updateMyFacultyProfile({
    required String tenantSlug,
    required String collegeId,
    String? designation,
    String? qualification,
    String? joiningDate,
    String? researchInterests,
    String? bio,
  }) async {
    final data = <String, dynamic>{};

    if (designation != null) {
      data['designation'] = designation;
    }

    if (qualification != null) {
      data['qualification'] = qualification;
    }

    if (joiningDate != null) {
      data['joining_date'] = joiningDate;
    }

    if (researchInterests != null) {
      data['research_interests'] = researchInterests;
    }

    if (bio != null) {
      data['bio'] = bio;
    }

    final response = await dio.patch(
      '/faculty/me',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: data,
    );

    return Faculty.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Faculty> getMyFacultyProfile() async {
    final response = await dio.get('/faculty/me');

    return Faculty.fromJson(response.data as Map<String, dynamic>);
  }

  Future<User> updateUser({
    required String tenantSlug,
    required String collegeId,
    required String userId,
    String? name,
    String? phone,
    String? role,
    bool? isActive,
  }) async {
    final data = <String, dynamic>{};

    if (name != null) {
      data['name'] = name;
    }

    if (phone != null) {
      data['phone'] = phone;
    }

    if (role != null) {
      data['role'] = role;
    }

    if (isActive != null) {
      data['is_active'] = isActive;
    }

    final response = await dio.patch(
      '/users/$userId',
      options: Options(
        headers: {'X-Tenant-ID': tenantSlug, 'X-College-ID': collegeId},
      ),
      data: data,
    );

    return User.fromJson(response.data as Map<String, dynamic>);
  }
}
