class ApiConfig {
  // Changer cette URL pour pointer vers votre backend Render en production
  static const String baseUrl =
      String.fromEnvironment('API_URL', defaultValue: 'http://10.0.2.2:5000');

  static const Duration connectTimeout = Duration(seconds: 10);
  static const Duration receiveTimeout = Duration(seconds: 30);

  // Endpoints
  static const String auth = '/auth';
  static const String cards = '/api/v1/cards';
  static const String crm = '/api/v1/crm';
  static const String stripe = '/api/v1/stripe';
  static const String qr = '/api/v1/qr';
}
