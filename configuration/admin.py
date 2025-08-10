from django.contrib import admin
from django.utils.html import format_html
from .models import AppConfiguration, NotificationTemplate, MaintenanceMode


@admin.register(AppConfiguration)
class AppConfigurationAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'is_active', 'updated_at', 'config_status')
    list_filter = ('is_active', 'stripe_enabled', 'consolidation_enabled')
    search_fields = ('company_name',)
    
    # Organisation des champs en sections
    fieldsets = (
        ('🎨 Branding & Interface', {
            'fields': (
                'company_name', 
                'logo', 'favicon', 
                'primary_color', 
                'font_family'
            ),
        }),
        ('📱 Réseaux Sociaux', {
            'fields': ('facebook_url', 'instagram_url', 'whatsapp_number', 'twitter_url'),
            'classes': ('collapse',),
        }),
        ('💳 Paiement', {
            'fields': (
                ('stripe_enabled', 'paypal_enabled', 'moncash_enabled'),
                'stripe_publishable_key',
                'paypal_client_id', 
                'moncash_client_id',
                ('usd_to_htg_rate', 'vat_rate', 'handling_fee_per_package'),
            ),
        }),
        ('📧 Notifications', {
            'fields': (
                ('email_notifications_enabled', 'sms_notifications_enabled', 'whatsapp_notifications_enabled'),
                ('smtp_host', 'smtp_port', 'smtp_username', 'smtp_use_tls'),
                ('notify_on_package_received', 'notify_on_shipment_created'),
                ('notify_on_shipment_shipped', 'notify_on_shipment_delivered'),
            ),
            'classes': ('collapse',),
        }),
        ('🚚 Services & Activités', {
            'fields': (
                ('consolidation_enabled', 'free_storage_days', 'public_tracking_enabled'),
                ('air_shipping_enabled', 'sea_shipping_enabled', 'express_shipping_enabled'),
                ('air_shipping_rate_per_kg', 'sea_shipping_rate_per_kg', 'express_shipping_rate_per_kg'),
                'allowed_delivery_countries',
            ),
        }),
        ('🌍 Localisation & Contenu', {
            'fields': (
                'available_languages',
                'welcome_message_fr', 'welcome_message_en',
                'privacy_policy', 'terms_of_service',
            ),
            'classes': ('collapse',),
        }),
        ('👥 Utilisateurs & Sécurité', {
            'fields': (
                ('email_verification_required', 'manual_account_approval'),
                ('max_packages_per_user', 'max_package_weight_kg'),
                'two_factor_auth_enabled',
                'blocked_countries',
            ),
            'classes': ('collapse',),
        }),
        ('📊 Statistiques & Rapports', {
            'fields': (
                'default_report_period',
                ('auto_export_reports', 'client_report_access'),
            ),
            'classes': ('collapse',),
        }),
        ('⚙️ Métadonnées', {
            'fields': ('is_active',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def config_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✅ Active</span>')
        return format_html('<span style="color: red;">❌ Inactive</span>')
    config_status.short_description = 'Statut'
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression de la configuration active
        if obj and obj.is_active:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_name_display', 'is_active', 'updated_at')
    list_filter = ('is_active', 'name')
    search_fields = ('name', 'email_subject')
    
    fieldsets = (
        ('📧 Configuration Email', {
            'fields': ('name', 'email_subject', 'email_body'),
        }),
        ('📱 Configuration SMS/WhatsApp', {
            'fields': ('sms_body',),
        }),
        ('📝 Informations', {
            'fields': ('available_variables', 'is_active'),
        }),
    )
    
    readonly_fields = ('available_variables', 'created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        # Définir les variables disponibles selon le type de template
        variables_map = {
            'package_received': '{user_name}, {package_number}, {tracking_number}, {weight}',
            'shipment_created': '{user_name}, {shipment_number}, {total_cost}, {delivery_address}',
            'shipment_shipped': '{user_name}, {shipment_number}, {tracking_number}',
            'shipment_delivered': '{user_name}, {shipment_number}, {delivery_date}',
            'payment_received': '{user_name}, {amount}, {payment_method}',
            'account_created': '{user_name}, {warehouse_address}',
        }
        obj.available_variables = variables_map.get(obj.name, '')
        super().save_model(request, obj, form, change)


@admin.register(MaintenanceMode)
class MaintenanceModeAdmin(admin.ModelAdmin):
    list_display = ('maintenance_status', 'estimated_end_time', 'updated_at')
    
    fieldsets = (
        ('🔧 Configuration Maintenance', {
            'fields': ('is_enabled', 'message', 'estimated_end_time'),
        }),
        ('🔒 Accès Autorisé', {
            'fields': ('allowed_ips',),
        }),
    )
    
    def maintenance_status(self, obj):
        if obj.is_enabled:
            return format_html('<span style="color: orange;">🔧 Maintenance Active</span>')
        return format_html('<span style="color: green;">✅ Service Normal</span>')
    maintenance_status.short_description = 'Statut'
    
    def has_add_permission(self, request):
        # Une seule instance de maintenance
        return not MaintenanceMode.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False  # Ne pas supprimer le mode maintenance


# Personnalisation de l'admin
admin.site.site_header = "🇭🇹 Administration Belpanye"
admin.site.site_title = "Belpanye Admin"
admin.site.index_title = "Panel d'Administration"
