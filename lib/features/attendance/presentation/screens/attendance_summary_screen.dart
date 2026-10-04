import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/auth/auth_cubit.dart';
import '../../logic/attendance_summary_cubit.dart';
import '../widgets/attendance_course_card.dart';

class AttendanceSummaryScreen extends StatefulWidget {
  const AttendanceSummaryScreen({super.key});

  @override
  State<AttendanceSummaryScreen> createState() =>
      _AttendanceSummaryScreenState();
}

class _AttendanceSummaryScreenState extends State<AttendanceSummaryScreen> {
  @override
  void initState() {
    super.initState();
    context.read<AttendanceSummaryCubit>().loadSummary();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Attendance'),
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
      body: BlocBuilder<AttendanceSummaryCubit, AttendanceSummaryState>(
        builder: (context, state) => switch (state) {
          AttendanceSummaryInitial() ||
          AttendanceSummaryLoading() =>
            const Center(child: CircularProgressIndicator()),
          AttendanceSummaryLoaded(:final summaries) => summaries.isEmpty
              ? const Center(child: Text('No attendance data available.'))
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: summaries.length,
                  separatorBuilder: (_, _) => const SizedBox(height: 12),
                  itemBuilder: (context, index) =>
                      AttendanceCourseCard(summary: summaries[index]),
                ),
          AttendanceSummaryError(:final message) => Center(
              child: Text(
                message,
                style:
                    TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            ),
        },
      ),
    );
  }
}
