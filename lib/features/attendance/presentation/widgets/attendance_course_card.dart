import 'package:flutter/material.dart';

import '../../data/models/attendance_summary.dart';

class AttendanceCourseCard extends StatelessWidget {
  const AttendanceCourseCard({super.key, required this.summary});

  final AttendanceSummary summary;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isLow = summary.belowThreshold;
    final color = isLow ? theme.colorScheme.error : theme.colorScheme.primary;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(summary.courseName, style: theme.textTheme.titleMedium),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: summary.percentage / 100,
              color: color,
              semanticsLabel: '${summary.percentage.toStringAsFixed(1)}% attendance',
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${summary.attendedSessions}/${summary.totalSessions} classes',
                  style: theme.textTheme.bodySmall,
                ),
                Text(
                  '${summary.percentage.toStringAsFixed(1)}%',
                  style: theme.textTheme.labelLarge?.copyWith(color: color),
                ),
              ],
            ),
            if (isLow) ...[
              const SizedBox(height: 6),
              Text(
                'Below minimum attendance threshold',
                style: theme.textTheme.bodySmall?.copyWith(color: color),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
