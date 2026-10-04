import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/auth/auth_cubit.dart';
import '../../../core/auth/auth_state.dart';
import '../../auth/data/models/auth_response.dart';
import '../../auth/data/repository/auth_repository.dart';
import '../models/college.dart';
import '../models/faculty.dart';
import '../models/tenant.dart';
import '../repository/tenant_config_repository.dart';
import 'faculty_profile_screen.dart';

class FacultyHomeScreen extends StatefulWidget {
  const FacultyHomeScreen({super.key});

  @override
  State<FacultyHomeScreen> createState() => _FacultyHomeScreenState();
}

class _FacultyHomeScreenState extends State<FacultyHomeScreen> {
  late final AuthRepository _authRepository;
  late final TenantConfigRepository _repository;

  late Future<_FacultyContext> _future;

  @override
  void initState() {
    super.initState();

    final dio = context.read<Dio>();

    _authRepository = AuthRepository(dio: dio);

    _repository = TenantConfigRepository(dio);

    _future = _loadFacultyContext();
  }

  Future<_FacultyContext> _loadFacultyContext() async {
    final authState = context.read<AuthCubit>().state;

    if (authState is! AuthAuthenticated) {
      throw StateError('Authenticated session is unavailable.');
    }

    final profile = await _authRepository.getMe();

    if (profile.collegeId == null) {
      throw StateError('This faculty account is not assigned to a college.');
    }

    final college = await _repository.getMyCollege();

    final facultyResponse = await _repository.getMyFacultyProfile();

    final tenant = Tenant(
      id: profile.tenantId,
      name: authState.tenantSlug,
      slug: authState.tenantSlug,
      isActive: true,
    );

    return _FacultyContext(
      profile: profile,
      faculty: facultyResponse,
      college: college,
      tenant: tenant,
    );
  }

  void _retry() {
    if (!mounted) return;

    setState(() {
      _future = _loadFacultyContext();
    });
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<_FacultyContext>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        if (snapshot.hasError) {
          return Scaffold(
            appBar: AppBar(title: const Text('Faculty')),
            body: Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.error_outline, size: 48),
                    const SizedBox(height: 16),
                    Text(
                      snapshot.error.toString(),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    FilledButton(onPressed: _retry, child: const Text('Retry')),
                  ],
                ),
              ),
            ),
          );
        }

        final data = snapshot.data!;

        return FacultyProfileScreen(
          tenant: data.tenant,
          college: data.college,
          facultyId: data.faculty.id,
          facultyName: data.profile.name,
          initialFaculty: data.faculty,
        );
      },
    );
  }
}

class _FacultyContext {
  final UserProfile profile;
  final Faculty faculty;
  final College college;
  final Tenant tenant;

  const _FacultyContext({
    required this.profile,
    required this.faculty,
    required this.college,
    required this.tenant,
  });
}
