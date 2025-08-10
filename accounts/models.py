from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    USER_ROLES = [
        ('client', 'Client'),
        ('agent_in', 'Agent In'),
        ('agent_out', 'Agent Out'),
        ('admin', 'Administrateur'),
    ]
    
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    address_haiti = models.TextField(blank=True)
    customer_id = models.CharField(
        max_length=10, 
        unique=True, 
        blank=True,
        db_index=True,
        help_text="Identifiant client unique (ex: DJ12AB34)"
    )
    role = models.CharField(
        max_length=20,
        choices=USER_ROLES,
        default='client',
        verbose_name='Rôle utilisateur'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['role', 'first_name']),
            models.Index(fields=['role', 'customer_id']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.customer_id:
            self.customer_id = self.generate_unique_customer_id()
        super().save(*args, **kwargs)
    
    def generate_unique_customer_id(self):
        """Génère un customer_id unique avec initiales"""
        # Générer les initiales à partir du prénom et nom
        initials = ""
        if self.first_name:
            initials += self.first_name[0].upper()
        if self.last_name:
            initials += self.last_name[0].upper()
        
        # Si pas d'initiales, utiliser les deux premières lettres de l'email
        if not initials and self.email:
            initials = self.email[:2].upper()
        
        # Si toujours pas d'initiales, utiliser "BP" (Belpanye)
        if not initials:
            initials = "BP"
        
        # Limiter les initiales à 2 caractères maximum
        initials = initials[:2]
        
        # Essayer de générer un ID unique (max 100 tentatives)
        for attempt in range(100):
            # Générer 6 caractères aléatoires
            random_part = str(uuid.uuid4()).replace('-', '')[:6].upper()
            
            # Combiner initiales + partie aléatoire
            candidate_id = initials + random_part
            
            # Vérifier l'unicité (exclure l'utilisateur actuel si update)
            existing_users = User.objects.filter(customer_id=candidate_id)
            if self.pk:  # Si c'est une mise à jour, exclure cet utilisateur
                existing_users = existing_users.exclude(pk=self.pk)
            
            if not existing_users.exists():
                return candidate_id
        
        # Si après 100 tentatives pas d'unicité, utiliser UUID complet
        # (très improbable mais sécurise le système)
        return str(uuid.uuid4()).replace('-', '')[:8].upper()
    
    @property
    def warehouse_address(self):
        return f"{self.get_full_name()} #{self.customer_id}\n123 NW 21st St\nMiami, FL 33142\nÉtats-Unis"
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    @property
    def is_client(self):
        return self.role == 'client'
    
    @property  
    def is_agent_in(self):
        return self.role == 'agent_in'
    
    @property
    def is_agent_out(self):
        return self.role == 'agent_out'
    
    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_staff

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profil de {self.user.email}"


class PackageVisa(models.Model):
    """Modèle pour donner visa à quelqu'un pour récupérer un colis"""
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='visas_given',
        verbose_name='Client propriétaire'
    )
    delegate_name = models.CharField(
        max_length=100,
        verbose_name='Nom du délégué'
    )
    delegate_phone = models.CharField(
        max_length=20,
        verbose_name='Téléphone du délégué'
    )
    delegate_id_number = models.CharField(
        max_length=50,
        verbose_name='Numéro de pièce d\'identité'
    )
    package_tracking = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Numéro de suivi du colis'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Visa actif'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes additionnelles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Visa de colis'
        verbose_name_plural = 'Visas de colis'
    
    def __str__(self):
        return f"Visa pour {self.delegate_name} - Client: {self.client.email}"
