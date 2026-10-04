import '../../features/tenant_config/presentation/tenant_list_screen.dart';
import 'package:dio/dio.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../features/academics/data/repository/academics_repository.dart';
import '../../features/academics/logic/academics_cubit.dart';
import '../../features/academics/presentation/screens/academics_screen.dart';
import '../../features/attendance/data/repository/attendance_repository.dart';
import '../../features/attendance/logic/attendance_summary_cubit.dart';
import '../../features/attendance/presentation/screens/attendance_summary_screen.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/hod/presentation/hod_dashboard_screen.dart';
import '../../features/notices/presentation/screens/notices_screen.dart';
import '../../features/placements/presentation/screens/placements_screen.dart';
import '../../features/results/presentation/screens/results_screen.dart';
import '../../features/timetable/presentation/screens/timetable_screen.dart';
import '../../features/super_admin/presentation/super_admin_dashboard_screen.dart';
import 'package:cepr/features/college_admin/presentation/college_admin_dashboard_screen.dart';
import '../../features/tenant_config/presentation/faculty_home_screen.dart';
import '../auth/auth_cubit.dart';
import '../auth/auth_state.dart';

/// Creates the app router wired to [authCubit] for auth-based redirects.
/// [dio] is the authenticated Dio instance (has token + tenant headers).
GoRouter createAppRouter({required AuthCubit authCubit, required Dio dio}) {
  return GoRouter(
    initialLocation: '/login',
    refreshListenable: _AuthListenable(authCubit),
    redirect: (context, state) {
      final authState = authCubit.state;
      final isLoginRoute = state.matchedLocation == '/login';

      if (authState is AuthInitial) return null;

      if (authState is AuthUnauthenticated || authState is AuthError) {
        return isLoginRoute ? null : '/login';
      }

      if (authState is AuthAuthenticated && isLoginRoute) {
        return _homeForRole(authState.role);
      }

      return null;
    },
    routes: [
      // ── Auth ──────────────────────────────────────────────────────────────
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),

      GoRoute(
        path: '/admin',
        name: 'super-admin',
        builder: (context, state) => const SuperAdminDashboardScreen(),
      ),

      // ── Super Admin ───────────────────────────────────────────────────────
      GoRoute(
        path: '/admin/tenants',
        name: 'tenant-management',
        builder: (context, state) => const TenantListScreen(),
      ),

      // ── HOD ───────────────────────────────────────────────────────────────
      GoRoute(
        path: '/hod',
        name: 'hod',
        builder: (context, state) => const HodDashboardScreen(),
      ),

      // ── Faculty ─────────────────────────────────────────────────────────────
      GoRoute(
        path: '/faculty',
        name: 'faculty',
        builder: (context, state) => const FacultyHomeScreen(),
      ),

      // ── Attendance ────────────────────────────────────────────────────────
      GoRoute(
        path: '/attendance',
        name: 'attendance',
        builder: (context, state) => BlocProvider(
          create: (_) => AttendanceSummaryCubit(
            repository: AttendanceRepository(dio: dio),
          ),
          child: const AttendanceSummaryScreen(),
        ),
      ),

      // ── Academics ─────────────────────────────────────────────────────────
      GoRoute(
        path: '/academics',
        name: 'academics',
        builder: (context, state) => BlocProvider(
          create: (_) =>
              AcademicsCubit(repository: AcademicsRepository(dio: dio)),
          child: const AcademicsScreen(),
        ),
      ),

      // ── Placements ────────────────────────────────────────────────────────
      GoRoute(
        path: '/placements',
        name: 'placements',
        builder: (context, state) => const PlacementsScreen(),
      ),

      // ── Timetable ─────────────────────────────────────────────────────────
      GoRoute(
        path: '/timetable',
        name: 'timetable',
        builder: (context, state) => const TimetableScreen(),
      ),

      // ── Notices ───────────────────────────────────────────────────────────
      GoRoute(
        path: '/notices',
        name: 'notices',
        builder: (context, state) => const NoticesScreen(),
      ),

      // ── Results ───────────────────────────────────────────────────────────
      GoRoute(
        path: '/results',
        name: 'results',
        builder: (context, state) => const ResultsScreen(),
      ),

      // ── College Admin ───────────────────────────────────────────────────────
      GoRoute(
        path: '/college-admin',
        name: 'college-admin',
        builder: (context, state) => const CollegeAdminDashboardScreen(),
      ),
    ],
  );
}

/// Maps a user role to their default home route after login.
String _homeForRole(String role) {
  return switch (role) {
    'super_admin' => '/admin',
    'admin' => '/college-admin',
    'hod' => '/hod',
    'faculty' => '/faculty',
    'placement_officer' => '/placements',
    'parent' => '/academics',
    'student' => '/academics',
    _ => '/academics',
  };
}

/// Makes GoRouter re-evaluate its redirect whenever AuthState changes.
class _AuthListenable extends ChangeNotifier {
  _AuthListenable(AuthCubit cubit) {
    cubit.stream.listen((_) => notifyListeners());
  }
}
