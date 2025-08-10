from django.urls import path
from . import views

app_name = 'configuration'

urlpatterns = [
    # Configuration publique
    path('public/', views.PublicConfigurationView.as_view(), name='public-config'),
    
    # Configuration admin
    path('admin/', views.AdminConfigurationView.as_view(), name='admin-config'),
    
    # Maintenance
    path('maintenance/', views.check_maintenance_mode, name='maintenance-check'),
    
    # Tarifs d'expédition
    path('shipping-rates/', views.get_shipping_rates, name='shipping-rates'),
    path('calculate-shipping/', views.calculate_shipping_cost, name='calculate-shipping'),
    
    # Templates de notification
    path('notification-templates/', views.get_notification_templates, name='notification-templates'),
]