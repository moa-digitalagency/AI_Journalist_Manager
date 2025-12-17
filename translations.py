"""
Multilingual translation system for AI Journalist Manager.
Supports French (fr) and English (en).
"""

TRANSLATIONS = {
    'fr': {
        # Common
        'app_name': 'AI Journalist Manager',
        'admin_panel': 'Panneau d\'administration',
        'powered_by': 'Propulsé par Gemini AI & Telegram',
        'save': 'Enregistrer',
        'cancel': 'Annuler',
        'delete': 'Supprimer',
        'edit': 'Modifier',
        'view': 'Voir',
        'create': 'Créer',
        'add': 'Ajouter',
        'back': 'Retour',
        'search': 'Rechercher',
        'actions': 'Actions',
        'status': 'Statut',
        'active': 'Actif',
        'inactive': 'Inactif',
        'yes': 'Oui',
        'no': 'Non',
        'loading': 'Chargement...',
        'confirm_delete': 'Êtes-vous sûr de vouloir supprimer cet élément ?',
        'no_data': 'Aucune donnée disponible',
        'total': 'Total',
        'details': 'Détails',
        
        # Auth
        'login': 'Se connecter',
        'logout': 'Déconnexion',
        'username': 'Identifiant',
        'username_or_email': 'Nom d\'utilisateur ou email',
        'password': 'Mot de passe',
        'remember_me': 'Se souvenir de moi',
        'login_error': 'Identifiant ou mot de passe incorrect',
        'login_required': 'Veuillez vous connecter pour accéder à cette page',
        'account_disabled': 'Votre compte est désactivé',
        
        # Navigation
        'dashboard': 'Tableau de bord',
        'journalists': 'Journalistes',
        'subscribers': 'Abonnés',
        'plans': 'Forfaits',
        'logs': 'Logs',
        'users': 'Utilisateurs',
        'settings': 'Paramètres',
        'system': 'Système',
        'new_journalist': 'Nouveau Journaliste',
        
        # Dashboard
        'welcome': 'Bienvenue',
        'overview': 'Vue d\'ensemble',
        'total_journalists': 'Total Journalistes',
        'active_journalists': 'Journalistes Actifs',
        'total_subscribers': 'Total Abonnés',
        'active_subscribers': 'Abonnés Actifs',
        'total_articles': 'Total Articles',
        'articles_today': 'Articles Aujourd\'hui',
        'summaries_sent': 'Résumés Envoyés',
        'recent_activity': 'Activité Récente',
        'quick_actions': 'Actions Rapides',
        
        # Journalists
        'journalist': 'Journaliste',
        'journalist_name': 'Nom du journaliste',
        'journalist_description': 'Description',
        'journalist_topics': 'Sujets',
        'journalist_language': 'Langue',
        'journalist_timezone': 'Fuseau horaire',
        'telegram_bot_token': 'Token Bot Telegram',
        'telegram_channel': 'Canal Telegram',
        'sources': 'Sources',
        'add_source': 'Ajouter une source',
        'source_url': 'URL de la source',
        'source_type': 'Type de source',
        'rss_feed': 'Flux RSS',
        'website': 'Site Web',
        'create_journalist': 'Créer un journaliste',
        'edit_journalist': 'Modifier le journaliste',
        'journalist_created': 'Journaliste créé avec succès',
        'journalist_updated': 'Journaliste mis à jour avec succès',
        'journalist_deleted': 'Journaliste supprimé avec succès',
        'no_journalists': 'Aucun journaliste configuré',
        'start_bot': 'Démarrer le bot',
        'stop_bot': 'Arrêter le bot',
        'bot_running': 'Bot en cours d\'exécution',
        'bot_stopped': 'Bot arrêté',
        
        # Subscribers
        'subscriber': 'Abonné',
        'telegram_id': 'ID Telegram',
        'telegram_username': 'Nom d\'utilisateur Telegram',
        'subscription_plan': 'Forfait',
        'subscription_start': 'Début d\'abonnement',
        'subscription_end': 'Fin d\'abonnement',
        'subscribed_to': 'Abonné à',
        'no_subscribers': 'Aucun abonné',
        
        # Plans
        'plan': 'Forfait',
        'plan_name': 'Nom du forfait',
        'plan_description': 'Description',
        'plan_price': 'Prix',
        'plan_duration': 'Durée (jours)',
        'is_trial': 'Essai gratuit',
        'can_receive_summaries': 'Peut recevoir des résumés',
        'can_ask_questions': 'Peut poser des questions',
        'can_receive_audio': 'Peut recevoir l\'audio',
        'create_plan': 'Créer un forfait',
        'edit_plan': 'Modifier le forfait',
        'plan_created': 'Forfait créé avec succès',
        'plan_updated': 'Forfait mis à jour avec succès',
        'plan_deleted': 'Forfait supprimé avec succès',
        'no_plans': 'Aucun forfait configuré',
        'free_trial': 'Essai Gratuit',
        'per_month': '/mois',
        
        # Users
        'user': 'Utilisateur',
        'email': 'Email',
        'role': 'Rôle',
        'roles': 'Rôles',
        'permissions': 'Permissions',
        'superadmin': 'Super Admin',
        'is_active': 'Est actif',
        'create_user': 'Créer un utilisateur',
        'edit_user': 'Modifier l\'utilisateur',
        'user_created': 'Utilisateur créé avec succès',
        'user_updated': 'Utilisateur mis à jour avec succès',
        'user_deleted': 'Utilisateur supprimé avec succès',
        'no_users': 'Aucun utilisateur',
        'change_password': 'Changer le mot de passe',
        'new_password': 'Nouveau mot de passe',
        'confirm_password': 'Confirmer le mot de passe',
        'password_changed': 'Mot de passe changé avec succès',
        'passwords_not_match': 'Les mots de passe ne correspondent pas',
        'manage_roles': 'Gérer les rôles',
        'create_role': 'Créer un rôle',
        'edit_role': 'Modifier le rôle',
        'role_created': 'Rôle créé avec succès',
        'role_updated': 'Rôle mis à jour avec succès',
        'role_deleted': 'Rôle supprimé avec succès',
        
        # Logs
        'activity_logs': 'Logs d\'activité',
        'security_logs': 'Logs de sécurité',
        'timestamp': 'Horodatage',
        'action': 'Action',
        'description': 'Description',
        'ip_address': 'Adresse IP',
        'user_agent': 'Agent utilisateur',
        'no_logs': 'Aucun log disponible',
        
        # Settings
        'general_settings': 'Paramètres généraux',
        'ai_settings': 'Paramètres IA',
        'telegram_settings': 'Paramètres Telegram',
        'audio_settings': 'Paramètres Audio',
        'scheduler_settings': 'Paramètres du planificateur',
        'setting_updated': 'Paramètre mis à jour avec succès',
        'settings_saved': 'Paramètres enregistrés avec succès',
        'setting_key': 'Clé',
        'setting_value': 'Valeur',
        'setting_category': 'Catégorie',
        
        # Articles
        'article': 'Article',
        'articles': 'Articles',
        'article_title': 'Titre',
        'article_content': 'Contenu',
        'article_source': 'Source',
        'article_date': 'Date de publication',
        'fetch_articles': 'Récupérer les articles',
        'generate_summary': 'Générer le résumé',
        
        # Summaries
        'summary': 'Résumé',
        'summaries': 'Résumés',
        'daily_summary': 'Résumé quotidien',
        'summary_date': 'Date du résumé',
        'send_summary': 'Envoyer le résumé',
        'summary_sent': 'Résumé envoyé avec succès',
        
        # Errors
        'error_occurred': 'Une erreur s\'est produite',
        'not_found': 'Page non trouvée',
        'unauthorized': 'Accès non autorisé',
        'forbidden': 'Accès interdit',
        'invalid_data': 'Données invalides',
        'required_field': 'Ce champ est requis',
        
        # Success messages
        'success': 'Succès',
        'saved_successfully': 'Enregistré avec succès',
        'deleted_successfully': 'Supprimé avec succès',
        'updated_successfully': 'Mis à jour avec succès',
        'created_successfully': 'Créé avec succès',
        
        # Language
        'language': 'Langue',
        'french': 'Français',
        'english': 'English',
        'change_language': 'Changer de langue',
        
        # Additional
        'unknown': 'Inconnu',
        'system': 'Système',
        'this_week': 'cette semaine',
        'activity_7_days': 'Activité (7 jours)',
        'recent_journalists': 'Journalistes récents',
        'new_subscribers': 'Nouveaux abonnés',
        'view_all': 'Voir tout',
        'approved': 'Approuvé',
        'pending': 'En attente',
        'extend': 'Prolonger',
        'revoke': 'Révoquer',
    },
    
    'en': {
        # Common
        'app_name': 'AI Journalist Manager',
        'admin_panel': 'Administration Panel',
        'powered_by': 'Powered by Gemini AI & Telegram',
        'save': 'Save',
        'cancel': 'Cancel',
        'delete': 'Delete',
        'edit': 'Edit',
        'view': 'View',
        'create': 'Create',
        'add': 'Add',
        'back': 'Back',
        'search': 'Search',
        'actions': 'Actions',
        'status': 'Status',
        'active': 'Active',
        'inactive': 'Inactive',
        'yes': 'Yes',
        'no': 'No',
        'loading': 'Loading...',
        'confirm_delete': 'Are you sure you want to delete this item?',
        'no_data': 'No data available',
        'total': 'Total',
        'details': 'Details',
        
        # Auth
        'login': 'Login',
        'logout': 'Logout',
        'username': 'Username',
        'username_or_email': 'Username or email',
        'password': 'Password',
        'remember_me': 'Remember me',
        'login_error': 'Invalid username or password',
        'login_required': 'Please log in to access this page',
        'account_disabled': 'Your account is disabled',
        
        # Navigation
        'dashboard': 'Dashboard',
        'journalists': 'Journalists',
        'subscribers': 'Subscribers',
        'plans': 'Plans',
        'logs': 'Logs',
        'users': 'Users',
        'settings': 'Settings',
        'system': 'System',
        'new_journalist': 'New Journalist',
        
        # Dashboard
        'welcome': 'Welcome',
        'overview': 'Overview',
        'total_journalists': 'Total Journalists',
        'active_journalists': 'Active Journalists',
        'total_subscribers': 'Total Subscribers',
        'active_subscribers': 'Active Subscribers',
        'total_articles': 'Total Articles',
        'articles_today': 'Articles Today',
        'summaries_sent': 'Summaries Sent',
        'recent_activity': 'Recent Activity',
        'quick_actions': 'Quick Actions',
        
        # Journalists
        'journalist': 'Journalist',
        'journalist_name': 'Journalist name',
        'journalist_description': 'Description',
        'journalist_topics': 'Topics',
        'journalist_language': 'Language',
        'journalist_timezone': 'Timezone',
        'telegram_bot_token': 'Telegram Bot Token',
        'telegram_channel': 'Telegram Channel',
        'sources': 'Sources',
        'add_source': 'Add source',
        'source_url': 'Source URL',
        'source_type': 'Source type',
        'rss_feed': 'RSS Feed',
        'website': 'Website',
        'create_journalist': 'Create journalist',
        'edit_journalist': 'Edit journalist',
        'journalist_created': 'Journalist created successfully',
        'journalist_updated': 'Journalist updated successfully',
        'journalist_deleted': 'Journalist deleted successfully',
        'no_journalists': 'No journalists configured',
        'start_bot': 'Start bot',
        'stop_bot': 'Stop bot',
        'bot_running': 'Bot running',
        'bot_stopped': 'Bot stopped',
        
        # Subscribers
        'subscriber': 'Subscriber',
        'telegram_id': 'Telegram ID',
        'telegram_username': 'Telegram username',
        'subscription_plan': 'Subscription plan',
        'subscription_start': 'Subscription start',
        'subscription_end': 'Subscription end',
        'subscribed_to': 'Subscribed to',
        'no_subscribers': 'No subscribers',
        
        # Plans
        'plan': 'Plan',
        'plan_name': 'Plan name',
        'plan_description': 'Description',
        'plan_price': 'Price',
        'plan_duration': 'Duration (days)',
        'is_trial': 'Free trial',
        'can_receive_summaries': 'Can receive summaries',
        'can_ask_questions': 'Can ask questions',
        'can_receive_audio': 'Can receive audio',
        'create_plan': 'Create plan',
        'edit_plan': 'Edit plan',
        'plan_created': 'Plan created successfully',
        'plan_updated': 'Plan updated successfully',
        'plan_deleted': 'Plan deleted successfully',
        'no_plans': 'No plans configured',
        'free_trial': 'Free Trial',
        'per_month': '/month',
        
        # Users
        'user': 'User',
        'email': 'Email',
        'role': 'Role',
        'roles': 'Roles',
        'permissions': 'Permissions',
        'superadmin': 'Super Admin',
        'is_active': 'Is active',
        'create_user': 'Create user',
        'edit_user': 'Edit user',
        'user_created': 'User created successfully',
        'user_updated': 'User updated successfully',
        'user_deleted': 'User deleted successfully',
        'no_users': 'No users',
        'change_password': 'Change password',
        'new_password': 'New password',
        'confirm_password': 'Confirm password',
        'password_changed': 'Password changed successfully',
        'passwords_not_match': 'Passwords do not match',
        'manage_roles': 'Manage roles',
        'create_role': 'Create role',
        'edit_role': 'Edit role',
        'role_created': 'Role created successfully',
        'role_updated': 'Role updated successfully',
        'role_deleted': 'Role deleted successfully',
        
        # Logs
        'activity_logs': 'Activity Logs',
        'security_logs': 'Security Logs',
        'timestamp': 'Timestamp',
        'action': 'Action',
        'description': 'Description',
        'ip_address': 'IP Address',
        'user_agent': 'User Agent',
        'no_logs': 'No logs available',
        
        # Settings
        'general_settings': 'General Settings',
        'ai_settings': 'AI Settings',
        'telegram_settings': 'Telegram Settings',
        'audio_settings': 'Audio Settings',
        'scheduler_settings': 'Scheduler Settings',
        'setting_updated': 'Setting updated successfully',
        'settings_saved': 'Settings saved successfully',
        'setting_key': 'Key',
        'setting_value': 'Value',
        'setting_category': 'Category',
        
        # Articles
        'article': 'Article',
        'articles': 'Articles',
        'article_title': 'Title',
        'article_content': 'Content',
        'article_source': 'Source',
        'article_date': 'Publication date',
        'fetch_articles': 'Fetch articles',
        'generate_summary': 'Generate summary',
        
        # Summaries
        'summary': 'Summary',
        'summaries': 'Summaries',
        'daily_summary': 'Daily Summary',
        'summary_date': 'Summary date',
        'send_summary': 'Send summary',
        'summary_sent': 'Summary sent successfully',
        
        # Errors
        'error_occurred': 'An error occurred',
        'not_found': 'Page not found',
        'unauthorized': 'Unauthorized access',
        'forbidden': 'Access forbidden',
        'invalid_data': 'Invalid data',
        'required_field': 'This field is required',
        
        # Success messages
        'success': 'Success',
        'saved_successfully': 'Saved successfully',
        'deleted_successfully': 'Deleted successfully',
        'updated_successfully': 'Updated successfully',
        'created_successfully': 'Created successfully',
        
        # Language
        'language': 'Language',
        'french': 'Français',
        'english': 'English',
        'change_language': 'Change language',
        
        # Additional
        'unknown': 'Unknown',
        'system': 'System',
        'this_week': 'this week',
        'activity_7_days': 'Activity (7 days)',
        'recent_journalists': 'Recent Journalists',
        'new_subscribers': 'New Subscribers',
        'view_all': 'View all',
        'approved': 'Approved',
        'pending': 'Pending',
        'extend': 'Extend',
        'revoke': 'Revoke',
    }
}


def get_translation(key, lang='fr'):
    """Get a translation for a given key and language."""
    if lang not in TRANSLATIONS:
        lang = 'fr'
    return TRANSLATIONS.get(lang, {}).get(key, key)


def get_all_translations(lang='fr'):
    """Get all translations for a given language."""
    if lang not in TRANSLATIONS:
        lang = 'fr'
    return TRANSLATIONS.get(lang, {})


class TranslationHelper:
    """Helper class for template translations."""
    
    def __init__(self, lang='fr'):
        self.lang = lang
        self.translations = TRANSLATIONS.get(lang, TRANSLATIONS['fr'])
    
    def __call__(self, key):
        return self.translations.get(key, key)
    
    def get(self, key, default=None):
        return self.translations.get(key, default if default else key)
