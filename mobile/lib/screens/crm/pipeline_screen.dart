import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../models/contact.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

final _pipelineProvider = FutureProvider<Map<String, List<Contact>>>((ref) async {
  final data = await ApiService.instance.getPipeline();
  return {
    for (final stage in Contact.stageLabels.keys)
      stage: ((data[stage] as List<dynamic>?) ?? [])
          .map((e) => Contact.fromJson(e as Map<String, dynamic>))
          .toList(),
  };
});

class PipelineScreen extends ConsumerWidget {
  const PipelineScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pipeAsync = ref.watch(_pipelineProvider);

    return Scaffold(
      backgroundColor: AppTheme.surface,
      appBar: AppBar(
        title: const Text('Pipeline de vente'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(_pipelineProvider),
          ),
        ],
      ),
      body: pipeAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Erreur de chargement'),
              TextButton(
                onPressed: () => ref.invalidate(_pipelineProvider),
                child: const Text('Réessayer'),
              ),
            ],
          ),
        ),
        data: (pipeline) => RefreshIndicator(
          onRefresh: () async => ref.invalidate(_pipelineProvider),
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.all(12),
            children: Contact.stageLabels.entries.map((entry) {
              final contacts = pipeline[entry.key] ?? [];
              return _KanbanColumn(
                stage: entry.key,
                label: entry.value,
                contacts: contacts,
                color: AppTheme.pipelineColors[entry.key] ?? AppTheme.textSecondary,
                onContactMoved: (contactId, newStage) async {
                  await ApiService.instance.updateContactStage(contactId, newStage);
                  ref.invalidate(_pipelineProvider);
                },
                onContactTapped: (id) => context.push('/crm/contacts/$id'),
              );
            }).toList(),
          ),
        ),
      ),
    );
  }
}

class _KanbanColumn extends StatelessWidget {
  final String stage;
  final String label;
  final List<Contact> contacts;
  final Color color;
  final Future<void> Function(int contactId, String newStage) onContactMoved;
  final void Function(int id) onContactTapped;

  const _KanbanColumn({
    required this.stage,
    required this.label,
    required this.contacts,
    required this.color,
    required this.onContactMoved,
    required this.onContactTapped,
  });

  @override
  Widget build(BuildContext context) {
    return DragTarget<_DragData>(
      onWillAcceptWithDetails: (details) => details.data.fromStage != stage,
      onAcceptWithDetails: (details) =>
          onContactMoved(details.data.contactId, stage),
      builder: (context, candidateData, _) {
        final isOver = candidateData.isNotEmpty;
        return Container(
          width: 220,
          margin: const EdgeInsets.only(right: 12),
          decoration: BoxDecoration(
            color: isOver ? color.withOpacity(0.08) : Colors.white,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
                color: isOver ? color : const Color(0xFFE5E7EB), width: isOver ? 2 : 1),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.12),
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(13)),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 10, height: 10,
                      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(label,
                          style: TextStyle(
                              fontWeight: FontWeight.w700,
                              color: color,
                              fontSize: 14)),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: color.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text('${contacts.length}',
                          style: TextStyle(
                              fontSize: 12, fontWeight: FontWeight.w700, color: color)),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: contacts.isEmpty
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Text(
                            'Glissez un contact ici',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                                color: AppTheme.textSecondary.withOpacity(0.6),
                                fontSize: 13),
                          ),
                        ),
                      )
                    : ListView.separated(
                        padding: const EdgeInsets.all(10),
                        itemCount: contacts.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 8),
                        itemBuilder: (context, i) => _DraggableContactCard(
                          contact: contacts[i],
                          stage: stage,
                          onTap: () => onContactTapped(contacts[i].id),
                        ),
                      ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _DragData {
  final int contactId;
  final String fromStage;
  const _DragData({required this.contactId, required this.fromStage});
}

class _DraggableContactCard extends StatelessWidget {
  final Contact contact;
  final String stage;
  final VoidCallback onTap;

  const _DraggableContactCard({
    required this.contact,
    required this.stage,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Draggable<_DragData>(
      data: _DragData(contactId: contact.id, fromStage: stage),
      feedback: Material(
        elevation: 6,
        borderRadius: BorderRadius.circular(10),
        child: SizedBox(
          width: 200,
          child: _ContactCardContent(contact: contact),
        ),
      ),
      childWhenDragging: Opacity(
        opacity: 0.4,
        child: _ContactCardContent(contact: contact),
      ),
      child: GestureDetector(
        onTap: onTap,
        child: _ContactCardContent(contact: contact),
      ),
    );
  }
}

class _ContactCardContent extends StatelessWidget {
  final Contact contact;
  const _ContactCardContent({required this.contact});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFE5E7EB)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 14,
                backgroundColor: AppTheme.primary.withOpacity(0.1),
                child: Text(
                  contact.firstName[0].toUpperCase(),
                  style: const TextStyle(
                      fontSize: 12,
                      color: AppTheme.primary,
                      fontWeight: FontWeight.w700),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(contact.fullName,
                    style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                        color: AppTheme.textPrimary),
                    overflow: TextOverflow.ellipsis),
              ),
            ],
          ),
          if (contact.company != null) ...[
            const SizedBox(height: 6),
            Text(contact.company!,
                style: const TextStyle(
                    fontSize: 11, color: AppTheme.textSecondary),
                overflow: TextOverflow.ellipsis),
          ],
          if (contact.phone != null) ...[
            const SizedBox(height: 4),
            Row(
              children: [
                const Icon(Icons.phone, size: 11, color: AppTheme.textSecondary),
                const SizedBox(width: 4),
                Text(contact.phone!,
                    style: const TextStyle(
                        fontSize: 11, color: AppTheme.textSecondary)),
              ],
            ),
          ],
          if (contact.city != null) ...[
            const SizedBox(height: 4),
            Row(
              children: [
                const Icon(Icons.location_on_outlined,
                    size: 11, color: AppTheme.textSecondary),
                const SizedBox(width: 4),
                Text(contact.city!,
                    style: const TextStyle(
                        fontSize: 11, color: AppTheme.textSecondary)),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
