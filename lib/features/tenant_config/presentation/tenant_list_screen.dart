import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../cubit/tenant_config_cubit.dart';
import '../cubit/tenant_config_state.dart';
import '../models/tenant.dart';
import 'tenant_create_screen.dart';
import 'tenant_manage_screen.dart';

class TenantListScreen extends StatefulWidget {
  const TenantListScreen({super.key});

  @override
  State<TenantListScreen> createState() => _TenantListScreenState();
}

class _TenantListScreenState extends State<TenantListScreen> {
  @override
  void initState() {
    super.initState();

    context.read<TenantConfigCubit>().loadTenants();
  }

  Future<void> _refresh() async {
    await context.read<TenantConfigCubit>().loadTenants();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Manage Colleges')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final created = await Navigator.of(context).push<bool>(
            MaterialPageRoute(builder: (_) => const TenantCreateScreen()),
          );

          if (created == true && mounted) {
            _refresh();
          }
        },
        icon: const Icon(Icons.add),
        label: const Text('Add Tenant'),
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
                    ElevatedButton(
                      onPressed: _refresh,
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            );
          }

          if (state is TenantListLoaded) {
            final tenants = state.tenants;

            if (tenants.isEmpty) {
              return const Center(child: Text('No colleges created yet.'));
            }

            return RefreshIndicator(
              onRefresh: _refresh,
              child: ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: tenants.length,
                separatorBuilder: (_, _) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  final Tenant tenant = tenants[index];

                  return Card(
                    child: ListTile(
                      leading: CircleAvatar(
                        child: Text(
                          tenant.name.isNotEmpty
                              ? tenant.name[0].toUpperCase()
                              : '?',
                        ),
                      ),
                      title: Text(tenant.name),
                      subtitle: Text(tenant.slug),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            tenant.isActive ? Icons.check_circle : Icons.cancel,
                            color: tenant.isActive ? Colors.green : Colors.red,
                          ),
                          const SizedBox(width: 8),
                          const Icon(Icons.chevron_right),
                        ],
                      ),
                      onTap: () async {
                        final cubit = context.read<TenantConfigCubit>();

                        await Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => TenantManageScreen(tenant: tenant),
                          ),
                        );

                        if (!mounted) return;

                        cubit.loadTenants();
                      },
                    ),
                  );
                },
              ),
            );
          }

          return const SizedBox();
        },
      ),
    );
  }
}
