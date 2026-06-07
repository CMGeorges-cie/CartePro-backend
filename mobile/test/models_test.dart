import 'package:flutter_test/flutter_test.dart';
import 'package:cartepro_pro/models/contact.dart';
import 'package:cartepro_pro/models/task.dart';
import 'package:cartepro_pro/models/card_model.dart';

void main() {
  group('Contact', () {
    test('fromJson parses all fields', () {
      final json = {
        'id': 1,
        'first_name': 'Jean',
        'last_name': 'Tremblay',
        'full_name': 'Jean Tremblay',
        'email': 'jean@test.com',
        'phone': '514-555-0101',
        'company': 'Peinture JT',
        'city': 'Montréal',
        'pipeline_stage': 'contacted',
        'source': 'qr_scan',
        'created_at': '2026-01-15T10:00:00',
      };
      final c = Contact.fromJson(json);
      expect(c.id, 1);
      expect(c.fullName, 'Jean Tremblay');
      expect(c.pipelineStage, 'contacted');
      expect(c.stageFr, 'Contacté');
    });

    test('stageFr returns unknown stage as-is', () {
      final json = {
        'id': 2,
        'first_name': 'Marie',
        'full_name': 'Marie',
        'pipeline_stage': 'unknown_stage',
        'created_at': '2026-01-15T10:00:00',
      };
      final c = Contact.fromJson(json);
      expect(c.stageFr, 'unknown_stage');
    });

    test('stageLabels covers all 5 pipeline stages', () {
      expect(Contact.stageLabels.length, 5);
      for (final stage in ['new', 'contacted', 'quote_sent', 'won', 'lost']) {
        expect(Contact.stageLabels.containsKey(stage), isTrue);
      }
    });
  });

  group('Task', () {
    test('fromJson parses isDone and priority', () {
      final json = {
        'id': 10,
        'title': 'Rappeler client',
        'description': 'Pour confirmer RDV',
        'due_date': '2026-06-01T00:00:00',
        'is_done': false,
        'priority': 'high',
        'contact_id': 1,
      };
      final t = Task.fromJson(json);
      expect(t.id, 10);
      expect(t.isDone, false);
      expect(t.priority, 'high');
      expect(t.contactId, 1);
    });

    test('isOverdue true when past due and not done', () {
      final past = DateTime.now().subtract(const Duration(days: 2));
      final json = {
        'id': 11,
        'title': 'Tâche en retard',
        'is_done': false,
        'priority': 'medium',
        'due_date': past.toIso8601String(),
      };
      final t = Task.fromJson(json);
      expect(t.isOverdue, isTrue);
    });

    test('isOverdue false when task is done', () {
      final past = DateTime.now().subtract(const Duration(days: 2));
      final json = {
        'id': 12,
        'title': 'Tâche terminée',
        'is_done': true,
        'priority': 'low',
        'due_date': past.toIso8601String(),
      };
      final t = Task.fromJson(json);
      expect(t.isOverdue, isFalse);
    });

    test('isOverdue false when no due date', () {
      final json = {
        'id': 13,
        'title': 'Sans échéance',
        'is_done': false,
        'priority': 'low',
      };
      final t = Task.fromJson(json);
      expect(t.isOverdue, isFalse);
    });
  });

  group('CardModel', () {
    test('fromJson parses all pro fields', () {
      final json = {
        'id': 'abc-123',
        'name': 'Jean Peintre',
        'title': 'Maître Peintre',
        'email': 'jean@peinture.ca',
        'phone': '514-555-0001',
        'trade': 'Peinture',
        'service_zone': 'Montréal',
        'bio': 'Expert depuis 15 ans',
        'google_review_url': 'https://g.page/r/abc',
        'facebook_url': 'https://fb.com/jean',
        'whatsapp_number': '5145550001',
        'instagram': '@jean_peintre',
        'linkedin': 'https://linkedin.com/in/jean',
        'is_active': true,
        'plan_type': 'monthly',
      };
      final c = CardModel.fromJson(json);
      expect(c.id, 'abc-123');
      expect(c.trade, 'Peinture');
      expect(c.planType, 'monthly');
      expect(c.isActive, isTrue);
      expect(c.googleReviewUrl, 'https://g.page/r/abc');
    });

    test('fromJson defaults plan_type to none', () {
      final json = {
        'id': 'xyz',
        'name': 'Test',
        'title': 'Test',
        'email': 'test@test.com',
        'is_active': true,
      };
      final c = CardModel.fromJson(json);
      expect(c.planType, 'none');
    });
  });
}

