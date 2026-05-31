import 'package:cookie_jar/cookie_jar.dart';
import 'package:dio/dio.dart';
import 'package:dio_cookie_manager/dio_cookie_manager.dart';
import 'package:flutter/foundation.dart';
import '../config/api_config.dart';

/// Client HTTP singleton avec gestion automatique des cookies de session Flask-Login.
class ApiService {
  ApiService._();
  static final ApiService instance = ApiService._();

  late final Dio _dio;
  final CookieJar _cookieJar = CookieJar();

  void init() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: ApiConfig.connectTimeout,
      receiveTimeout: ApiConfig.receiveTimeout,
      contentType: 'application/json',
    ));
    _dio.interceptors.add(CookieManager(_cookieJar));
    if (kDebugMode) {
      _dio.interceptors.add(LogInterceptor(responseBody: true));
    }
  }

  // ── Auth ──────────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> login(String username, String password) async {
    final res = await _dio.post('${ApiConfig.auth}/login',
        data: {'username': username, 'password': password});
    return res.data;
  }

  Future<void> logout() async {
    await _dio.post('${ApiConfig.auth}/logout');
    await _cookieJar.deleteAll();
  }

  Future<Map<String, dynamic>> register(
      String username, String email, String password) async {
    final res = await _dio.post('${ApiConfig.auth}/register',
        data: {'username': username, 'email': email, 'password': password});
    return res.data;
  }

  Future<Map<String, dynamic>> getMe() async {
    final res = await _dio.get('${ApiConfig.auth}/me');
    return res.data;
  }

  // ── Cartes ────────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> listCards({int page = 1}) async {
    final res = await _dio.get(ApiConfig.cards, queryParameters: {'page': page});
    return res.data;
  }

  Future<Map<String, dynamic>> createCard(Map<String, dynamic> data) async {
    final res = await _dio.post('${ApiConfig.cards}/', data: data);
    return res.data;
  }

  Future<Map<String, dynamic>> getCard(String cardId) async {
    final res = await _dio.get('${ApiConfig.cards}/$cardId');
    return res.data;
  }

  Future<void> updateCard(String cardId, Map<String, dynamic> data) async {
    await _dio.put('${ApiConfig.cards}/$cardId', data: data);
  }

  Future<void> recordScan(String cardId) async {
    await _dio.post('${ApiConfig.cards}/$cardId/scan');
  }

  Future<List<dynamic>> getPhotos(String cardId) async {
    final res = await _dio.get('${ApiConfig.cards}/$cardId/photos');
    return res.data;
  }

  Future<Map<String, dynamic>> submitQuote(
      String cardId, Map<String, dynamic> data) async {
    final res = await _dio.post('${ApiConfig.cards}/$cardId/quote', data: data);
    return res.data;
  }

  Future<Map<String, dynamic>> getScanStats(String cardId,
      {int page = 1}) async {
    final res = await _dio
        .get('${ApiConfig.cards}/$cardId/scans', queryParameters: {'page': page});
    return res.data;
  }

  // ── CRM — Contacts ────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> getCrmDashboard() async {
    final res = await _dio.get('${ApiConfig.crm}/dashboard');
    return res.data;
  }

  Future<Map<String, dynamic>> getPipeline() async {
    final res = await _dio.get('${ApiConfig.crm}/pipeline');
    return res.data;
  }

  Future<Map<String, dynamic>> listContacts({
    int page = 1,
    String? stage,
    String? search,
  }) async {
    final res = await _dio.get('${ApiConfig.crm}/contacts', queryParameters: {
      'page': page,
      if (stage != null) 'stage': stage,
      if (search != null && search.isNotEmpty) 'q': search,
    });
    return res.data;
  }

  Future<Map<String, dynamic>> createContact(Map<String, dynamic> data) async {
    final res = await _dio.post('${ApiConfig.crm}/contacts', data: data);
    return res.data;
  }

  Future<Map<String, dynamic>> getContact(int contactId) async {
    final res = await _dio.get('${ApiConfig.crm}/contacts/$contactId');
    return res.data;
  }

  Future<void> updateContact(int contactId, Map<String, dynamic> data) async {
    await _dio.put('${ApiConfig.crm}/contacts/$contactId', data: data);
  }

  Future<void> updateContactStage(int contactId, String stage) async {
    await _dio.patch('${ApiConfig.crm}/contacts/$contactId/stage',
        data: {'stage': stage});
  }

  Future<void> deleteContact(int contactId) async {
    await _dio.delete('${ApiConfig.crm}/contacts/$contactId');
  }

  Future<Map<String, dynamic>> contactFromQuote(int quoteId) async {
    final res = await _dio
        .post('${ApiConfig.crm}/contacts/from-quote/$quoteId');
    return res.data;
  }

  // ── CRM — Notes ───────────────────────────────────────────────────────────

  Future<List<dynamic>> getNotes(int contactId) async {
    final res =
        await _dio.get('${ApiConfig.crm}/contacts/$contactId/notes');
    return res.data;
  }

  Future<Map<String, dynamic>> addNote(int contactId, String content) async {
    final res = await _dio.post('${ApiConfig.crm}/contacts/$contactId/notes',
        data: {'content': content});
    return res.data;
  }

  Future<void> deleteNote(int noteId) async {
    await _dio.delete('${ApiConfig.crm}/notes/$noteId');
  }

  // ── CRM — Tâches ─────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> listTasks({
    bool? done,
    bool dueToday = false,
    int? contactId,
  }) async {
    final res = await _dio.get('${ApiConfig.crm}/tasks', queryParameters: {
      if (done != null) 'done': done.toString(),
      if (dueToday) 'due_today': 'true',
      if (contactId != null) 'contact_id': contactId,
    });
    return res.data;
  }

  Future<Map<String, dynamic>> createTask(Map<String, dynamic> data) async {
    final res = await _dio.post('${ApiConfig.crm}/tasks', data: data);
    return res.data;
  }

  Future<void> toggleTask(int taskId) async {
    await _dio.patch('${ApiConfig.crm}/tasks/$taskId/done');
  }

  Future<void> deleteTask(int taskId) async {
    await _dio.delete('${ApiConfig.crm}/tasks/$taskId');
  }

  // ── Stripe ────────────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> createCheckout(String plan) async {
    final res = await _dio.post('${ApiConfig.stripe}/create-checkout',
        data: {'plan': plan});
    return res.data;
  }

  Future<Map<String, dynamic>> getCustomerPortal() async {
    final res = await _dio.get('${ApiConfig.stripe}/portal');
    return res.data;
  }
}
