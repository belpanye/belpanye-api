from django.db import models
from django.core.validators import URLValidator, FileExtensionValidator


class AppConfiguration(models.Model):
    """
    Configuration singleton pour l'application
    Une seule instance active à la fois
    """
    # Branding & Interface
    company_name = models.CharField(
        max_length=100, 
        default="Belpanye", 
        verbose_name="Nom de l'entreprise"
    )
    
    logo = models.ImageField(
        upload_to='branding/logos/', 
        null=True, blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'svg'])],
        verbose_name="Logo principal"
    )
    
    favicon = models.ImageField(
        upload_to='branding/favicons/', 
        null=True, blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['ico', 'png'])],
        verbose_name="Favicon"
    )
    
    primary_color = models.CharField(
        max_length=7,
        default='#3B82F6', 
        verbose_name="Couleur principale"
    )
    
    
    font_family = models.CharField(
        max_length=50,
        choices=[
            ('Inter', 'Inter'),
            ('Roboto', 'Roboto'),
            ('Open Sans', 'Open Sans'),
            ('Lato', 'Lato'),
            ('Montserrat', 'Montserrat'),
            ('Poppins', 'Poppins'),
        ],
        default='Inter',
        verbose_name="Police de caractères"
    )
    
    # Réseaux sociaux
    facebook_url = models.URLField(blank=True, verbose_name="Facebook")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram")
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name="WhatsApp")
    twitter_url = models.URLField(blank=True, verbose_name="Twitter")
    
    # Paiement
    stripe_enabled = models.BooleanField(default=True, verbose_name="Activer Stripe")
    paypal_enabled = models.BooleanField(default=False, verbose_name="Activer PayPal")
    moncash_enabled = models.BooleanField(default=True, verbose_name="Activer MonCash")
    
    stripe_publishable_key = models.CharField(max_length=200, blank=True, verbose_name="Clé publique Stripe")
    paypal_client_id = models.CharField(max_length=200, blank=True, verbose_name="Client ID PayPal")
    moncash_client_id = models.CharField(max_length=200, blank=True, verbose_name="Client ID MonCash")
    
    usd_to_htg_rate = models.DecimalField(
        max_digits=10, decimal_places=2, 
        default=150.00,
        verbose_name="Taux USD vers HTG"
    )
    
    vat_rate = models.DecimalField(
        max_digits=5, decimal_places=2, 
        default=0.00,
        verbose_name="Taux de TVA (%)"
    )
    
    handling_fee_per_package = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=2.00,
        verbose_name="Frais de manutention par colis ($)"
    )
    
    # Notifications
    email_notifications_enabled = models.BooleanField(default=True, verbose_name="Notifications email")
    sms_notifications_enabled = models.BooleanField(default=False, verbose_name="Notifications SMS")
    whatsapp_notifications_enabled = models.BooleanField(default=True, verbose_name="Notifications WhatsApp")
    
    smtp_host = models.CharField(max_length=100, blank=True, verbose_name="Serveur SMTP")
    smtp_port = models.IntegerField(default=587, verbose_name="Port SMTP")
    smtp_username = models.CharField(max_length=100, blank=True, verbose_name="Utilisateur SMTP")
    smtp_use_tls = models.BooleanField(default=True, verbose_name="Utiliser TLS")
    
    # Moment des notifications
    notify_on_package_received = models.BooleanField(default=True, verbose_name="Notifier à la réception")
    notify_on_shipment_created = models.BooleanField(default=True, verbose_name="Notifier à la création d'expédition")
    notify_on_shipment_shipped = models.BooleanField(default=True, verbose_name="Notifier à l'expédition")
    notify_on_shipment_delivered = models.BooleanField(default=True, verbose_name="Notifier à la livraison")
    
    # Services & Activités
    consolidation_enabled = models.BooleanField(default=True, verbose_name="Activer la consolidation")
    free_storage_days = models.IntegerField(default=30, verbose_name="Jours de stockage gratuit")
    public_tracking_enabled = models.BooleanField(default=True, verbose_name="Tracking public")
    
    air_shipping_enabled = models.BooleanField(default=True, verbose_name="Transport aérien")
    sea_shipping_enabled = models.BooleanField(default=True, verbose_name="Transport maritime")
    express_shipping_enabled = models.BooleanField(default=False, verbose_name="Livraison express")
    
    # Prix par kg
    air_shipping_rate_per_kg = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0.00,
        verbose_name="Prix transport aérien ($/kg)"
    )
    
    sea_shipping_rate_per_kg = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0.00,
        verbose_name="Prix transport maritime ($/kg)"
    )
    
    express_shipping_rate_per_kg = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0.00,
        verbose_name="Prix livraison express ($/kg)"
    )
    
    # Pays autorisés
    allowed_delivery_countries = models.TextField(
        default="Haiti",
        verbose_name="Pays de livraison autorisés",
        help_text="Un pays par ligne"
    )
    
    # Localisation & contenu
    available_languages = models.CharField(
        max_length=50,
        default="fr,en",
        verbose_name="Langues disponibles",
        help_text="Codes séparés par des virgules (ex: fr,en,ht)"
    )
    
    welcome_message_fr = models.TextField(
        default="Bienvenue sur Belpanye - Votre service de réexpédition vers Haïti",
        verbose_name="Message d'accueil (Français)"
    )
    
    welcome_message_en = models.TextField(
        default="Welcome to Belpanye - Your package forwarding service to Haiti",
        verbose_name="Message d'accueil (Anglais)"
    )
    
    privacy_policy = models.TextField(blank=True, verbose_name="Politique de confidentialité")
    terms_of_service = models.TextField(blank=True, verbose_name="Conditions d'utilisation")
    
    # Utilisateurs & sécurité
    email_verification_required = models.BooleanField(default=True, verbose_name="Vérification email obligatoire")
    manual_account_approval = models.BooleanField(default=False, verbose_name="Validation manuelle des comptes")
    max_packages_per_user = models.IntegerField(default=10, verbose_name="Nombre max de colis par utilisateur")
    max_package_weight_kg = models.DecimalField(
        max_digits=8, decimal_places=2,
        default=50.00,
        verbose_name="Poids max par colis (kg)"
    )
    
    two_factor_auth_enabled = models.BooleanField(default=False, verbose_name="Authentification à 2 facteurs")
    
    blocked_countries = models.TextField(
        blank=True,
        verbose_name="Pays bloqués",
        help_text="Un pays par ligne"
    )
    
    # Statistiques & rapports
    default_report_period = models.CharField(
        max_length=20,
        choices=[
            ('week', 'Semaine'),
            ('month', 'Mois'),
            ('quarter', 'Trimestre'),
            ('year', 'Année'),
        ],
        default='month',
        verbose_name="Période par défaut des rapports"
    )
    
    auto_export_reports = models.BooleanField(default=False, verbose_name="Export automatique des rapports")
    client_report_access = models.BooleanField(default=True, verbose_name="Accès client aux rapports")
    
    # Métadonnées
    is_active = models.BooleanField(default=True, verbose_name="Configuration active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuration de l'application"
        verbose_name_plural = "Configurations de l'application"
    
    def __str__(self):
        return f"Configuration {self.company_name} - {self.updated_at.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'une seule configuration est active
        if self.is_active:
            AppConfiguration.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_config(cls):
        """Récupère la configuration active ou crée une configuration par défaut"""
        config = cls.objects.filter(is_active=True).first()
        if not config:
            config = cls.objects.create(is_active=True)
        return config


class NotificationTemplate(models.Model):
    """Templates personnalisables pour les notifications"""
    
    TEMPLATE_TYPES = [
        ('package_received', 'Colis reçu'),
        ('shipment_created', 'Expédition créée'),
        ('shipment_shipped', 'Expédition envoyée'),
        ('shipment_delivered', 'Expédition livrée'),
        ('payment_received', 'Paiement reçu'),
        ('account_created', 'Compte créé'),
    ]
    
    name = models.CharField(max_length=50, choices=TEMPLATE_TYPES, unique=True)
    
    # Email
    email_subject = models.CharField(max_length=200, verbose_name="Sujet email")
    email_body = models.TextField(verbose_name="Corps email")
    
    # SMS/WhatsApp
    sms_body = models.TextField(verbose_name="Message SMS/WhatsApp", max_length=1600)
    
    # Variables disponibles
    available_variables = models.TextField(
        verbose_name="Variables disponibles",
        help_text="Variables utilisables: {user_name}, {package_number}, {tracking_number}, etc.",
        editable=False
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Template de notification"
        verbose_name_plural = "Templates de notifications"
    
    def __str__(self):
        return f"Template {self.get_name_display()}"


class MaintenanceMode(models.Model):
    """Mode maintenance pour l'application"""
    
    is_enabled = models.BooleanField(default=False, verbose_name="Mode maintenance actif")
    message = models.TextField(
        default="Site en maintenance. Nous reviendrons bientôt!",
        verbose_name="Message de maintenance"
    )
    estimated_end_time = models.DateTimeField(null=True, blank=True, verbose_name="Fin estimée")
    allowed_ips = models.TextField(
        blank=True,
        verbose_name="IPs autorisées",
        help_text="Une IP par ligne"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Mode maintenance"
        verbose_name_plural = "Modes maintenance"
    
    def __str__(self):
        status = "Actif" if self.is_enabled else "Inactif"
        return f"Maintenance {status}"
