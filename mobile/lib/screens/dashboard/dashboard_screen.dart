import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

final _dashboardProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return ApiService.instance.getCrmDashboard();
});

final _meProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return ApiService.instance.getMe();
});

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashAsync = ref.watch(_dashboardProvider);
    final meAsync = ref.watch(_meProvider);

    return Scaffold(
      backgroundColor: AppTheme.surface,
      appBar: AppBar(
        title: const Text('Tableau de bord'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.invalidate(_dashboardProvider);
              ref.invalidate(_meProvider);
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(_dashboardProvider);
          ref.invalidate(_meProvider);
        },
        child: meAsync.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => _ErrorView(onRetry: () => ref.invalidate(_meProvider)),
          data: (me) => dashAsync.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (e, _) => _ErrorView(onRetry: () => ref.invalidate(_dashboardProvider)),
            data: (dash) => _DashboardBody(me: me, dash: dash),
          ),
        ),
      ),
    );
  }
}

class _DashboardBody extends StatelessWidget {
  final Map<String, dynamic> me;
  final Map<String, dynamic> dash;

  const _DashboardBody({required this.me, required this.dash});

  @override
  Widget build(BuildContext context) {
    final username = me['username'] ?? '';
    final pipeline = dash['pipeline'] as Map<String, dynamic>? ?? {};
    final tasksDueToday = dash['tasks_due_today'] as int? ?? 0;
    final convRate = (dash['conversion_rate'] as num?)?.toDouble() ?? 0.0;
    final totalContacts = pipeline.values
        .map((v) => (v as num?)?.toInt() ?? 0)
        .fold(0, (a, b) => a + b);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _GreetingCard(username: username),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _StatCard(
                label: 'Contacts total',
                value: '$totalContacts',
                icon: Icons.people_outline,
                color: AppTheme.primary,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _StatCard(
                label: 'Taux conversion',
                value: '${convRate.toStringAsFixed(1)}%',
                icon: Icons.trending_up,
                color: AppTheme.secondary,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _StatCard(
                label: 'Tâches aujourd\'hui',
                value: '$tasksDueToday',
                icon: Icons.task_alt,
                color: tasksDueToday > 0 ? AppTheme.warning : AppTheme.secondary,
                onTap: () => GoRouter.of(context).go('/crm/tasks'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _StatCard(
                label: 'Clients gagnés',
                value: '${pipeline['won'] ?? 0}',
                icon: Icons.emoji_events_outlined,
                color: AppTheme.secondary,
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),
        Text(
          'Entonnoir de vente',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
                color: AppTheme.textPrimary,
              ),
        ),
        const SizedBox(height: 12),
        _PipelineSummary(pipeline: pipeline),
        const SizedBox(height: 20),
        Text(
          'Accès rapide',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
                color: AppTheme.textPrimary,
              ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _QuickAction(
                icon: Icons.person_add_outlined,
                label: 'Ajouter contact',
                onTap: () => GoRouter.of(context).go('/crm/contacts'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _QuickAction(
                icon: Icons.view_kanban_outlined,
                label: 'Pipeline',
                onTap: () => GoRouter.of(context).go('/crm/pipeline'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _QuickAction(
                icon: Icons.badge_outlined,
                label: 'Ma carte',
                onTap: () => GoRouter.of(context).go('/card'),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _GreetingCard extends StatelessWidget {
  final String username;
  const _GreetingCard({required this.username});

  @override
  Widget build(BuildContext context) {
    final hour = DateTime.now().hour;
    final greeting = hour < 12 ? 'Bonjour' : hour < 18 ? 'Bon après-midi' : 'Bonsoir';

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppTheme.primary, Color(0xFF2563EB)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '$greeting, $username !',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Voici votre résumé CartePro Pro',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.85),
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
          const Icon(Icons.badge, color: Colors.white, size: 42),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;
  final VoidCallback? onTap;

  const _StatCard({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFE5E7EB)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: color, size: 22),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                  fontSize: 26, fontWeight: FontWeight.w800, color: color),
            ),
            const SizedBox(height: 2),
            Text(label,
                style: const TextStyle(
                    fontSize: 12, color: AppTheme.textSecondary)),
          ],
        ),
      ),
    );
  }
}

class _PipelineSummary extends StatelessWidget {
  final Map<String, dynamic> pipeline;
  const _PipelineSummary({required this.pipeline});

  static const _stages = [
    ('new', 'Nouveau', AppTheme.textSecondary),
    ('contacted', 'Contacté', AppTheme.primary),
    ('quote_sent', 'Soumission', AppTheme.warning),
    ('won', 'Gagné', AppTheme.secondary),
    ('lost', 'Perdu', AppTheme.danger),
  ];

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: _stages.map((s) {
            final count = (pipeline[s.$1] as num?)?.toInt() ?? 0;
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 6),
              child: Row(
                children: [
                  Container(
                    width: 10,
                    height: 10,
                    decoration: BoxDecoration(
                      color: s.$3,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(s.$2,
                        style: const TextStyle(
                            color: AppTheme.textPrimary, fontSize: 14)),
                  ),
                  Text(
                    '$count',
                    style: TextStyle(
                        fontWeight: FontWeight.w700,
                        color: s.$3,
                        fontSize: 16),
                  ),
                ],
              ),
            );
          }).toList(),
        ),
      ),
    );
  }
}

class _QuickAction extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _QuickAction({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFE5E7EB)),
        ),
        child: Column(
          children: [
            Icon(icon, color: AppTheme.primary, size: 24),
            const SizedBox(height: 6),
            Text(label,
                textAlign: TextAlign.center,
                style: const TextStyle(
                    fontSize: 11,
                    color: AppTheme.textPrimary,
                    fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  final VoidCallback onRetry;
  const _ErrorView({required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.wifi_off, size: 48, color: AppTheme.textSecondary),
          const SizedBox(height: 12),
          const Text('Impossible de charger les données'),
          const SizedBox(height: 12),
          TextButton(onPressed: onRetry, child: const Text('Réessayer')),
        ],
      ),
    );
  }
}
