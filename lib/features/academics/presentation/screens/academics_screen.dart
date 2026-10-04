import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/auth/auth_cubit.dart';
import '../../logic/academics_cubit.dart';

class AcademicsScreen extends StatefulWidget {
  const AcademicsScreen({super.key});

  @override
  State<AcademicsScreen> createState() => _AcademicsScreenState();
}

class _AcademicsScreenState extends State<AcademicsScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    context.read<AcademicsCubit>().load();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Academics'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: () {
              context.read<AuthCubit>().logout();
            },
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Departments'),
            Tab(text: 'Courses'),
          ],
        ),
      ),
      body: BlocBuilder<AcademicsCubit, AcademicsState>(
        builder: (context, state) => switch (state) {
          AcademicsInitial() || AcademicsLoading() =>
            const Center(child: CircularProgressIndicator()),
          AcademicsError(:final message) => Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    message,
                    style: TextStyle(color: theme.colorScheme.error),
                  ),
                  const SizedBox(height: 12),
                  FilledButton.tonal(
                    onPressed: () => context.read<AcademicsCubit>().load(),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
          AcademicsLoaded(:final departments, :final courses) => TabBarView(
              controller: _tabController,
              children: [
                // ── Departments tab ──────────────────────────────────────
                departments.isEmpty
                    ? const Center(child: Text('No departments yet.'))
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: departments.length,
                        itemBuilder: (context, i) {
                          final d = departments[i];
                          return Card(
                            child: ListTile(
                              leading: CircleAvatar(child: Text(d.code[0])),
                              title: Text(d.name),
                              subtitle: Text('Code: ${d.code}'),
                              trailing: d.isActive
                                  ? null
                                  : Chip(
                                      label: const Text('Inactive'),
                                      backgroundColor:
                                          theme.colorScheme.errorContainer,
                                    ),
                            ),
                          );
                        },
                      ),

                // ── Courses tab ─────────────────────────────────────────
                courses.isEmpty
                    ? const Center(child: Text('No courses yet.'))
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: courses.length,
                        itemBuilder: (context, i) {
                          final c = courses[i];
                          return Card(
                            child: ListTile(
                              leading: CircleAvatar(child: Text('S${c.semester}')),
                              title: Text(c.name),
                              subtitle: Text(
                                '${c.code} · ${c.credits} credits · Sem ${c.semester}',
                              ),
                              trailing: c.isActive
                                  ? null
                                  : Chip(
                                      label: const Text('Inactive'),
                                      backgroundColor:
                                          theme.colorScheme.errorContainer,
                                    ),
                            ),
                          );
                        },
                      ),
              ],
            ),
        },
      ),
    );
  }
}
