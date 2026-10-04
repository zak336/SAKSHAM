import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/auth/auth_cubit.dart';
import '../../auth/data/models/auth_response.dart';
import '../../auth/data/repository/auth_repository.dart';

/// HOD Dashboard - Department-scoped management interface.
class HodDashboardScreen extends StatefulWidget {
  const HodDashboardScreen({super.key});

  @override
  State<HodDashboardScreen> createState() => _HodDashboardScreenState();
}

class _HodDashboardScreenState extends State<HodDashboardScreen> {
  late final AuthRepository _authRepository;
  late Future<UserProfile> _profileFuture;

  @override
  void initState() {
    super.initState();
    final dio = context.read<Dio>();
    _authRepository = AuthRepository(dio: dio);
    _profileFuture = _loadProfile();
  }

  Future<UserProfile> _loadProfile() async {
    return await _authRepository.getMe();
  }

  void _retry() {
    if (!mounted) return;
    setState(() {
      _profileFuture = _loadProfile();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('HOD Dashboard'),
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
      body: FutureBuilder<UserProfile>(
        future: _profileFuture,
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

          final profile = snapshot.data!;

          return ListView(
            padding: const EdgeInsets.all(24),
            children: [
              // Welcome Header
              Text(
                'Welcome, ${profile.name}',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 4),
              Text(
                'Head of Department',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Theme.of(context).colorScheme.primary,
                    ),
              ),

              const SizedBox(height: 32),

              // Department Overview Section
              Text(
                'Department Overview',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 12),

              const Row(
                children: [
                  Expanded(
                    child: _StatCard(
                      title: 'Faculty',
                      value: '0',
                      icon: Icons.people_outline,
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: _StatCard(
                      title: 'Students',
                      value: '0',
                      icon: Icons.school_outlined,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 12),

              const Row(
                children: [
                  Expanded(
                    child: _StatCard(
                      title: 'Courses',
                      value: '0',
                      icon: Icons.menu_book_outlined,
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: _StatCard(
                      title: 'Attendance',
                      value: '0%',
                      icon: Icons.fact_check_outlined,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 32),

              // Management Actions
              Text(
                'Management',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 12),

              _ActionTile(
                icon: Icons.account_tree_outlined,
                title: 'Departments',
                subtitle: 'View assigned departments',
                onTap: () {
                  // Navigate to departments
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Departments module')),
                  );
                },
              ),

              _ActionTile(
                icon: Icons.people_outline,
                title: 'Faculty',
                subtitle: 'Manage department faculty',
                onTap: () {
                  // Navigate to faculty management
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Faculty module')),
                  );
                },
              ),

              _ActionTile(
                icon: Icons.school_outlined,
                title: 'Students',
                subtitle: 'View department students',
                onTap: () {
                  // Navigate to students
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Students module')),
                  );
                },
              ),

              _ActionTile(
                icon: Icons.menu_book_outlined,
                title: 'Courses',
                subtitle: 'Manage department courses',
                onTap: () {
                  // Navigate to courses
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Courses module')),
                  );
                },
              ),

              _ActionTile(
                icon: Icons.fact_check_outlined,
                title: 'Attendance',
                subtitle: 'View attendance reports',
                onTap: () {
                  // Navigate to attendance
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Attendance module')),
                  );
                },
              ),

              const SizedBox(height: 32),

              // Reports Section
              Text(
                'Reports',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 12),

              _ActionTile(
                icon: Icons.assessment_outlined,
                title: 'Academic Reports',
                subtitle: 'Department performance reports',
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Reports module')),
                  );
                },
              ),
            ],
          );
        },
      ),
    );
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

class _ActionTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _ActionTile({
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
