import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'theme/app_theme.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/register_screen.dart';
import 'screens/dashboard/dashboard_screen.dart';
import 'screens/card/card_screen.dart';
import 'screens/card/card_edit_screen.dart';
import 'screens/crm/contacts_screen.dart';
import 'screens/crm/contact_detail_screen.dart';
import 'screens/crm/pipeline_screen.dart';
import 'screens/crm/tasks_screen.dart';
import 'screens/settings/settings_screen.dart';

final _router = GoRouter(
  initialLocation: '/login',
  routes: [
    GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
    GoRoute(path: '/register', builder: (_, __) => const RegisterScreen()),
    ShellRoute(
      builder: (context, state, child) => MainShell(child: child),
      routes: [
        GoRoute(path: '/dashboard', builder: (_, __) => const DashboardScreen()),
        GoRoute(path: '/card', builder: (_, __) => const CardScreen()),
        GoRoute(path: '/card/edit', builder: (_, __) => const CardEditScreen()),
        GoRoute(path: '/crm/contacts', builder: (_, __) => const ContactsScreen()),
        GoRoute(
          path: '/crm/contacts/:id',
          builder: (_, state) =>
              ContactDetailScreen(contactId: int.parse(state.pathParameters['id']!)),
        ),
        GoRoute(path: '/crm/pipeline', builder: (_, __) => const PipelineScreen()),
        GoRoute(path: '/crm/tasks', builder: (_, __) => const TasksScreen()),
        GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen()),
      ],
    ),
  ],
);

class CarteProApp extends StatelessWidget {
  const CarteProApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp.router(
        title: 'CartePro Pro',
        theme: AppTheme.light,
        routerConfig: _router,
        debugShowCheckedModeBanner: false,
      );
}

class MainShell extends StatelessWidget {
  final Widget child;
  const MainShell({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _navIndex(location),
        onDestinationSelected: (i) => _navigate(context, i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined),
              selectedIcon: Icon(Icons.home), label: 'Accueil'),
          NavigationDestination(icon: Icon(Icons.badge_outlined),
              selectedIcon: Icon(Icons.badge), label: 'Ma carte'),
          NavigationDestination(icon: Icon(Icons.people_outline),
              selectedIcon: Icon(Icons.people), label: 'CRM'),
          NavigationDestination(icon: Icon(Icons.task_outlined),
              selectedIcon: Icon(Icons.task), label: 'Tâches'),
          NavigationDestination(icon: Icon(Icons.settings_outlined),
              selectedIcon: Icon(Icons.settings), label: 'Réglages'),
        ],
      ),
    );
  }

  int _navIndex(String location) {
    if (location.startsWith('/card')) return 1;
    if (location.startsWith('/crm/pipeline') || location.startsWith('/crm/contacts')) return 2;
    if (location.startsWith('/crm/tasks')) return 3;
    if (location.startsWith('/settings')) return 4;
    return 0;
  }

  void _navigate(BuildContext context, int index) {
    switch (index) {
      case 0: context.go('/dashboard');
      case 1: context.go('/card');
      case 2: context.go('/crm/contacts');
      case 3: context.go('/crm/tasks');
      case 4: context.go('/settings');
    }
  }
}
