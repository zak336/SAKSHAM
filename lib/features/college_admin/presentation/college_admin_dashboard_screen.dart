import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../auth/data/models/auth_response.dart';
import '../../auth/data/repository/auth_repository.dart';
import '../../tenant_config/models/college.dart';
import '../../tenant_config/models/tenant.dart';
import '../../tenant_config/repository/tenant_config_repository.dart';
import '../../tenant_config/presentation/college_manage_screen.dart';
import '../../../core/auth/auth_cubit.dart';
import '../../../core/auth/auth_state.dart';

class CollegeAdminDashboardScreen extends StatefulWidget {
  const CollegeAdminDashboardScreen({super.key});

  @override
  State<CollegeAdminDashboardScreen> createState() =>
      _CollegeAdminDashboardScreenState();
}

class _CollegeAdminDashboardScreenState
    extends State<CollegeAdminDashboardScreen> {
  late final AuthRepository _authRepository;
  late final TenantConfigRepository _tenantRepository;

  late Future<_AdminDashboardData> _dashboardFuture;

  @override
  void initState() {
    super.initState();

    final dio = context.read<Dio>();
    _authRepository = AuthRepository(dio: dio);
    _tenantRepository = TenantConfigRepository(dio);
    _dashboardFuture = _loadDashboardData();
  }

  Future<_AdminDashboardData> _loadDashboardData() async {
    final authState = context.read<AuthCubit>().state;

    if (authState is! AuthAuthenticated) {
      throw StateError('Authenticated tenant context is unavailable.');
    }

    final tenantSlug = authState.tenantSlug;

    final profile = await _authRepository.getMe();

    if (profile.collegeId == null) {
      throw Exception('This admin account is not assigned to a college.');
    }

    final college = await _tenantRepository.getMyCollege();

    return _AdminDashboardData(
      profile: profile,
      college: college,
      tenant: Tenant(
        id: profile.tenantId,
        name: college.name,
        slug: tenantSlug,
        isActive: true,
      ),
    );
  }

  void _retry() {
    if (!mounted) return;

    setState(() {
      _dashboardFuture = _loadDashboardData();
    });
  }

  void _openCollegeManagement(_AdminDashboardData data) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) =>
            CollegeManageScreen(tenant: data.tenant, college: data.college),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('College Admin'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: () {
              context.read<AuthCubit>().logout();
            },
          ),
        ],
      ),
      body: FutureBuilder<_AdminDashboardData>(
        future: _dashboardFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(
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
            );
          }

          final data = snapshot.data!;

          return ListView(
            padding: const EdgeInsets.all(24),
            children: [
              Text(
                data.college.name,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 4),
              Text(
                '${data.college.code} • '
                '${data.college.slug}',
              ),
              const SizedBox(height: 4),
              Text(
                'Welcome, '
                '${data.profile.name}',
                style: Theme.of(context).textTheme.bodyLarge,
              ),

              const SizedBox(height: 32),

              const _SectionTitle(title: 'Overview'),
              const SizedBox(height: 12),

              const Row(
                children: [
                  Expanded(
                    child: _StatCard(
                      title: 'Departments',
                      value: '0',
                      icon: Icons.account_tree_outlined,
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: _StatCard(
                      title: 'Faculty',
                      value: '0',
                      icon: Icons.people_outline,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 12),

              const Row(
                children: [
                  Expanded(
                    child: _StatCard(
                      title: 'Students',
                      value: '0',
                      icon: Icons.school_outlined,
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: _StatCard(
                      title: 'Courses',
                      value: '0',
                      icon: Icons.menu_book_outlined,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 32),

              const _SectionTitle(title: 'Management'),
              const SizedBox(height: 12),

              _AdminActionTile(
                icon: Icons.account_tree_outlined,
                title: 'Departments',
                subtitle: 'Manage college departments',
                onTap: () => _openCollegeManagement(data),
              ),

              _AdminActionTile(
                icon: Icons.people_outline,
                title: 'Faculty',
                subtitle: 'Manage faculty members',
                onTap: () => _openCollegeManagement(data),
              ),

              _AdminActionTile(
                icon: Icons.school_outlined,
                title: 'Students',
                subtitle: 'Manage student records',
                onTap: () {},
              ),

              _AdminActionTile(
                icon: Icons.menu_book_outlined,
                title: 'Courses',
                subtitle: 'Manage courses and subjects',
                onTap: () {},
              ),

              const SizedBox(height: 32),

              const _SectionTitle(title: 'Academic Operations'),
              const SizedBox(height: 12),

              _AdminActionTile(
                icon: Icons.fact_check_outlined,
                title: 'Attendance',
                subtitle: 'View attendance and reports',
                onTap: () {},
              ),

              _AdminActionTile(
                icon: Icons.assessment_outlined,
                title: 'Marks',
                subtitle: 'Manage assessments and marks',
                onTap: () {},
              ),

              _AdminActionTile(
                icon: Icons.calendar_month_outlined,
                title: 'Timetable',
                subtitle: 'Manage academic schedules',
                onTap: () {},
              ),
            ],
          );
        },
      ),
    );
  }
}

class _AdminDashboardData {
  final UserProfile profile;
  final College college;
  final Tenant tenant;

  const _AdminDashboardData({
    required this.profile,
    required this.college,
    required this.tenant,
  });
}

class _SectionTitle extends StatelessWidget {
  final String title;

  const _SectionTitle({required this.title});

  @override
  Widget build(BuildContext context) {
    return Text(title, style: Theme.of(context).textTheme.titleLarge);
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;

  const _StatCard({
    required this.title,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon),
            const SizedBox(height: 14),
            Text(value, style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 4),
            Text(title),
          ],
        ),
      ),
    );
  }
}

class _AdminActionTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _AdminActionTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: Icon(icon),
        title: Text(title),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}
