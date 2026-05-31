import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

final _meSettingsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return ApiService.instance.getMe();
});

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final meAsync = ref.watch(_meSettingsProvider);

    return Scaffold(
      backgroundColor: AppTheme.surface,
      appBar: AppBar(title: const Text('Réglages')),
      body: meAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Erreur de chargement'),
              TextButton(
                onPressed: () => ref.invalidate(_meSettingsProvider),
                child: const Text('Réessayer'),
              ),
            ],
          ),
        ),
        data: (me) => _SettingsBody(me: me, ref: ref),
      ),
    );
  }
}

class _SettingsBody extends StatelessWidget {
  final Map<String, dynamic> me;
  final WidgetRef ref;

  const _SettingsBody({required this.me, required this.ref});

  @override
  Widget build(BuildContext context) {
    final username = me['username'] as String? ?? '';
    final email = me['email'] as String? ?? '';
    final planType = me['plan_type'] as String? ?? 'none';
    final isPro = planType != 'none';

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _ProfileCard(username: username, email: email, planType: planType),
        const SizedBox(height: 20),
        _SectionTitle(label: 'Abonnement'),
        _SubscriptionCard(planType: planType, isPro: isPro),
        const SizedBox(height: 20),
        _SectionTitle(label: 'Application'),
        _SettingTile(
          icon: Icons.badge_outlined,
          label: 'Ma carte numérique',
          onTap: () => context.go('/card'),
        ),
        _SettingTile(
          icon: Icons.people_outline,
          label: 'Mes contacts CRM',
          onTap: () => context.go('/crm/contacts'),
        ),
        _SettingTile(
          icon: Icons.task_outlined,
          label: 'Mes tâches',
          onTap: () => context.go('/crm/tasks'),
        ),
        const SizedBox(height: 20),
        _SectionTitle(label: 'Compte'),
        _SettingTile(
          icon: Icons.info_outline,
          label: 'Version',
          trailing: const Text('1.0.0',
              style: TextStyle(color: AppTheme.textSecondary, fontSize: 14)),
        ),
        const SizedBox(height: 8),
        _LogoutButton(ref: ref),
        const SizedBox(height: 32),
      ],
    );
  }
}

class _ProfileCard extends StatelessWidget {
  final String username;
  final String email;
  final String planType;

  const _ProfileCard({
    required this.username,
    required this.email,
    required this.planType,
  });

  @override
  Widget build(BuildContext context) {
    final isPro = planType != 'none';
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE5E7EB)),
      ),
      child: Row(
        children: [
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: AppTheme.primary.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                username.isNotEmpty ? username[0].toUpperCase() : '?',
                style: const TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.primary),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(username,
                    style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.textPrimary)),
                Text(email,
                    style: const TextStyle(
                        fontSize: 13, color: AppTheme.textSecondary)),
                const SizedBox(height: 6),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                  decoration: BoxDecoration(
                    color: isPro
                        ? AppTheme.secondary.withOpacity(0.12)
                        : AppTheme.textSecondary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    _planLabel(planType),
                    style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: isPro ? AppTheme.secondary : AppTheme.textSecondary),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _planLabel(String plan) => switch (plan) {
        'monthly' => 'Pro Mensuel',
        'annual' => 'Pro Annuel',
        _ => 'Gratuit',
      };
}

class _SubscriptionCard extends StatefulWidget {
  final String planType;
  final bool isPro;

  const _SubscriptionCard({required this.planType, required this.isPro});

  @override
  State<_SubscriptionCard> createState() => _SubscriptionCardState();
}

class _SubscriptionCardState extends State<_SubscriptionCard> {
  bool _loadingCheckout = false;

  Future<void> _subscribe(String plan) async {
    setState(() => _loadingCheckout = true);
    try {
      final data = await ApiService.instance.createCheckout(plan);
      final url = data['checkout_url'] as String?;
      if (url != null && mounted) {
        _showCheckoutInfo(url);
      }
    } on DioException catch (e) {
      final msg = e.response?.data?['message'] as String? ?? 'Erreur';
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
      }
    } finally {
      if (mounted) setState(() => _loadingCheckout = false);
    }
  }

  void _showCheckoutInfo(String url) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Paiement Stripe'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Ouvrez ce lien pour finaliser votre abonnement :'),
            const SizedBox(height: 8),
            SelectableText(url,
                style: const TextStyle(
                    fontSize: 12, color: AppTheme.primary,
                    decoration: TextDecoration.underline)),
          ],
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('OK')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (widget.isPro) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              const Icon(Icons.workspace_premium, color: AppTheme.secondary, size: 28),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('CartePro Pro actif',
                        style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15)),
                    Text(
                      widget.planType == 'monthly' ? '15 \$/mois' : '120 \$/an',
                      style: const TextStyle(
                          color: AppTheme.textSecondary, fontSize: 13),
                    ),
                  ],
                ),
              ),
              TextButton(
                onPressed: () async {
                  try {
                    final data = await ApiService.instance.getCustomerPortal();
                    final url = data['portal_url'] as String?;
                    if (url != null && context.mounted) {
                      _showCheckoutInfo(url);
                    }
                  } catch (_) {}
                },
                child: const Text('Gérer'),
              ),
            ],
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: const [
                Icon(Icons.workspace_premium_outlined, color: AppTheme.warning, size: 24),
                SizedBox(width: 8),
                Text('Passer à CartePro Pro',
                    style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15)),
              ],
            ),
            const SizedBox(height: 8),
            const Text(
              '• Photos avant/après\n• CRM complet (contacts, pipeline, tâches)\n• QR premium\n• Statistiques de scan',
              style: TextStyle(color: AppTheme.textSecondary, fontSize: 13, height: 1.6),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: _loadingCheckout ? null : () => _subscribe('monthly'),
                    child: const Text('15 \$/mois'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _loadingCheckout ? null : () => _subscribe('annual'),
                    child: _loadingCheckout
                        ? const SizedBox(
                            width: 16, height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                        : const Text('120 \$/an'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            const Center(
              child: Text('Économisez 60 \$ avec le plan annuel',
                  style: TextStyle(fontSize: 11, color: AppTheme.secondary)),
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  final String label;
  const _SectionTitle({required this.label});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        label.toUpperCase(),
        style: const TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w700,
          color: AppTheme.textSecondary,
          letterSpacing: 1,
        ),
      ),
    );
  }
}

class _SettingTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback? onTap;
  final Widget? trailing;

  const _SettingTile({
    required this.icon,
    required this.label,
    this.onTap,
    this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon, color: AppTheme.primary, size: 22),
        title: Text(label, style: const TextStyle(fontSize: 15)),
        trailing: trailing ?? (onTap != null ? const Icon(Icons.chevron_right) : null),
        onTap: onTap,
      ),
    );
  }
}

class _LogoutButton extends StatefulWidget {
  final WidgetRef ref;
  const _LogoutButton({required this.ref});

  @override
  State<_LogoutButton> createState() => _LogoutButtonState();
}

class _LogoutButtonState extends State<_LogoutButton> {
  bool _loading = false;

  Future<void> _logout() async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Se déconnecter ?'),
        content: const Text('Vous serez redirigé vers la page de connexion.'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Annuler')),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: AppTheme.danger),
            child: const Text('Déconnecter'),
          ),
        ],
      ),
    );
    if (ok != true || !mounted) return;
    setState(() => _loading = true);
    await ApiService.instance.logout();
    if (mounted) GoRouter.of(context).go('/login');
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        onPressed: _loading ? null : _logout,
        icon: _loading
            ? const SizedBox(width: 16, height: 16,
                child: CircularProgressIndicator(strokeWidth: 2))
            : const Icon(Icons.logout, color: AppTheme.danger),
        label: Text('Se déconnecter',
            style: const TextStyle(color: AppTheme.danger)),
        style: OutlinedButton.styleFrom(
          side: const BorderSide(color: AppTheme.danger),
          padding: const EdgeInsets.symmetric(vertical: 14),
        ),
      ),
    );
  }
}
