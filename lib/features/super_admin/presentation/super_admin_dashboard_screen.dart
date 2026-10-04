import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/auth/auth_cubit.dart';
import '../../tenant_config/cubit/tenant_config_cubit.dart';
import '../../tenant_config/cubit/tenant_config_state.dart';
import '../../tenant_config/models/tenant.dart';
import '../../tenant_config/presentation/tenant_create_screen.dart';
import '../../tenant_config/presentation/tenant_list_screen.dart';
import '../../tenant_config/presentation/tenant_manage_screen.dart';
import '../../tenant_config/repository/tenant_config_repository.dart';

class SuperAdminDashboardScreen extends StatefulWidget {
  const SuperAdminDashboardScreen({super.key});

  @override
  State<SuperAdminDashboardScreen> createState() =>
      _SuperAdminDashboardScreenState();
}

class _SuperAdminDashboardScreenState extends State<SuperAdminDashboardScreen> {
  late final TenantConfigRepository _repository;

  @override
  void initState() {
    super.initState();

    _repository = TenantConfigRepository(context.read<Dio>());

    Future.microtask(() {
      if (!mounted) return;

      context.read<TenantConfigCubit>().loadTenants();
    });
  }

  Future<void> _toggleTenant(Tenant tenant, bool isActive) async {
    final cubit = context.read<TenantConfigCubit>();
    
    try {
      await _repository.updateTenant(tenantId: tenant.id, isActive: isActive);

      if (!mounted) return;

      await cubit.loadTenants();

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isActive
                ? '${tenant.name} activated.'
                : '${tenant.name} deactivated.',
          ),
        ),
      );
    } catch (error) {
      if (!mounted) return;

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(error.toString())));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ZakCERP Super Admin'),
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
      body: BlocBuilder<TenantConfigCubit, TenantConfigState>(
        builder: (context, state) {
          if (state is TenantListLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (state is TenantConfigError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(state.message, textAlign: TextAlign.center),
                    const SizedBox(height: 16),
                    FilledButton(
                      onPressed: () {
                        context.read<TenantConfigCubit>().loadTenants();
                      },
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            );
          }

          if (state is TenantListLoaded) {
            final tenants = state.tenants;

            final activeTenants = tenants
                .where((tenant) => tenant.isActive)
                .length;

            return RefreshIndicator(
              onRefresh: () async {
                await context.read<TenantConfigCubit>().loadTenants();
              },
              child: ListView(
                padding: const EdgeInsets.all(20),
                children: [
                  Text(
                    'Platform Overview',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 16),

                  Row(
                    children: [
                      Expanded(
                        child: _StatCard(
                          title: 'Tenants',
                          value: '${tenants.length}',
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _StatCard(
                          title: 'Active',
                          value: '$activeTenants',
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 28),

                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Tenants',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      FilledButton.icon(
                        onPressed: () async {
                          final cubit = context.read<TenantConfigCubit>();

                          final created = await Navigator.of(context)
                              .push<bool>(
                                MaterialPageRoute(
                                  builder: (_) => const TenantCreateScreen(),
                                ),
                              );

                          if (!mounted) return;

                          if (created == true) {
                            await cubit.loadTenants();
                          }
                        },
                        icon: const Icon(Icons.add),
                        label: const Text('Create Tenant'),
                      ),
                    ],
                  ),

                  const SizedBox(height: 12),

                  if (tenants.isEmpty)
                    const Card(
                      child: Padding(
                        padding: EdgeInsets.all(20),
                        child: Text('No tenants have been created yet.'),
                      ),
                    ),

                  for (final tenant in tenants)
                    Card(
                      margin: const EdgeInsets.only(bottom: 10),
                      child: ListTile(
                        leading: CircleAvatar(
                          child: Text(
                            tenant.name.isNotEmpty
                                ? tenant.name[0].toUpperCase()
                                : '?',
                          ),
                        ),
                        title: Text(tenant.name),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(tenant.slug),
                            const SizedBox(height: 4),
                            Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(
                                  tenant.isActive
                                      ? Icons.check_circle
                                      : Icons.cancel,
                                  size: 15,
                                  color: tenant.isActive
                                      ? Colors.green
                                      : Colors.red,
                                ),
                                const SizedBox(width: 5),
                                Text(tenant.isActive ? 'Active' : 'Inactive'),
                              ],
                            ),
                          ],
                        ),
                        trailing: SizedBox(
                          width: 130,
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.end,
                            children: [
                              Switch(
                                value: tenant.isActive,
                                onChanged: (value) {
                                  _toggleTenant(tenant, value);
                                },
                              ),
                              const SizedBox(width: 4),
                              const Icon(Icons.chevron_right),
                            ],
                          ),
                        ),
                        onTap: () async {
                          final cubit = context.read<TenantConfigCubit>();

                          await Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) =>
                                  TenantManageScreen(tenant: tenant),
                            ),
                          );

                          if (!mounted) return;

                          await cubit.loadTenants();
                        },
                      ),
                    ),

                  const SizedBox(height: 28),

                  Text(
                    'Platform Management',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),

                  const SizedBox(height: 12),

                  Card(
                    child: ListTile(
                      leading: const Icon(Icons.business),
                      title: const Text('Manage Tenants'),
                      subtitle: const Text(
                        'Create and configure customer organizations',
                      ),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => const TenantListScreen(),
                          ),
                        );
                      },
                    ),
                  ),

                  Card(
                    child: ListTile(
                      leading: const Icon(Icons.extension),
                      title: const Text('Module Management'),
                      subtitle: const Text('Configure modules for each tenant'),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => const TenantListScreen(),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
            );
          }

          return const SizedBox();
        },
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title;
  final String value;

  const _StatCard({required this.title, required this.value});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.bodyMedium),
            const SizedBox(height: 6),
            Text(value, style: Theme.of(context).textTheme.headlineMedium),
          ],
        ),
      ),
    );
  }
}
