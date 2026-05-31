class CardModel {
  final String id;
  final String name;
  final String title;
  final String email;
  final String? phone;
  final String? website;
  final String? trade;
  final String? serviceZone;
  final String? bio;
  final String? googleReviewUrl;
  final String? facebookUrl;
  final String? whatsappNumber;
  final String? instagram;
  final String? linkedin;
  final bool isActive;
  final String planType;

  const CardModel({
    required this.id,
    required this.name,
    required this.title,
    required this.email,
    this.phone,
    this.website,
    this.trade,
    this.serviceZone,
    this.bio,
    this.googleReviewUrl,
    this.facebookUrl,
    this.whatsappNumber,
    this.instagram,
    this.linkedin,
    required this.isActive,
    required this.planType,
  });

  factory CardModel.fromJson(Map<String, dynamic> json) => CardModel(
        id: json['id'],
        name: json['name'],
        title: json['title'],
        email: json['email'],
        phone: json['phone'],
        website: json['website'],
        trade: json['trade'],
        serviceZone: json['service_zone'],
        bio: json['bio'],
        googleReviewUrl: json['google_review_url'],
        facebookUrl: json['facebook_url'],
        whatsappNumber: json['whatsapp_number'],
        instagram: json['instagram'],
        linkedin: json['linkedin'],
        isActive: json['is_active'] ?? true,
        planType: json['plan_type'] ?? 'none',
      );
}
