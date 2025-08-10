from django.urls import path
from .views import (
    AddressListView, WarehouseListView, OfficeListView,
    AddressCreateView, AddressUpdateView, AddressDeleteView
)

urlpatterns = [
    path('', AddressListView.as_view(), name='address-list'),
    path('create/', AddressCreateView.as_view(), name='address-create'),
    path('<int:pk>/', AddressUpdateView.as_view(), name='address-update'),
    path('<int:pk>/delete/', AddressDeleteView.as_view(), name='address-delete'),
    path('warehouses/', WarehouseListView.as_view(), name='warehouse-list'),
    path('offices/', OfficeListView.as_view(), name='office-list'),
]