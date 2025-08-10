from rest_framework import serializers
from .models import ShippingRate, Shipment, Payment
from packages.models import Package, PackageConsolidation

class ShippingRateSerializer(serializers.ModelSerializer):
    shipping_type_display = serializers.CharField(source='get_shipping_type_display', read_only=True)
    
    class Meta:
        model = ShippingRate
        fields = ('id', 'shipping_type', 'shipping_type_display', 'min_weight', 
                 'max_weight', 'price_per_kg', 'delivery_days', 'is_active')

class ShipmentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    shipping_type_display = serializers.CharField(source='get_shipping_type_display', read_only=True)
    
    class Meta:
        model = Shipment
        fields = ('id', 'user', 'shipment_number',
                 'shipping_type', 'shipping_type_display', 'total_weight', 
                 'shipping_cost', 'insurance_cost', 'total_cost',
                 'delivery_address', 'recipient_name', 'recipient_phone',
                 'status', 'status_display', 'tracking_number_haiti',
                 'created_at', 'paid_at', 'shipped_at', 'delivered_at', 'notes')
        read_only_fields = ('shipment_number', 'shipping_cost', 'total_cost', 
                           'created_at', 'paid_at', 'shipped_at', 'delivered_at')

class ShipmentCreateSerializer(serializers.ModelSerializer):
    package_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    consolidation_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Shipment
        fields = ('package_ids', 'consolidation_id', 'shipping_type', 
                 'insurance_cost', 'delivery_address', 'recipient_name', 
                 'recipient_phone', 'notes')
    
    def validate(self, attrs):
        package_ids = attrs.get('package_ids')
        consolidation_id = attrs.get('consolidation_id')
        
        if not package_ids and not consolidation_id:
            raise serializers.ValidationError("Vous devez spécifier des colis ou une consolidation.")
        
        if package_ids and consolidation_id:
            raise serializers.ValidationError("Vous ne pouvez pas spécifier à la fois des colis et une consolidation.")
        
        return attrs
    
    def validate_package_ids(self, value):
        if value:
            user = self.context['request'].user
            packages = Package.objects.filter(
                id__in=value,
                user=user,
                status__in=['received', 'ready']
            )
            
            if packages.count() != len(value):
                raise serializers.ValidationError("Certains colis ne sont pas valides.")
        
        return value
    
    def validate_consolidation_id(self, value):
        if value:
            user = self.context['request'].user
            try:
                consolidation = PackageConsolidation.objects.get(
                    id=value,
                    user=user,
                    is_active=True
                )
            except PackageConsolidation.DoesNotExist:
                raise serializers.ValidationError("Consolidation invalide.")
        
        return value
    
    def create(self, validated_data):
        package_ids = validated_data.pop('package_ids', None)
        consolidation_id = validated_data.pop('consolidation_id', None)
        user = self.context['request'].user
        
        shipment = Shipment.objects.create(user=user, **validated_data)
        
        if package_ids:
            packages = Package.objects.filter(id__in=package_ids, user=user)
            shipment.packages.set(packages)
            shipment.total_weight = sum(p.weight for p in packages)
        
        if consolidation_id:
            consolidation = PackageConsolidation.objects.get(id=consolidation_id, user=user)
            shipment.consolidation = consolidation
            shipment.total_weight = consolidation.total_weight
        
        shipment.calculate_shipping_cost()
        return shipment

class ShipmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ('status', 'tracking_number_haiti', 'notes')

class PaymentSerializer(serializers.ModelSerializer):
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = ('id', 'shipment', 'payment_method', 'payment_method_display',
                 'amount', 'status', 'status_display', 'transaction_id',
                 'payment_reference', 'created_at', 'completed_at')
        read_only_fields = ('created_at', 'completed_at')

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('payment_method', 'payment_reference')
    
    def create(self, validated_data):
        shipment = self.context['shipment']
        validated_data['amount'] = shipment.total_cost
        return Payment.objects.create(shipment=shipment, **validated_data)