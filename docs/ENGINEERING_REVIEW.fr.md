# Revue d’ingénierie (FR)

## Synthèse
Le backend est fonctionnel et organisé autour de blueprints Flask. Les flux principaux (auth, CRUD des cartes, listings admin) sont présents, mais plusieurs points de fiabilité, de cohérence et de tests doivent être améliorés.

## Problèmes & Risques
1. **Sérialisation utilisateur incohérente**
   - Deux méthodes `serialize()` existaient ; la dernière écrasait la première et omettait `stripe_customer_id`.
   - Correction appliquée dans le code avec une seule méthode complète.

2. **Vue publique de carte incohérente**
   - `GET /view/<int:card_id>` utilise un ID entier alors que `Card.id` est un UUID string.
   - Le template `view_card.html` est référencé mais absent.
   - Impact : 404 sur des UUID valides et rendu impossible.

3. **Validation des entrées insuffisante**
   - La création de carte accepte des champs manquants (`name`, `title`, `email`) alors que le modèle les exige.
   - Risque d’erreurs SQL en production (500 au lieu de 4xx).

4. **Emplacement des backups ambigu**
   - Le listing admin utilise `os.getcwd()`, dépendant du process manager.
   - Préférer `app.instance_path` ou une config explicite.

5. **Appels Stripe fragiles**
   - `/api/v1/stripe/config` dépend d’appels externes sans gestion fine des clés manquantes.
   - Prévoir un mode « gracieux » en absence de configuration.

6. **Storage du rate limiting**
   - Stockage en mémoire, non adapté à la prod (perte au redémarrage, pas scalable).

## Tests manquants
- **Routes publiques** : `GET /health`, `GET /view/<card_id>`.
- **QR** : `POST /api/v1/qr/generate` (success + erreurs).
- **Stripe** : `/config` (mock SDK) et `/webhook` (events).
- **Admin** : export CSV/JSON, restauration, contrôle d’accès non-admin.
- **Cards** : validation, accès à carte supprimée, limite pro.
- **Auth** : upload avatar et cas d’erreur.

## Recommandations
1. Ajouter la validation des champs obligatoires pour la création/édition de cartes.
2. Aligner la route publique sur les UUID et ajouter le template manquant (ou supprimer la route).
3. Centraliser le chemin des backups via la config.
4. Gérer le cas Stripe non configuré de manière sûre.
5. Étendre la couverture de tests sur les routes publiques/QR/Stripe/admin.
