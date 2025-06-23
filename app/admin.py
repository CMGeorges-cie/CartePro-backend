from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelViewfrom
from flask import session, redirect, url_for, request
from.models import db, Card, User, Subscription


# On  crée une vue de base qui vérifie si l'utilisateur est un administrateur
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            return user and user.is_admin
        return False

    def inaccessible_callback(self, name, **kwargs):
        # Redirige les utilisateurs non connectés vers la page de login
        return redirect(url_for('auth.login', next=request.url))
    
# --- Définition des vues pour chaque modèle ---
class UserAdminView(ModelView):
    #colonnes à afficher dans la liste
    column_list = ('id', 'username', 'stripe_customer_id')
    # permet la recherche par nom d'utilisateur
    column_filters = ('username',)
    #TODO: permet la recherche par email

class SubscriptionAdminView(ModelView):
    #colonnes à afficher dans la liste
    column_list = ('id', 'user_id', 'plan_name', 'status', 'current_period_end')
    # permet la recherche par id d'utilisateur
    column_filters = ('user_id', 'plan_name', 'status')

class CardAdminView(ModelView):
    #colonnes à afficher dans la liste
    column_list = ('id', 'name', 'user_id', 'plan_type', 'is_active',)
    # permet la recherche par nom, email et titre
    column_filters = ( 'plan_type', 'is_active',)


# --- Initialisation de l'admin ---
# On passe notre vue sécurisée en paramètre
admin = Admin(name='QR Card Dashboard', template_mode='bootstrap4', index_view=MyAdminIndexView())

# On ajoute chaque vue au portail
admin.add_view(UserAdminView(User, db.session))
admin.add_view(SubscriptionAdminView(Subscription, db.session, category="Billing"))
admin.add_view(CardAdminView(Card, db.session, category="Content"))