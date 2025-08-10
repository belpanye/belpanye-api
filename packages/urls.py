from django.urls import path
from . import views

app_name = 'packages'

urlpatterns = [
    # Gestion des colis
    path('', views.PackageListCreateView.as_view(), name='package_list_create'),
    path('<uuid:pk>/', views.PackageDetailView.as_view(), name='package_detail'),
    
    # Agent In - Enregistrement de colis
    path('register/', views.PackageRegistrationView.as_view(), name='package_registration'),
    path('announced/', views.AnnouncedPackagesListView.as_view(), name='announced_packages'),
    path('announced/<uuid:package_id>/process/', views.process_announced_package, name='process_announced_package'),
    
    # Agent In - Gestion de tous les colis
    path('agent-in/all/', views.AgentInPackageListView.as_view(), name='agent_in_packages'),
    path('<uuid:package_id>/update-status/', views.update_package_status, name='update_package_status'),
    
    # Client - Annonce de colis
    path('announce/', views.PackageAnnouncementView.as_view(), name='package_announcement'),
    
    # Consolidations
    path('consolidations/', views.PackageConsolidationListCreateView.as_view(), name='consolidation_list_create'),
    path('consolidations/<uuid:pk>/', views.PackageConsolidationDetailView.as_view(), name='consolidation_detail'),
    path('consolidations/<uuid:consolidation_id>/add-package/', views.add_package_to_consolidation, name='add_package_to_consolidation'),
    path('consolidations/<uuid:consolidation_id>/remove-package/<uuid:package_id>/', views.remove_package_from_consolidation, name='remove_package_from_consolidation'),
    
    # Admin endpoints
    path('admin/', views.AdminPackageListView.as_view(), name='admin_package_list'),
    path('admin/<uuid:pk>/', views.AdminPackageDetailView.as_view(), name='admin_package_detail'),
]