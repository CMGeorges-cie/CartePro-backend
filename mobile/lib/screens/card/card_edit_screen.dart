import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../models/card_model.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

final _editCardProvider = FutureProvider<CardModel?>((ref) async {
  final data = await ApiService.instance.listCards();
  final items = data['items'] as List<dynamic>? ?? [];
  if (items.isEmpty) return null;
  return CardModel.fromJson(items.first as Map<String, dynamic>);
});

class CardEditScreen extends ConsumerStatefulWidget {
  const CardEditScreen({super.key});

  @override
  ConsumerState<CardEditScreen> createState() => _CardEditScreenState();
}

class _CardEditScreenState extends ConsumerState<CardEditScreen> {
  final _formKey = GlobalKey<FormState>();
  bool _loading = false;
  bool _initialized = false;
  String? _cardId;

  final _name = TextEditingController();
  final _title = TextEditingController();
  final _email = TextEditingController();
  final _phone = TextEditingController();
  final _website = TextEditingController();
  final _trade = TextEditingController();
  final _serviceZone = TextEditingController();
  final _bio = TextEditingController();
  final _googleReview = TextEditingController();
  final _facebook = TextEditingController();
  final _whatsapp = TextEditingController();
  final _instagram = TextEditingController();
  final _linkedin = TextEditingController();

  @override
  void dispose() {
    for (final c in [_name, _title, _email, _phone, _website, _trade,
        _serviceZone, _bio, _googleReview, _facebook, _whatsapp, _instagram, _linkedin]) {
      c.dispose();
    }
    super.dispose();
  }

  void _populate(CardModel card) {
    if (_initialized) return;
    _initialized = true;
    _cardId = card.id;
    _name.text = card.name;
    _title.text = card.title;
    _email.text = card.email;
    _phone.text = card.phone ?? '';
    _website.text = card.website ?? '';
    _trade.text = card.trade ?? '';
    _serviceZone.text = card.serviceZone ?? '';
    _bio.text = card.bio ?? '';
    _googleReview.text = card.googleReviewUrl ?? '';
    _facebook.text = card.facebookUrl ?? '';
    _whatsapp.text = card.whatsappNumber ?? '';
    _instagram.text = card.instagram ?? '';
    _linkedin.text = card.linkedin ?? '';
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      final data = {
        'name': _name.text.trim(),
        'title': _title.text.trim(),
        'email': _email.text.trim(),
        if (_phone.text.isNotEmpty) 'phone': _phone.text.trim(),
        if (_website.text.isNotEmpty) 'website': _website.text.trim(),
        if (_trade.text.isNotEmpty) 'trade': _trade.text.trim(),
        if (_serviceZone.text.isNotEmpty) 'service_zone': _serviceZone.text.trim(),
        if (_bio.text.isNotEmpty) 'bio': _bio.text.trim(),
        if (_googleReview.text.isNotEmpty) 'google_review_url': _googleReview.text.trim(),
        if (_facebook.text.isNotEmpty) 'facebook_url': _facebook.text.trim(),
        if (_whatsapp.text.isNotEmpty) 'whatsapp_number': _whatsapp.text.trim(),
        if (_instagram.text.isNotEmpty) 'instagram': _instagram.text.trim(),
        if (_linkedin.text.isNotEmpty) 'linkedin': _linkedin.text.trim(),
      };
      if (_cardId != null) {
        await ApiService.instance.updateCard(_cardId!, data);
      } else {
        await ApiService.instance.createCard(data);
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Carte sauvegardée !')),
        );
        ref.invalidate(_editCardProvider);
        context.go('/card');
      }
    } on DioException catch (e) {
      final msg = e.response?.data?['message'] as String? ?? 'Erreur de sauvegarde.';
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(msg)));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final cardAsync = ref.watch(_editCardProvider);

    return Scaffold(
      backgroundColor: AppTheme.surface,
      appBar: AppBar(
        title: const Text('Modifier ma carte'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/card'),
        ),
        actions: [
          TextButton(
            onPressed: _loading ? null : _save,
            child: _loading
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2))
                : const Text('Sauvegarder',
                    style: TextStyle(fontWeight: FontWeight.w700)),
          ),
        ],
      ),
      body: cardAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => const Center(child: Text('Erreur de chargement')),
        data: (card) {
          if (card != null) _populate(card);
          return Form(
            key: _formKey,
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _Section(label: 'Informations de base'),
                _Field(ctrl: _name, label: 'Nom complet *', icon: Icons.person_outline,
                    validator: (v) => v == null || v.isEmpty ? 'Requis' : null),
                _Field(ctrl: _title, label: 'Titre / Poste *', icon: Icons.work_outline,
                    validator: (v) => v == null || v.isEmpty ? 'Requis' : null),
                _Field(ctrl: _email, label: 'Courriel *', icon: Icons.email_outlined,
                    type: TextInputType.emailAddress,
                    validator: (v) => v == null || v.isEmpty ? 'Requis' : null),
                _Field(ctrl: _trade, label: 'Métier (ex: Peintre, Électricien)', icon: Icons.construction),
                _Section(label: 'Coordonnées'),
                _Field(ctrl: _phone, label: 'Téléphone', icon: Icons.phone_outlined,
                    type: TextInputType.phone),
                _Field(ctrl: _website, label: 'Site web', icon: Icons.language_outlined,
                    type: TextInputType.url),
                _Field(ctrl: _serviceZone, label: 'Zone de service', icon: Icons.location_on_outlined),
                _Section(label: 'Présentation'),
                _Field(ctrl: _bio, label: 'Bio / Description', icon: Icons.notes, maxLines: 3),
                _Section(label: 'Réseaux & avis'),
                _Field(ctrl: _googleReview, label: 'Lien Google Avis', icon: Icons.star_outline, type: TextInputType.url),
                _Field(ctrl: _facebook, label: 'Page Facebook', icon: Icons.facebook, type: TextInputType.url),
                _Field(ctrl: _whatsapp, label: 'Numéro WhatsApp', icon: Icons.chat_outlined, type: TextInputType.phone),
                _Field(ctrl: _instagram, label: 'Instagram (@...)', icon: Icons.camera_alt_outlined),
                _Field(ctrl: _linkedin, label: 'LinkedIn (URL)', icon: Icons.work_history_outlined, type: TextInputType.url),
                const SizedBox(height: 24),
                SizedBox(
                  height: 50,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _save,
                    child: const Text('Sauvegarder la carte'),
                  ),
                ),
                const SizedBox(height: 32),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _Section extends StatelessWidget {
  final String label;
  const _Section({required this.label});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 20, bottom: 8),
      child: Text(
        label,
        style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w700,
            color: AppTheme.primary,
            letterSpacing: 0.5),
      ),
    );
  }
}

class _Field extends StatelessWidget {
  final TextEditingController ctrl;
  final String label;
  final IconData icon;
  final TextInputType? type;
  final int maxLines;
  final String? Function(String?)? validator;

  const _Field({
    required this.ctrl,
    required this.label,
    required this.icon,
    this.type,
    this.maxLines = 1,
    this.validator,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextFormField(
        controller: ctrl,
        keyboardType: type,
        maxLines: maxLines,
        validator: validator,
        decoration: InputDecoration(
          labelText: label,
          prefixIcon: Icon(icon),
        ),
      ),
    );
  }
}
