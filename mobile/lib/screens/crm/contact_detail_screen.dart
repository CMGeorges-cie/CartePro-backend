import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../models/contact.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

class ContactDetailScreen extends ConsumerStatefulWidget {
  final int contactId;
  const ContactDetailScreen({super.key, required this.contactId});

  @override
  ConsumerState<ContactDetailScreen> createState() => _ContactDetailScreenState();
}

class _ContactDetailScreenState extends ConsumerState<ContactDetailScreen> {
  Contact? _contact;
  List<Map<String, dynamic>> _notes = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final data = await ApiService.instance.getContact(widget.contactId);
      final notesData = await ApiService.instance.getNotes(widget.contactId);
      setState(() {
        _contact = Contact.fromJson(data['contact'] as Map<String, dynamic>? ?? data);
        _notes = (notesData as List<dynamic>)
            .map((e) => e as Map<String, dynamic>)
            .toList();
        _loading = false;
      });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  Future<void> _updateStage(String newStage) async {
    try {
      await ApiService.instance.updateContactStage(widget.contactId, newStage);
      _load();
    } catch (_) {}
  }

  Future<void> _deleteContact() async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Supprimer le contact ?'),
        content: const Text('Cette action est irréversible.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Annuler')),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: AppTheme.danger),
            child: const Text('Supprimer'),
          ),
        ],
      ),
    );
    if (ok == true) {
      await ApiService.instance.deleteContact(widget.contactId);
      if (mounted) context.go('/crm/contacts');
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Scaffold(body: Center(child: CircularProgressIndicator()));

    final c = _contact;
    if (c == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Contact')),
        body: const Center(child: Text('Contact introuvable')),
      );
    }

    return Scaffold(
      backgroundColor: AppTheme.surface,
      appBar: AppBar(
        title: Text(c.fullName),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/crm/contacts'),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline),
            color: AppTheme.danger,
            onPressed: _deleteContact,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _ContactHeader(contact: c),
            const SizedBox(height: 16),
            _StageSelector(current: c.pipelineStage, onSelect: _updateStage),
            const SizedBox(height: 16),
            _ContactInfo(contact: c),
            const SizedBox(height: 16),
            _NotesSection(
              contactId: widget.contactId,
              notes: _notes,
              onChanged: _load,
            ),
            const SizedBox(height: 16),
            _TasksForContact(contactId: widget.contactId),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
}

class _ContactHeader extends StatelessWidget {
  final Contact contact;
  const _ContactHeader({required this.contact});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        CircleAvatar(
          radius: 36,
          backgroundColor: AppTheme.primary.withOpacity(0.1),
          child: Text(
            contact.firstName[0].toUpperCase(),
            style: const TextStyle(
                fontSize: 28, color: AppTheme.primary, fontWeight: FontWeight.w700),
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(contact.fullName,
                  style: const TextStyle(
                      fontSize: 20, fontWeight: FontWeight.w700, color: AppTheme.textPrimary)),
              if (contact.company != null)
                Text(contact.company!,
                    style: const TextStyle(color: AppTheme.textSecondary, fontSize: 14)),
              if (contact.city != null)
                Text(contact.city!,
                    style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
            ],
          ),
        ),
      ],
    );
  }
}

class _StageSelector extends StatelessWidget {
  final String current;
  final void Function(String) onSelect;

  const _StageSelector({required this.current, required this.onSelect});

  static const _stages = [
    ('new', 'Nouveau'),
    ('contacted', 'Contacté'),
    ('quote_sent', 'Soumission'),
    ('won', 'Gagné'),
    ('lost', 'Perdu'),
  ];

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Étape du pipeline',
                style: TextStyle(fontWeight: FontWeight.w700, color: AppTheme.textPrimary)),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _stages.map((s) {
                final isCurrent = s.$1 == current;
                final color = AppTheme.pipelineColors[s.$1] ?? AppTheme.textSecondary;
                return GestureDetector(
                  onTap: () => onSelect(s.$1),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 150),
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                    decoration: BoxDecoration(
                      color: isCurrent ? color : Colors.white,
                      border: Border.all(color: isCurrent ? color : const Color(0xFFE5E7EB)),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      s.$2,
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: isCurrent ? Colors.white : AppTheme.textSecondary,
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
}

class _ContactInfo extends StatelessWidget {
  final Contact contact;
  const _ContactInfo({required this.contact});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Informations',
                style: TextStyle(fontWeight: FontWeight.w700, color: AppTheme.textPrimary)),
            const SizedBox(height: 12),
            if (contact.email != null) _Row(Icons.email_outlined, contact.email!),
            if (contact.phone != null) _Row(Icons.phone_outlined, contact.phone!),
            if (contact.source != null) _Row(Icons.source_outlined, 'Source: ${contact.source}'),
            _Row(Icons.calendar_today_outlined,
                'Ajouté le ${_formatDate(contact.createdAt)}'),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime d) =>
      '${d.day.toString().padLeft(2, '0')}/${d.month.toString().padLeft(2, '0')}/${d.year}';
}

class _Row extends StatelessWidget {
  final IconData icon;
  final String text;
  const _Row(this.icon, this.text);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Icon(icon, size: 16, color: AppTheme.textSecondary),
          const SizedBox(width: 10),
          Expanded(child: Text(text, style: const TextStyle(fontSize: 14))),
        ],
      ),
    );
  }
}

class _NotesSection extends StatefulWidget {
  final int contactId;
  final List<Map<String, dynamic>> notes;
  final VoidCallback onChanged;

  const _NotesSection({
    required this.contactId,
    required this.notes,
    required this.onChanged,
  });

  @override
  State<_NotesSection> createState() => _NotesSectionState();
}

class _NotesSectionState extends State<_NotesSection> {
  final _noteCtrl = TextEditingController();
  bool _saving = false;

  @override
  void dispose() {
    _noteCtrl.dispose();
    super.dispose();
  }

  Future<void> _addNote() async {
    if (_noteCtrl.text.trim().isEmpty) return;
    setState(() => _saving = true);
    try {
      await ApiService.instance.addNote(widget.contactId, _noteCtrl.text.trim());
      _noteCtrl.clear();
      widget.onChanged();
    } catch (_) {} finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _deleteNote(int noteId) async {
    await ApiService.instance.deleteNote(noteId);
    widget.onChanged();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text('Notes',
                    style: TextStyle(fontWeight: FontWeight.w700, color: AppTheme.textPrimary)),
                const Spacer(),
                Text('${widget.notes.length}',
                    style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
              ],
            ),
            const SizedBox(height: 12),
            ...widget.notes.map((n) => _NoteItem(note: n, onDelete: () => _deleteNote(n['id']))),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _noteCtrl,
                    decoration: const InputDecoration(
                      hintText: 'Ajouter une note…',
                      isDense: true,
                    ),
                    maxLines: 2,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  onPressed: _saving ? null : _addNote,
                  icon: _saving
                      ? const SizedBox(
                          width: 16, height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.send),
                  style: IconButton.styleFrom(backgroundColor: AppTheme.primary),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _NoteItem extends StatelessWidget {
  final Map<String, dynamic> note;
  final VoidCallback onDelete;

  const _NoteItem({required this.note, required this.onDelete});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFF9FAFB),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFE5E7EB)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Text(note['content'] as String? ?? '',
                style: const TextStyle(fontSize: 13)),
          ),
          GestureDetector(
            onTap: onDelete,
            child: const Icon(Icons.close, size: 16, color: AppTheme.textSecondary),
          ),
        ],
      ),
    );
  }
}

class _TasksForContact extends StatefulWidget {
  final int contactId;
  const _TasksForContact({required this.contactId});

  @override
  State<_TasksForContact> createState() => _TasksForContactState();
}

class _TasksForContactState extends State<_TasksForContact> {
  List<Map<String, dynamic>> _tasks = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await ApiService.instance.listTasks(contactId: widget.contactId);
      setState(() {
        _tasks = (data['items'] as List<dynamic>? ?? [])
            .map((e) => e as Map<String, dynamic>)
            .toList();
        _loading = false;
      });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Tâches liées',
                style: TextStyle(fontWeight: FontWeight.w700, color: AppTheme.textPrimary)),
            const SizedBox(height: 12),
            if (_loading)
              const Center(child: CircularProgressIndicator())
            else if (_tasks.isEmpty)
              const Text('Aucune tâche liée à ce contact.',
                  style: TextStyle(color: AppTheme.textSecondary, fontSize: 13))
            else
              ..._tasks.map((t) => _SimpleTaskRow(task: t, onToggle: () async {
                await ApiService.instance.toggleTask(t['id']);
                _load();
              })),
          ],
        ),
      ),
    );
  }
}

class _SimpleTaskRow extends StatelessWidget {
  final Map<String, dynamic> task;
  final VoidCallback onToggle;

  const _SimpleTaskRow({required this.task, required this.onToggle});

  @override
  Widget build(BuildContext context) {
    final isDone = task['is_done'] as bool? ?? false;
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        children: [
          Checkbox(value: isDone, onChanged: (_) => onToggle(), activeColor: AppTheme.secondary),
          Expanded(
            child: Text(
              task['title'] as String? ?? '',
              style: TextStyle(
                  decoration: isDone ? TextDecoration.lineThrough : null,
                  color: isDone ? AppTheme.textSecondary : AppTheme.textPrimary,
                  fontSize: 14),
            ),
          ),
        ],
      ),
    );
  }
}
