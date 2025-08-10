from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentification
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profil utilisateur
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile_view, name='update_profile'),
    
    # Recherche clients (pour agents in)
    path('clients/search/', views.search_clients_view, name='search_clients'),
    
    # Admin endpoints
    path('admin/users/', views.UserListView.as_view(), name='admin_user_list'),
    path('admin/users/<int:pk>/', views.UserDetailView.as_view(), name='admin_user_detail'),
]