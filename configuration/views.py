from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.cache import cache
from .models import AppConfiguration, NotificationTemplate, MaintenanceMode
from .serializers import (
    AppConfigurationSerializer, 
    AppConfigurationAdminSerializer,
    NotificationTemplateSerializer,
    MaintenanceModeSerializer
)


class PublicConfigurationView(generics.RetrieveAPIView):
    """
    Endpoint public pour récupérer la configuration de l'app
    Accessible sans authentification
    """
    serializer_class = AppConfigurationSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_object(self):
        # Cache la configuration pour 5 minutes
        config = cache.get('app_config')
        if not config:
            config = AppConfiguration.get_active_config()
            cache.set('app_config', config, 300)  # 5 minutes
        return config


class AdminConfigurationView(generics.RetrieveUpdateAPIView):
    """
    Endpoint admin pour gérer la configuration complète
    Accessible seulement aux admins
    """
    serializer_class = AppConfigurationAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_object(self):
        return AppConfiguration.get_active_config()
    
    def update(self, request, *args, **kwargs):
        # Vider le cache après mise à jour
        cache.delete('app_config')
        return super().update(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def check_maintenance_mode(request):
    """
    Vérifie si l'app est en mode maintenance
    """
    maintenance = MaintenanceMode.objects.first()
    if maintenance and maintenance.is_enabled:
        # Vérifier si l'IP est autorisée
        client_ip = get_client_ip(request)
        allowed_ips = maintenance.allowed_ips.split('\n') if maintenance.allowed_ips else []
        
        if client_ip not in allowed_ips:
            return Response({
                'maintenance_mode': True,
                'message': maintenance.message,
                'estimated_end_time': maintenance.estimated_end_time
            })
    
    return Response({'maintenance_mode': False})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_shipping_rates(request):
    """
    Récupère les tarifs d'expédition actuels
    """
    config = AppConfiguration.get_active_config()
    
    rates = {}
    if config.air_shipping_enabled:
        rates['air'] = float(config.air_shipping_rate_per_kg)
    if config.sea_shipping_enabled:
        rates['sea'] = float(config.sea_shipping_rate_per_kg)
    if config.express_shipping_enabled:
        rates['express'] = float(config.express_shipping_rate_per_kg)
    
    return Response({
        'rates': rates,
        'handling_fee': float(config.handling_fee_per_package),
        'vat_rate': float(config.vat_rate),
        'usd_to_htg_rate': float(config.usd_to_htg_rate)
    })


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def calculate_shipping_cost(request):
    """
    Calcule le coût d'expédition pour un poids donné
    """
    weight = request.data.get('weight', 0)
    shipping_type = request.data.get('shipping_type', 'sea')
    
    config = AppConfiguration.get_active_config()
    
    rate_map = {
        'air': config.air_shipping_rate_per_kg,
        'sea': config.sea_shipping_rate_per_kg,
        'express': config.express_shipping_rate_per_kg,
    }
    
    if shipping_type not in rate_map:
        return Response({'error': 'Type d\'expédition invalide'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    rate = rate_map[shipping_type]
    base_cost = float(weight) * float(rate)
    handling_fee = float(config.handling_fee_per_package)
    vat = base_cost * float(config.vat_rate) / 100
    total_cost = base_cost + handling_fee + vat
    
    return Response({
        'weight': weight,
        'shipping_type': shipping_type,
        'rate_per_kg': float(rate),
        'base_cost': round(base_cost, 2),
        'handling_fee': handling_fee,
        'vat': round(vat, 2),
        'total_cost': round(total_cost, 2)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_notification_templates(request):
    """
    Récupère tous les templates de notification
    """
    templates = NotificationTemplate.objects.filter(is_active=True)
    serializer = NotificationTemplateSerializer(templates, many=True)
    return Response(serializer.data)


def get_client_ip(request):
    """Récupère l'IP réelle du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
