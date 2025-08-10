from django.db import models
from django.conf import settings
from packages.models import Package, PackageConsolidation
import uuid

class ShippingRate(models.Model):
    SHIPPING_TYPE_CHOICES = [
        ('air', 'Aérien'),
        ('sea', 'Maritime'),
    ]
    
    shipping_type = models.CharField(max_length=10, choices=SHIPPING_TYPE_CHOICES)
    min_weight = models.DecimalField(max_digits=6, decimal_places=2)
    max_weight = models.DecimalField(max_digits=6, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_days = models.IntegerField(help_text="Nombre de jours de livraison estimé")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_shipping_type_display()} - {self.min_weight}kg à {self.max_weight}kg"
    
    class Meta:
        ordering = ['shipping_type', 'min_weight']

class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente de paiement'),
        ('paid', 'Payé'),
        ('processing', 'En traitement'),
        ('shipped', 'Expédié'),
        ('in_transit', 'En transit'),
        ('delivered', 'Livré'),
        ('cancelled', 'Annulé'),
    ]
    
    SHIPPING_TYPE_CHOICES = [
        ('air', 'Aérien'),
        ('sea', 'Maritime'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shipments')
    shipment_number = models.CharField(max_length=100, unique=True, blank=True)
    packages = models.ManyToManyField(Package, related_name='shipments', blank=True)
    consolidation = models.ForeignKey(PackageConsolidation, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipments')
    
    shipping_type = models.CharField(max_length=10, choices=SHIPPING_TYPE_CHOICES)
    total_weight = models.DecimalField(max_digits=8, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    delivery_address = models.TextField()
    recipient_name = models.CharField(max_length=200)
    recipient_phone = models.CharField(max_length=20)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tracking_number_haiti = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.shipment_number:
            self.shipment_number = f"SH{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    def calculate_shipping_cost(self):
        try:
            rate = ShippingRate.objects.filter(
                shipping_type=self.shipping_type,
                min_weight__lte=self.total_weight,
                max_weight__gte=self.total_weight,
                is_active=True
            ).first()
            
            if rate:
                self.shipping_cost = rate.price_per_kg * self.total_weight
                self.total_cost = self.shipping_cost + self.insurance_cost
                self.save()
                return self.shipping_cost
        except:
            pass
        return 0
    
    def __str__(self):
        return f"{self.shipment_number} - {self.user.email}"
    
    class Meta:
        ordering = ['-created_at']

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Carte de crédit'),
        ('paypal', 'PayPal'),
        ('moncash', 'MonCash'),
        ('bank_transfer', 'Virement bancaire'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=200, blank=True)
    payment_reference = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Paiement {self.id} - {self.shipment.shipment_number}"
