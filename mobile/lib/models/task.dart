class Task {
  final int id;
  final String title;
  final String? description;
  final DateTime? dueDate;
  final bool isDone;
  final String priority;
  final int? contactId;

  const Task({
    required this.id,
    required this.title,
    this.description,
    this.dueDate,
    required this.isDone,
    required this.priority,
    this.contactId,
  });

  factory Task.fromJson(Map<String, dynamic> json) => Task(
        id: json['id'],
        title: json['title'],
        description: json['description'],
        dueDate: json['due_date'] != null ? DateTime.parse(json['due_date']) : null,
        isDone: json['is_done'] ?? false,
        priority: json['priority'] ?? 'medium',
        contactId: json['contact_id'],
      );

  bool get isOverdue =>
      !isDone && dueDate != null && dueDate!.isBefore(DateTime.now());
}
