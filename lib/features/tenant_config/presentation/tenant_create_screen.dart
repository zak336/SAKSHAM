import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../cubit/tenant_config_cubit.dart';
import '../cubit/tenant_config_state.dart';

class TenantCreateScreen extends StatefulWidget {
  const TenantCreateScreen({super.key});

  @override
  State<TenantCreateScreen> createState() =>
      _TenantCreateScreenState();
}

class _TenantCreateScreenState
    extends State<TenantCreateScreen> {
  final _formKey = GlobalKey<FormState>();

  final _nameController = TextEditingController();
  final _slugController = TextEditingController();

  @override
  void dispose() {
    _nameController.dispose();
    _slugController.dispose();
    super.dispose();
  }

  void _createTenant() {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    context.read<TenantConfigCubit>().createTenant(
          name: _nameController.text.trim(),
          slug: _slugController.text
              .trim()
              .toLowerCase(),
        );
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<TenantConfigCubit,
        TenantConfigState>(
      listener: (context, state) {
        if (state is TenantCreated) {
          Navigator.of(context).pop(true);
        }

        if (state is TenantConfigError) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(state.message),
            ),
          );
        }
      },
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Create Tenant'),
        ),
        body: Padding(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              children: [
                TextFormField(
                  controller: _nameController,
                  decoration: const InputDecoration(
                    labelText: 'College Name',
                    hintText: 'Example: GEC Raipur',
                  ),
                  validator: (value) {
                    if (value == null ||
                        value.trim().length < 2) {
                      return 'Enter a valid college name';
                    }

                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _slugController,
                  decoration: const InputDecoration(
                    labelText: 'Tenant ID',
                    hintText: 'Example: gec-raipur',
                    helperText:
                        'Lowercase letters, numbers and hyphens only',
                  ),
                  validator: (value) {
                    if (value == null ||
                        value.trim().length < 2) {
                      return 'Enter a valid tenant ID';
                    }

                    final regex =
                        RegExp(r'^[a-z0-9\-]+$');

                    if (!regex.hasMatch(
                      value.trim().toLowerCase(),
                    )) {
                      return 'Only lowercase letters, numbers and hyphens are allowed';
                    }

                    return null;
                  },
                ),
                const SizedBox(height: 32),
                BlocBuilder<TenantConfigCubit,
                    TenantConfigState>(
                  builder: (context, state) {
                    final loading =
                        state is TenantCreating;

                    return SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed:
                            loading ? null : _createTenant,
                        child: Padding(
                          padding: const EdgeInsets.all(14),
                          child: loading
                              ? const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child:
                                      CircularProgressIndicator(),
                                )
                              : const Text(
                                  'Create College',
                                ),
                        ),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}