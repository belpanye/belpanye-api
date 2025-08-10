from django.db import models
from django.core.validators import RegexValidator


class Address(models.Model):
    ADDRESS_TYPES = [
        ('warehouse', 'Entrepôt'),
        ('office', 'Bureau'),
        ('pickup_point', 'Point de retrait'),
    ]
    
    COUNTRIES = [
        ('US', 'États-Unis'),
        ('HT', 'Haïti'),
        ('CA', 'Canada'),
        ('FR', 'France'),
    ]
    
    # Informations de base
    type = models.CharField(
        max_length=20, 
        choices=ADDRESS_TYPES,
        verbose_name="Type d'adresse"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nom de l'établissement"
    )
    
    # Localisation
    country = models.CharField(
        max_length=2,
        choices=COUNTRIES,
        verbose_name="Pays"
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Ville"
    )
    address_line1 = models.CharField(
        max_length=200,
        verbose_name="Adresse ligne 1"
    )
    street_address = models.CharField(
        max_length=200,
        verbose_name="Adresse complète",
        blank=True
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="État/Province"
    )
    address_line2 = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Adresse ligne 2"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Code postal"
    )
    
    # Contact
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        verbose_name="Téléphone"
    )
    email = models.EmailField(
        verbose_name="Email"
    )
    
    # Horaires
    hours = models.TextField(
        verbose_name="Horaires d'ouverture",
        help_text="Ex: Lun-Ven: 8h00-18h00, Sam: 9h00-15h00"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    
    # Pour les entrepôts
    is_default_warehouse = models.BooleanField(
        default=False,
        verbose_name="Entrepôt par défaut",
        help_text="Utilisé pour générer l'adresse personnalisée des utilisateurs"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adresses"
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.city}, {self.get_country_display()}"
    
    @property
    def full_address(self):
        """Retourne l'adresse complète formatée"""
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts.append(f"{self.city}")
        if self.postal_code:
            parts.append(self.postal_code)
        parts.append(self.get_country_display())
        return ", ".join(parts)
    
    @property
    def country_flag(self):
        """Retourne l'emoji du drapeau du pays"""
        flags = {
            'US': '🇺🇸',
            'HT': '🇭🇹',
            'CA': '🇨🇦',
            'FR': '🇫🇷'
        }
        return flags.get(self.country, '🌍')
    
    def get_personalized_address(self, user):
        """Génère une adresse personnalisée pour un utilisateur"""
        if self.type != 'warehouse':
            return None
            
        lines = []
        lines.append(f"{user.first_name} {user.last_name}")
        lines.append(self.name)
        lines.append(self.address_line1)
        if self.address_line2:
            lines.append(self.address_line2)
        lines.append(f"{self.city}")
        if self.postal_code:
            lines.append(self.postal_code)
        lines.append(self.get_country_display())
        lines.append(f"Ref: {user.id}")
        
        return "\n".join(lines)


class AddressService(models.Model):
    """Services disponibles dans chaque adresse"""
    
    SERVICE_CHOICES = [
        ('package_reception', 'Réception de colis'),
        ('consolidation', 'Consolidation'),
        ('sea_shipping', 'Expédition maritime'),
        ('air_shipping', 'Expédition aérienne'),
        ('express_shipping', 'Expédition express'),
        ('customer_service', 'Service client'),
        ('package_pickup', 'Retrait de colis'),
        ('payments', 'Paiements'),
        ('technical_support', 'Support technique'),
    ]
    
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name="Adresse"
    )
    service_type = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES,
        verbose_name="Type de service"
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="Disponible"
    )
    additional_info = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Informations supplémentaires"
    )
    
    class Meta:
        verbose_name = "Service d'adresse"
        verbose_name_plural = "Services d'adresse"
        unique_together = ['address', 'service_type']
    
    def __str__(self):
        return f"{self.address.name} - {self.get_service_type_display()}"
    
    @property
    def service_icon(self):
        """Retourne l'icône associée au service"""
        icons = {
            'package_reception': '📦',
            'consolidation': '📋',
            'sea_shipping': '🚢',
            'air_shipping': '✈️',
            'express_shipping': '⚡',
            'customer_service': '👥',
            'package_pickup': '📤',
            'payments': '💳',
            'technical_support': '🔧',
        }
        return icons.get(self.service_type, '📍')
