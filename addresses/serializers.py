from rest_framework import serializers
from .models import Address, AddressService


class AddressServiceSerializer(serializers.ModelSerializer):
    service_display = serializers.CharField(source='get_service_type_display', read_only=True)
    service_icon = serializers.CharField(read_only=True)
    
    class Meta:
        model = AddressService
        fields = [
            'id', 'service_type', 'service_display', 'service_icon',
            'is_available', 'additional_info'
        ]


class AddressSerializer(serializers.ModelSerializer):
    services = AddressServiceSerializer(many=True, read_only=True)
    country_display = serializers.CharField(source='get_country_display', read_only=True)
    country_flag = serializers.CharField(read_only=True)
    full_address = serializers.CharField(read_only=True)
    personalized_address = serializers.SerializerMethodField()
    
    class Meta:
        model = Address
        fields = [
            'id', 'type', 'name', 'country', 'country_display', 'country_flag',
            'city', 'address_line1', 'address_line2', 'postal_code',
            'phone', 'email', 'hours', 'full_address', 'personalized_address',
            'is_active', 'is_default_warehouse', 'display_order',
            'services'
        ]
    
    def get_personalized_address(self, obj):
        """Retourne l'adresse personnalisée pour l'utilisateur connecté"""
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return obj.get_personalized_address(request.user)
        return None


class AddressWriteSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier les adresses"""
    services = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Address
        fields = [
            'id', 'type', 'name', 'country', 'city', 'street_address',
            'state', 'postal_code', 'phone', 'email', 'hours', 
            'is_active', 'is_default_warehouse', 'services'
        ]
    
    def create(self, validated_data):
        services_data = validated_data.pop('services', [])
        address = Address.objects.create(**validated_data)
        
        # Créer les services associés
        for service_type in services_data:
            AddressService.objects.create(
                address=address,
                service_type=service_type,
                is_available=True
            )
        
        return address
    
    def update(self, instance, validated_data):
        services_data = validated_data.pop('services', None)
        
        # Mettre à jour l'adresse
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mettre à jour les services si fournis
        if services_data is not None:
            # Supprimer les anciens services
            instance.services.all().delete()
            
            # Créer les nouveaux services
            for service_type in services_data:
                AddressService.objects.create(
                    address=instance,
                    service_type=service_type,
                    is_available=True
                )
        
        return instance