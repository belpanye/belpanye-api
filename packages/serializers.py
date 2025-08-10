from rest_framework import serializers
from .models import Package, PackageConsolidation
from accounts.serializers import UserSerializer

class PackageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    agent_in = UserSerializer(read_only=True)
    volume = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    fragility_display = serializers.CharField(source='get_fragility_display', read_only=True)
    shipping_mode_display = serializers.CharField(source='get_shipping_mode_display', read_only=True)
    
    class Meta:
        model = Package
        fields = ('id', 'user', 'agent_in', 'tracking_number', 'sender', 'description', 
                 'weight', 'length', 'width', 'height', 'value', 'photo',
                 'status', 'status_display', 'fragility', 'fragility_display',
                 'shipping_mode', 'shipping_mode_display', 'destination',
                 'announced_at', 'received_at', 'notes', 'volume')
        read_only_fields = ('tracking_number', 'announced_at', 'received_at')

class PackageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ('sender', 'description', 'weight', 'length', 'width', 
                 'height', 'value', 'photo', 'notes')

class PackageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ('status', 'notes')


class PackageRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'enregistrement de colis par les agents in"""
    client_email = serializers.EmailField(write_only=True)
    
    class Meta:
        model = Package
        fields = ('client_email', 'sender', 'description', 'weight', 'length', 
                 'width', 'height', 'value', 'photo', 'fragility', 
                 'shipping_mode', 'destination', 'notes')
    
    def validate_client_email(self, value):
        """Vérifier que le client existe"""
        from accounts.models import User
        try:
            client = User.objects.get(email=value, role='client')
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Client non trouvé avec cet email.")
    
    def create(self, validated_data):
        from accounts.models import User
        from django.utils import timezone
        
        client_email = validated_data.pop('client_email')
        client = User.objects.get(email=client_email, role='client')
        agent_in = self.context['request'].user
        
        # Créer le colis avec statut "received" (reçu à l'entrepôt)
        package = Package.objects.create(
            user=client,
            agent_in=agent_in,
            status='received',
            received_at=timezone.now(),
            **validated_data
        )
        
        return package


class PackageAnnouncementSerializer(serializers.ModelSerializer):
    """Serializer pour l'annonce de colis par les clients"""
    
    class Meta:
        model = Package
        fields = ('sender', 'description', 'destination', 'notes')
    
    def create(self, validated_data):
        from django.utils import timezone
        
        client = self.context['request'].user
        
        # Créer le colis avec statut "announced" (annoncé par le client)
        package = Package.objects.create(
            user=client,
            status='announced',
            announced_at=timezone.now(),
            **validated_data
        )
        
        return package

class PackageConsolidationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    packages = PackageSerializer(many=True, read_only=True)
    package_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PackageConsolidation
        fields = ('id', 'user', 'packages', 'consolidation_number',
                 'total_weight', 'total_value', 'created_at', 'is_active',
                 'package_count')
        read_only_fields = ('consolidation_number', 'total_weight', 'total_value', 'created_at')
    
    def get_package_count(self, obj):
        return obj.packages.count()

class PackageConsolidationCreateSerializer(serializers.ModelSerializer):
    package_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    
    class Meta:
        model = PackageConsolidation
        fields = ('package_ids',)
    
    def validate_package_ids(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Il faut au moins 2 colis pour créer une consolidation.")
        
        user = self.context['request'].user
        packages = Package.objects.filter(
            id__in=value,
            user=user,
            status='received'
        )
        
        if packages.count() != len(value):
            raise serializers.ValidationError("Certains colis ne sont pas valides ou ne vous appartiennent pas.")
        
        return value
    
    def create(self, validated_data):
        package_ids = validated_data.pop('package_ids')
        user = self.context['request'].user
        
        consolidation = PackageConsolidation.objects.create(user=user)
        packages = Package.objects.filter(id__in=package_ids, user=user)
        
        consolidation.packages.set(packages)
        consolidation.calculate_totals()
        
        packages.update(status='waiting')
        
        return consolidation