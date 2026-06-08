import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/task.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

class TasksScreen extends ConsumerStatefulWidget {
  const TasksScreen({super.key});

  @override
  ConsumerState<TasksScreen> createState() => _TasksScreenState();
}

class _TasksScreenState extends ConsumerState<TasksScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabs;
  List<Task> _tasks = [];
  bool _loading = true;
  String? _filter; // null=all, 'today', 'overdue', 'done'

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 4, vsync: this);
    _tabs.addListener(() {
      switch (_tabs.index) {
        case 0: _filter = null;
        case 1: _filter = 'today';
        case 2: _filter = 'overdue';
        case 3: _filter = 'done';
      }
      _load();
    });
    _load();
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      Map<String, dynamic> data;
      if (_filter == 'today') {
        data = await ApiService.instance.listTasks(dueToday: true);
      } else if (_filter == 'done') {
        data = await ApiService.instance.listTasks(done: true);
      } else {
        data = await ApiService.instance.listTasks();
      }

      final items = (data['items'] as List<dynamic>? ?? [])
          .map((e) => Task.fromJson(e as Map<String, dynamic>))
          .toList();

      // Client-side filter for overdue
      final filtered = _filter == 'overdue'
          ? items.where((t) => t.isOverdue).toList()
          : _filter == null
              ? items.where((t) => !t.isDone).toList()
              : items;

      setState(() { _tasks = filtered; _loading = false; });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  Future<void> _toggleTask(int taskId) async {
    await ApiService.instance.toggleTask(taskId);
    _load();
  }

  Future<void> _deleteTask(int taskId) async {
    await ApiService.instance.deleteTask(taskId);
    _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surface,
      appBar: AppBar(
        title: const Text('Tâches'),
        bottom: TabBar(
          controller: _tabs,
          isScrollable: true,
          tabAlignment: TabAlignment.start,
          tabs: const [
            Tab(text: 'À faire'),
            Tab(text: "Aujourd'hui"),
            Tab(text: 'En retard'),
            Tab(text: 'Terminées'),
          ],
        ),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _tasks.isEmpty
              ? _EmptyTasks(filter: _filter, onAdd: _showAddTask)
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.separated(
                    padding: const EdgeInsets.all(12),
                    itemCount: _tasks.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 8),
                    itemBuilder: (context, i) => _TaskTile(
                      task: _tasks[i],
                      onToggle: () => _toggleTask(_tasks[i].id),
                      onDelete: () => _deleteTask(_tasks[i].id),
                    ),
                  ),
                ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showAddTask,
        child: const Icon(Icons.add_task),
      ),
    );
  }

  void _showAddTask() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => _AddTaskSheet(
        onSaved: () {
          Navigator.pop(context);
          _load();
        },
      ),
    );
  }
}

class _TaskTile extends StatelessWidget {
  final Task task;
  final VoidCallback onToggle;
  final VoidCallback onDelete;

  const _TaskTile({
    required this.task,
    required this.onToggle,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final priorityColor = AppTheme.priorityColors[task.priority] ?? AppTheme.textSecondary;
    final overdue = task.isOverdue;

    return Dismissible(
      key: ValueKey(task.id),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        decoration: BoxDecoration(
          color: AppTheme.danger.withOpacity(0.8),
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Icon(Icons.delete_outline, color: Colors.white),
      ),
      confirmDismiss: (_) => showDialog<bool>(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text('Supprimer la tâche ?'),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Annuler')),
            TextButton(
              onPressed: () => Navigator.pop(context, true),
              style: TextButton.styleFrom(foregroundColor: AppTheme.danger),
              child: const Text('Supprimer'),
            ),
          ],
        ),
      ),
      onDismissed: (_) => onDelete(),
      child: Card(
        child: ListTile(
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          leading: Checkbox(
            value: task.isDone,
            onChanged: (_) => onToggle(),
            activeColor: AppTheme.secondary,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
          ),
          title: Text(
            task.title,
            style: TextStyle(
              fontWeight: FontWeight.w600,
              color: task.isDone ? AppTheme.textSecondary : AppTheme.textPrimary,
              decoration: task.isDone ? TextDecoration.lineThrough : null,
            ),
          ),
          subtitle: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (task.description != null)
                Text(task.description!,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
              const SizedBox(height: 4),
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: priorityColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      _priorityLabel(task.priority),
                      style: TextStyle(
                          fontSize: 10, fontWeight: FontWeight.w700, color: priorityColor),
                    ),
                  ),
                  if (task.dueDate != null) ...[
                    const SizedBox(width: 8),
                    Icon(
                      Icons.calendar_today_outlined,
                      size: 12,
                      color: overdue ? AppTheme.danger : AppTheme.textSecondary,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      _formatDate(task.dueDate!),
                      style: TextStyle(
                          fontSize: 11,
                          color: overdue ? AppTheme.danger : AppTheme.textSecondary,
                          fontWeight: overdue ? FontWeight.w700 : FontWeight.normal),
                    ),
                    if (overdue)
                      const Padding(
                        padding: EdgeInsets.only(left: 4),
                        child: Text('EN RETARD',
                            style: TextStyle(
                                fontSize: 9,
                                fontWeight: FontWeight.w800,
                                color: AppTheme.danger)),
                      ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _priorityLabel(String p) => switch (p) {
        'high' => 'Haute',
        'medium' => 'Moyenne',
        _ => 'Basse',
      };

  String _formatDate(DateTime d) =>
      '${d.day.toString().padLeft(2, '0')}/${d.month.toString().padLeft(2, '0')}/${d.year}';
}

class _EmptyTasks extends StatelessWidget {
  final String? filter;
  final VoidCallback onAdd;

  const _EmptyTasks({required this.filter, required this.onAdd});

  @override
  Widget build(BuildContext context) {
    final msgs = {
      'today': ("Pas de tâche aujourd'hui", 'Prenez du repos !'),
      'overdue': ('Aucun retard', 'Tout est à jour, bravo !'),
      'done': ('Aucune tâche terminée', 'Commencez à cocher vos tâches'),
      null: ('Aucune tâche à faire', 'Ajoutez votre première tâche'),
    };
    final (title, sub) = msgs[filter] ?? ('Aucune tâche', '');

    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.task_outlined, size: 64, color: AppTheme.textSecondary),
          const SizedBox(height: 16),
          Text(title,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          Text(sub, style: const TextStyle(color: AppTheme.textSecondary)),
          if (filter == null) ...[
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: onAdd,
              icon: const Icon(Icons.add_task),
              label: const Text('Ajouter une tâche'),
            ),
          ],
        ],
      ),
    );
  }
}

class _AddTaskSheet extends StatefulWidget {
  final VoidCallback onSaved;
  const _AddTaskSheet({required this.onSaved});

  @override
  State<_AddTaskSheet> createState() => _AddTaskSheetState();
}

class _AddTaskSheetState extends State<_AddTaskSheet> {
  final _formKey = GlobalKey<FormState>();
  final _title = TextEditingController();
  final _desc = TextEditingController();
  String _priority = 'medium';
  DateTime? _dueDate;
  bool _loading = false;

  @override
  void dispose() {
    _title.dispose();
    _desc.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(days: 1)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );
    if (picked != null) setState(() => _dueDate = picked);
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      await ApiService.instance.createTask({
        'title': _title.text.trim(),
        if (_desc.text.isNotEmpty) 'description': _desc.text.trim(),
        'priority': _priority,
        if (_dueDate != null)
          'due_date': _dueDate!.toIso8601String().split('T').first,
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
            const Text('Nouvelle tâche',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
            const SizedBox(height: 16),
            TextFormField(
              controller: _title,
              decoration: const InputDecoration(labelText: 'Titre *'),
              validator: (v) => v == null || v.isEmpty ? 'Requis' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _desc,
              decoration: const InputDecoration(labelText: 'Description'),
              maxLines: 2,
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _priority,
                    decoration: const InputDecoration(labelText: 'Priorité'),
                    items: const [
                      DropdownMenuItem(value: 'low', child: Text('Basse')),
                      DropdownMenuItem(value: 'medium', child: Text('Moyenne')),
                      DropdownMenuItem(value: 'high', child: Text('Haute')),
                    ],
                    onChanged: (v) => setState(() => _priority = v ?? 'medium'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: GestureDetector(
                    onTap: _pickDate,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                      decoration: BoxDecoration(
                        border: Border.all(color: const Color(0xFFE5E7EB)),
                        borderRadius: BorderRadius.circular(10),
                        color: Colors.white,
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.calendar_today_outlined, size: 18,
                              color: AppTheme.textSecondary),
                          const SizedBox(width: 8),
                          Text(
                            _dueDate != null
                                ? '${_dueDate!.day}/${_dueDate!.month}/${_dueDate!.year}'
                                : 'Échéance',
                            style: TextStyle(
                              fontSize: 14,
                              color: _dueDate != null
                                  ? AppTheme.textPrimary
                                  : AppTheme.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _loading ? null : _save,
              child: _loading
                  ? const SizedBox(
                      width: 18, height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Text('Créer la tâche'),
            ),
          ],
        ),
      ),
    );
  }
}
