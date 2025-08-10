from django.db import models
from django.conf import settings
import uuid

class Package(models.Model):
    STATUS_CHOICES = [
        ('announced', 'Announced'),
        ('received', 'Reçeived'),
        ('inTransit', 'In-Transit'),
        ('available', 'Available'),
        ('delivered', 'Livré'),
    ]
    
    FRAGILITY_CHOICES = [
        ('normal', 'Normal'),
        ('fragile', 'Fragile'),
        ('very_fragile', 'Very fragile'),
    ]
    
    SHIPPING_MODE_CHOICES = [
        ('plane', 'Plane'),
        ('boat', 'Boat'),
        ('express', 'Express'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='packages')
    tracking_number = models.CharField(max_length=100, unique=True, blank=True)
    sender = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    weight = models.DecimalField(max_digits=6, decimal_places=2, help_text="Poids en lbs")
    length = models.DecimalField(max_digits=6, decimal_places=2, help_text="Longueur en cm")
    width = models.DecimalField(max_digits=6, decimal_places=2, help_text="Largeur en cm")
    height = models.DecimalField(max_digits=6, decimal_places=2, help_text="Hauteur en cm")
    value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valeur déclarée en USD")
    photo = models.ImageField(upload_to='packages/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='announced')
    fragility = models.CharField(
        max_length=20, 
        choices=FRAGILITY_CHOICES, 
        default='normal',
        verbose_name='Fragilité'
    )
    shipping_mode = models.CharField(
        max_length=20,
        choices=SHIPPING_MODE_CHOICES,
        default='normal',
        verbose_name='Mode d\'expédition'
    )
    destination = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Destination'
    )
    announced_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    agent_in = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='packages_registered',
        verbose_name='Agent de réception'
    )
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = f"BP{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def volume(self):
        return (self.length * self.width * self.height) / 1000
    
    def __str__(self):
        return f"{self.tracking_number} - {self.user.email}"
    
    class Meta:
        ordering = ['-received_at']

class PackageConsolidation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    packages = models.ManyToManyField(Package, related_name='consolidations')
    consolidation_number = models.CharField(max_length=100, unique=True, blank=True)
    total_weight = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.consolidation_number:
            self.consolidation_number = f"CONS{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        packages = self.packages.all()
        self.total_weight = sum(p.weight for p in packages)
        self.total_value = sum(p.value for p in packages)
        self.save()
    
    def __str__(self):
        return f"Consolidation {self.consolidation_number} - {self.user.email}"


class PackageDelivery(models.Model):
    """Modèle pour gérer les livraisons et signatures"""
    package = models.OneToOneField(
        Package,
        on_delete=models.CASCADE,
        related_name='delivery'
    )
    agent_out = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deliveries_made',
        verbose_name='Agent de livraison'
    )
    recipient_name = models.CharField(
        max_length=100,
        verbose_name='Nom du destinataire'
    )
    recipient_id = models.CharField(
        max_length=50,
        verbose_name='Pièce d\'identité du destinataire'
    )
    signature = models.TextField(
        blank=True,
        verbose_name='Signature (base64)'
    )
    delivery_photo = models.ImageField(
        upload_to='deliveries/',
        blank=True,
        null=True,
        verbose_name='Photo de livraison'
    )
    delivered_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(
        blank=True,
        verbose_name='Notes de livraison'
    )
    
    class Meta:
        verbose_name = 'Livraison'
        verbose_name_plural = 'Livraisons'
    
    def __str__(self):
        return f"Livraison {self.package.tracking_number} à {self.recipient_name}"


class PackagePayment(models.Model):
    """Modèle pour gérer les paiements des colis"""
    PAYMENT_METHODS = [
        ('moncash', 'MonCash'),
        ('bank_transfer', 'Virement bancaire'),
        ('spih', 'SPIH'),
        ('credit_card', 'Carte de crédit'),
        ('cash', 'Espèces'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]
    
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Montant'
    )
    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name='Méthode de paiement'
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending',
        verbose_name='Statut du paiement'
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID de transaction'
    )
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Référence de paiement'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
    
    def __str__(self):
        return f"Paiement {self.package.tracking_number} - {self.get_method_display()}"
