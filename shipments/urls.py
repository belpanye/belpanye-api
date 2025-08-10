from django.urls import path
from . import views

app_name = 'shipments'

urlpatterns = [
    # Tarifs d'expédition
    path('rates/', views.ShippingRateListView.as_view(), name='shipping_rates'),
    path('calculate-cost/', views.calculate_shipping_cost, name='calculate_shipping_cost'),
    
    # Expéditions
    path('', views.ShipmentListCreateView.as_view(), name='shipment_list_create'),
    path('<uuid:pk>/', views.ShipmentDetailView.as_view(), name='shipment_detail'),
    
    # Paiements
    path('<uuid:shipment_id>/payments/', views.create_payment, name='create_payment'),
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/<uuid:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/<uuid:payment_id>/confirm/', views.confirm_payment, name='confirm_payment'),
    
    # Admin endpoints
    path('admin/', views.AdminShipmentListView.as_view(), name='admin_shipment_list'),
    path('admin/<uuid:pk>/', views.AdminShipmentDetailView.as_view(), name='admin_shipment_detail'),
    path('admin/rates/', views.AdminShippingRateListCreateView.as_view(), name='admin_rate_list_create'),
    path('admin/rates/<int:pk>/', views.AdminShippingRateDetailView.as_view(), name='admin_rate_detail'),
]