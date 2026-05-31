class Contact {
  final int id;
  final String firstName;
  final String? lastName;
  final String fullName;
  final String? email;
  final String? phone;
  final String? company;
  final String? city;
  final String pipelineStage;
  final String? source;
  final DateTime createdAt;

  const Contact({
    required this.id,
    required this.firstName,
    this.lastName,
    required this.fullName,
    this.email,
    this.phone,
    this.company,
    this.city,
    required this.pipelineStage,
    this.source,
    required this.createdAt,
  });

  factory Contact.fromJson(Map<String, dynamic> json) => Contact(
        id: json['id'],
        firstName: json['first_name'],
        lastName: json['last_name'],
        fullName: json['full_name'] ?? json['first_name'],
        email: json['email'],
        phone: json['phone'],
        company: json['company'],
        city: json['city'],
        pipelineStage: json['pipeline_stage'] ?? 'new',
        source: json['source'],
        createdAt: DateTime.parse(json['created_at']),
      );

  static const stageLabels = {
    'new': 'Nouveau',
    'contacted': 'Contacté',
    'quote_sent': 'Soumission envoyée',
    'won': 'Gagné',
    'lost': 'Perdu',
  };

  String get stageFr => stageLabels[pipelineStage] ?? pipelineStage;
}
