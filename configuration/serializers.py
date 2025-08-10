from rest_framework import serializers
from .models import AppConfiguration, NotificationTemplate, MaintenanceMode


class AppConfigurationSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la configuration publique
    Exclut les informations sensibles
    """
    class Meta:
        model = AppConfiguration
        fields = [
            'company_name',
            'logo',
            'favicon', 
            'primary_color',
            'font_family',
            'facebook_url',
            'instagram_url',
            'whatsapp_number',
            'twitter_url',
            'stripe_enabled',
            'paypal_enabled',
            'moncash_enabled',
            'usd_to_htg_rate',
            'vat_rate',
            'handling_fee_per_package',
            'consolidation_enabled',
            'free_storage_days',
            'public_tracking_enabled',
            'air_shipping_enabled',
            'sea_shipping_enabled',
            'express_shipping_enabled',
            'air_shipping_rate_per_kg',
            'sea_shipping_rate_per_kg',
            'express_shipping_rate_per_kg',
            'allowed_delivery_countries',
            'available_languages',
            'welcome_message_fr',
            'welcome_message_en',
            'privacy_policy',
            'terms_of_service',
            'max_packages_per_user',
            'max_package_weight_kg',
            'two_factor_auth_enabled',
        ]


class AppConfigurationAdminSerializer(serializers.ModelSerializer):
    """
    Sérialiseur complet pour l'admin (inclut les clés API)
    """
    class Meta:
        model = AppConfiguration
        fields = '__all__'


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = '__all__'


class MaintenanceModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceMode
        fields = '__all__'