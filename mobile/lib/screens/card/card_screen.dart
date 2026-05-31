import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../../models/card_model.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';
import '../../config/api_config.dart';

final _cardsProvider = FutureProvider<List<CardModel>>((ref) async {
  final data = await ApiService.instance.listCards();
  final items = data['items'] as List<dynamic>? ?? [];
  return items.map((e) => CardModel.fromJson(e as Map<String, dynamic>)).toList();
});

class CardScreen extends ConsumerWidget {
  const CardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cardsAsync = ref.watch(_cardsProvider);

    return Scaffold(
      backgroundColor: AppTheme.surface,
      appBar: AppBar(
        title: const Text('Ma carte numérique'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit_outlined),
            onPressed: () => context.go('/card/edit'),
          ),
        ],
      ),
      body: cardsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Erreur de chargement'),
              TextButton(
                onPressed: () => ref.invalidate(_cardsProvider),
                child: const Text('Réessayer'),
              ),
            ],
          ),
        ),
        data: (cards) {
          if (cards.isEmpty) return _EmptyCard();
          return _CardView(card: cards.first, ref: ref);
        },
      ),
      floatingActionButton: cardsAsync.valueOrNull?.isEmpty == true
          ? FloatingActionButton.extended(
              onPressed: () => context.go('/card/edit'),
              icon: const Icon(Icons.add),
              label: const Text('Créer ma carte'),
            )
          : null,
    );
  }
}

class _CardView extends StatelessWidget {
  final CardModel card;
  final WidgetRef ref;
  const _CardView({required this.card, required this.ref});

  String get _publicUrl => '${ApiConfig.baseUrl}/public/view/${card.id}';

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: () async => ref.invalidate(_cardsProvider),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _DigitalCardWidget(card: card),
          const SizedBox(height: 20),
          _QrSection(url: _publicUrl, cardId: card.id),
          const SizedBox(height: 20),
          _SocialLinks(card: card),
          if (card.planType == 'none') ...[
            const SizedBox(height: 20),
            _UpgradeBanner(),
          ],
        ],
      ),
    );
  }
}

class _DigitalCardWidget extends StatelessWidget {
  final CardModel card;
  const _DigitalCardWidget({required this.card});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppTheme.primary, Color(0xFF1E40AF)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primary.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 30,
                backgroundColor: Colors.white.withOpacity(0.2),
                child: Text(
                  card.name.isNotEmpty ? card.name[0].toUpperCase() : '?',
                  style: const TextStyle(
                      fontSize: 24, color: Colors.white, fontWeight: FontWeight.w700),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(card.name,
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.w700)),
                    Text(card.title,
                        style: TextStyle(
                            color: Colors.white.withOpacity(0.85), fontSize: 14)),
                    if (card.trade != null)
                      Text(card.trade!,
                          style: TextStyle(
                              color: Colors.white.withOpacity(0.75),
                              fontSize: 12)),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: card.isActive
                      ? AppTheme.secondary
                      : AppTheme.textSecondary,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  card.isActive ? 'Active' : 'Inactive',
                  style: const TextStyle(
                      color: Colors.white,
                      fontSize: 11,
                      fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          const Divider(color: Colors.white24),
          const SizedBox(height: 16),
          if (card.email.isNotEmpty) _InfoRow(Icons.email_outlined, card.email),
          if (card.phone != null) _InfoRow(Icons.phone_outlined, card.phone!),
          if (card.website != null) _InfoRow(Icons.language_outlined, card.website!),
          if (card.serviceZone != null)
            _InfoRow(Icons.location_on_outlined, card.serviceZone!),
          if (card.bio != null) ...[
            const SizedBox(height: 12),
            Text(card.bio!,
                style: TextStyle(
                    color: Colors.white.withOpacity(0.8),
                    fontSize: 13,
                    fontStyle: FontStyle.italic)),
          ],
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String text;
  const _InfoRow(this.icon, this.text);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Icon(icon, color: Colors.white70, size: 16),
          const SizedBox(width: 8),
          Expanded(
            child: Text(text,
                style: const TextStyle(color: Colors.white, fontSize: 14)),
          ),
        ],
      ),
    );
  }
}

class _QrSection extends StatelessWidget {
  final String url;
  final String cardId;
  const _QrSection({required this.url, required this.cardId});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Text(
              'QR Code de votre carte',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                    color: AppTheme.textPrimary,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              'Partagez ce code pour recevoir des contacts',
              style: Theme.of(context)
                  .textTheme
                  .bodySmall
                  ?.copyWith(color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 16),
            QrImageView(
              data: url,
              version: QrVersions.auto,
              size: 180,
              eyeStyle: const QrEyeStyle(
                eyeShape: QrEyeShape.square,
                color: AppTheme.primary,
              ),
              dataModuleStyle: const QrDataModuleStyle(
                dataModuleShape: QrDataModuleShape.square,
                color: AppTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 12),
            TextButton.icon(
              icon: const Icon(Icons.copy),
              label: const Text('Copier le lien'),
              onPressed: () {
                Clipboard.setData(ClipboardData(text: url));
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Lien copié !')),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _SocialLinks extends StatelessWidget {
  final CardModel card;
  const _SocialLinks({required this.card});

  @override
  Widget build(BuildContext context) {
    final links = <(String, String, IconData)>[
      if (card.googleReviewUrl != null)
        ('Google Avis', card.googleReviewUrl!, Icons.star_outline),
      if (card.facebookUrl != null)
        ('Facebook', card.facebookUrl!, Icons.facebook),
      if (card.whatsappNumber != null)
        ('WhatsApp', card.whatsappNumber!, Icons.chat_outlined),
      if (card.instagram != null)
        ('Instagram', card.instagram!, Icons.camera_alt_outlined),
      if (card.linkedin != null)
        ('LinkedIn', card.linkedin!, Icons.work_outline),
    ];

    if (links.isEmpty) return const SizedBox.shrink();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Réseaux & liens',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: AppTheme.textPrimary,
                    )),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: links
                  .map((l) => Chip(
                        avatar: Icon(l.$3, size: 16),
                        label: Text(l.$1,
                            style: const TextStyle(fontSize: 12)),
                      ))
                  .toList(),
            ),
          ],
        ),
      ),
    );
  }
}

class _UpgradeBanner extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFFFF7ED), Color(0xFFFFF3CD)],
        ),
        border: Border.all(color: AppTheme.warning.withOpacity(0.5)),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          const Icon(Icons.workspace_premium, color: AppTheme.warning, size: 28),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                Text('Passez à CartePro Pro',
                    style: TextStyle(fontWeight: FontWeight.w700, fontSize: 15)),
                SizedBox(height: 2),
                Text('15 \$/mois — Photos avant/après, CRM complet, QR premium',
                    style: TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
              ],
            ),
          ),
          const SizedBox(width: 8),
          TextButton(
            onPressed: () => context.go('/settings'),
            style: TextButton.styleFrom(
              backgroundColor: AppTheme.warning,
              foregroundColor: Colors.white,
              padding:
                  const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('Voir', style: TextStyle(fontSize: 12)),
          ),
        ],
      ),
    );
  }
}

class _EmptyCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.badge_outlined, size: 64, color: AppTheme.textSecondary),
            const SizedBox(height: 16),
            const Text(
              'Aucune carte numérique',
              style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.textPrimary),
            ),
            const SizedBox(height: 8),
            const Text(
              'Créez votre carte pour commencer à partager vos coordonnées',
              textAlign: TextAlign.center,
              style: TextStyle(color: AppTheme.textSecondary),
            ),
          ],
        ),
      ),
    );
  }
}
