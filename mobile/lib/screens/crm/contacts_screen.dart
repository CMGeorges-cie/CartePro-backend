import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../models/contact.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

class ContactsScreen extends ConsumerStatefulWidget {
  const ContactsScreen({super.key});

  @override
  ConsumerState<ContactsScreen> createState() => _ContactsScreenState();
}

class _ContactsScreenState extends ConsumerState<ContactsScreen> {
  List<Contact> _contacts = [];
  bool _loading = true;
  String? _error;
  String _search = '';
  String? _stageFilter;
  int _page = 1;
  bool _hasMore = true;
  final _searchCtrl = TextEditingController();

  static const _stages = [
    ('new', 'Nouveau'),
    ('contacted', 'Contacté'),
    ('quote_sent', 'Soumission'),
    ('won', 'Gagné'),
    ('lost', 'Perdu'),
  ];

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  Future<void> _load({bool reset = false}) async {
    if (reset) {
      setState(() { _contacts = []; _page = 1; _hasMore = true; });
    }
    if (!_hasMore) return;
    setState(() { _loading = true; _error = null; });
    try {
      final data = await ApiService.instance.listContacts(
        page: _page,
        stage: _stageFilter,
        search: _search.isNotEmpty ? _search : null,
      );
      final items = (data['items'] as List<dynamic>? ?? [])
          .map((e) => Contact.fromJson(e as Map<String, dynamic>))
          .toList();
      setState(() {
        _contacts = reset ? items : [..._contacts, ...items];
        _hasMore = items.length >= 20;
        _loading = false;
      });
    } on DioException {
      setState(() { _error = 'Erreur de chargement'; _loading = false; });
    }
  }

  void _applySearch() {
    _search = _searchCtrl.text.trim();
    _load(reset: true);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surface,
      appBar: AppBar(
        title: const Text('Contacts CRM'),
        actions: [
          IconButton(
            icon: const Icon(Icons.upload_outlined),
            tooltip: 'Importer CSV',
            onPressed: _showImportInfo,
          ),
        ],
      ),
      body: Column(
        children: [
          _SearchBar(
            ctrl: _searchCtrl,
            onSubmit: _applySearch,
            onClear: () {
              _searchCtrl.clear();
              _search = '';
              _load(reset: true);
            },
          ),
          _StageFilterRow(
            selected: _stageFilter,
            stages: _stages,
            onSelect: (s) {
              setState(() => _stageFilter = s);
              _load(reset: true);
            },
          ),
          Expanded(
            child: _error != null
                ? Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(_error!),
                        TextButton(
                          onPressed: () => _load(reset: true),
                          child: const Text('Réessayer'),
                        ),
                      ],
                    ),
                  )
                : _contacts.isEmpty && !_loading
                    ? _EmptyState(onAdd: _showAddContact)
                    : NotificationListener<ScrollNotification>(
                        onNotification: (n) {
                          if (n is ScrollEndNotification &&
                              n.metrics.pixels >=
                                  n.metrics.maxScrollExtent - 200) {
                            if (!_loading && _hasMore) {
                              _page++;
                              _load();
                            }
                          }
                          return false;
                        },
                        child: RefreshIndicator(
                          onRefresh: () => _load(reset: true),
                          child: ListView.separated(
                            padding: const EdgeInsets.all(12),
                            itemCount:
                                _contacts.length + (_loading ? 1 : 0),
                            separatorBuilder: (_, __) =>
                                const SizedBox(height: 8),
                            itemBuilder: (context, i) {
                              if (i == _contacts.length) {
                                return const Center(
                                  child: Padding(
                                    padding: EdgeInsets.all(16),
                                    child: CircularProgressIndicator(),
                                  ),
                                );
                              }
                              return _ContactTile(
                                contact: _contacts[i],
                                onTap: () async {
                                  await context.push('/crm/contacts/${_contacts[i].id}');
                                  _load(reset: true);
                                },
                              );
                            },
                          ),
                        ),
                      ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showAddContact,
        child: const Icon(Icons.person_add),
      ),
    );
  }

  void _showImportInfo() {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Importer des contacts'),
        content: const Text(
          'Importez un fichier CSV avec les colonnes :\n\n'
          'prénom, nom, courriel, téléphone, entreprise, ville\n\n'
          'Les colonnes anglaises (first_name, email, phone...) sont aussi acceptées.',
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('OK')),
        ],
      ),
    );
  }

  void _showAddContact() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => _AddContactSheet(
        onSaved: () {
          Navigator.pop(context);
          _load(reset: true);
        },
      ),
    );
  }
}

class _SearchBar extends StatelessWidget {
  final TextEditingController ctrl;
  final VoidCallback onSubmit;
  final VoidCallback onClear;

  const _SearchBar({
    required this.ctrl,
    required this.onSubmit,
    required this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 12, 12, 4),
      child: TextField(
        controller: ctrl,
        decoration: InputDecoration(
          hintText: 'Rechercher un contact…',
          prefixIcon: const Icon(Icons.search, size: 20),
          suffixIcon: ctrl.text.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear, size: 18),
                  onPressed: onClear,
                )
              : null,
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          isDense: true,
        ),
        textInputAction: TextInputAction.search,
        onSubmitted: (_) => onSubmit(),
      ),
    );
  }
}

class _StageFilterRow extends StatelessWidget {
  final String? selected;
  final List<(String, String)> stages;
  final void Function(String?) onSelect;

  const _StageFilterRow({
    required this.selected,
    required this.stages,
    required this.onSelect,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 44,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        children: [
          _Chip(label: 'Tous', selected: selected == null, onTap: () => onSelect(null)),
          ...stages.map((s) => _Chip(
                label: s.$2,
                selected: selected == s.$1,
                onTap: () => onSelect(s.$1 == selected ? null : s.$1),
                color: AppTheme.pipelineColors[s.$1],
              )),
        ],
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;
  final Color? color;

  const _Chip({
    required this.label,
    required this.selected,
    required this.onTap,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final c = color ?? AppTheme.primary;
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
          decoration: BoxDecoration(
            color: selected ? c : Colors.white,
            border: Border.all(color: selected ? c : const Color(0xFFE5E7EB)),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: selected ? Colors.white : AppTheme.textSecondary,
            ),
          ),
        ),
      ),
    );
  }
}

class _ContactTile extends StatelessWidget {
  final Contact contact;
  final VoidCallback onTap;

  const _ContactTile({required this.contact, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final stageColor = AppTheme.pipelineColors[contact.pipelineStage] ??
        AppTheme.textSecondary;

    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: CircleAvatar(
          backgroundColor: AppTheme.primary.withOpacity(0.1),
          child: Text(
            contact.firstName.isNotEmpty
                ? contact.firstName[0].toUpperCase()
                : '?',
            style: const TextStyle(
                color: AppTheme.primary, fontWeight: FontWeight.w700),
          ),
        ),
        title: Text(contact.fullName,
            style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (contact.company != null)
              Text(contact.company!,
                  style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
            if (contact.phone != null)
              Text(contact.phone!,
                  style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
          ],
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: stageColor.withOpacity(0.12),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                contact.stageFr,
                style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: stageColor),
              ),
            ),
          ],
        ),
        onTap: onTap,
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  final VoidCallback onAdd;
  const _EmptyState({required this.onAdd});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.people_outline, size: 64, color: AppTheme.textSecondary),
          const SizedBox(height: 16),
          const Text('Aucun contact',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          const Text('Ajoutez votre premier contact CRM',
              style: TextStyle(color: AppTheme.textSecondary)),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: onAdd,
            icon: const Icon(Icons.person_add),
            label: const Text('Ajouter un contact'),
          ),
        ],
      ),
    );
  }
}

class _AddContactSheet extends StatefulWidget {
  final VoidCallback onSaved;
  const _AddContactSheet({required this.onSaved});

  @override
  State<_AddContactSheet> createState() => _AddContactSheetState();
}

class _AddContactSheetState extends State<_AddContactSheet> {
  final _formKey = GlobalKey<FormState>();
  final _first = TextEditingController();
  final _last = TextEditingController();
  final _email = TextEditingController();
  final _phone = TextEditingController();
  final _company = TextEditingController();
  final _city = TextEditingController();
  bool _loading = false;

  @override
  void dispose() {
    for (final c in [_first, _last, _email, _phone, _company, _city]) c.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      await ApiService.instance.createContact({
        'first_name': _first.text.trim(),
        if (_last.text.isNotEmpty) 'last_name': _last.text.trim(),
        if (_email.text.isNotEmpty) 'email': _email.text.trim(),
        if (_phone.text.isNotEmpty) 'phone': _phone.text.trim(),
        if (_company.text.isNotEmpty) 'company': _company.text.trim(),
        if (_city.text.isNotEmpty) 'city': _city.text.trim(),
      });
      widget.onSaved();
    } on DioException catch (e) {
      final msg = e.response?.data?['message'] as String? ?? 'Erreur';
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 20, right: 20, top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      child: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('Nouveau contact',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
            const SizedBox(height: 16),
            Row(children: [
              Expanded(child: TextFormField(
                controller: _first,
                decoration: const InputDecoration(labelText: 'Prénom *'),
                validator: (v) => v == null || v.isEmpty ? 'Requis' : null,
              )),
              const SizedBox(width: 12),
              Expanded(child: TextFormField(
                controller: _last,
                decoration: const InputDecoration(labelText: 'Nom'),
              )),
            ]),
            const SizedBox(height: 12),
            TextFormField(
              controller: _email,
              decoration: const InputDecoration(labelText: 'Courriel'),
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _phone,
              decoration: const InputDecoration(labelText: 'Téléphone'),
              keyboardType: TextInputType.phone,
            ),
            const SizedBox(height: 12),
            Row(children: [
              Expanded(child: TextFormField(
                controller: _company,
                decoration: const InputDecoration(labelText: 'Entreprise'),
              )),
              const SizedBox(width: 12),
              Expanded(child: TextFormField(
                controller: _city,
                decoration: const InputDecoration(labelText: 'Ville'),
              )),
            ]),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _loading ? null : _save,
              child: _loading
                  ? const SizedBox(
                      width: 18, height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Text('Ajouter le contact'),
            ),
          ],
        ),
      ),
    );
  }
}
