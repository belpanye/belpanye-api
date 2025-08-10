#!/usr/bin/env python3
"""
Script pour créer des utilisateurs de test
"""

import os
import sys
import django


sys.path.append('/Users/davidjeudy/belpanye/belpanye_backend')

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User

def create_test_users():
    """Créer des utilisateurs de test"""
    

    User.objects.all().delete()
    
    users_data = [
        {
            'email': 'client@example.com',
            'username': 'client_example',
            'first_name': 'Client',
            'last_name': 'Example',
            'phone': '123-456-7890',
            'role': 'client',
            'password': 'password123'
        },
        {
            'email': 'marie.dupont@test.com',
            'username': 'marie_dupont',
            'first_name': 'Marie',
            'last_name': 'Dupont',
            'phone': '234-567-8901',
            'role': 'client',
            'password': 'password123'
        },
        {
            'email': 'jean.martin@test.com',
            'username': 'jean_martin',
            'first_name': 'Jean',
            'last_name': 'Martin',
            'phone': '345-678-9012',
            'role': 'client',
            'password': 'password123'
        },
        {
            'email': 'pierre.bernard@test.com',
            'username': 'pierre_bernard',
            'first_name': 'Pierre',
            'last_name': 'Bernard',
            'phone': '456-789-0123',
            'role': 'client',
            'password': 'password123'
        },
        {
            'email': 'sophie.wilson@test.com',
            'username': 'sophie_wilson',
            'first_name': 'Sophie',
            'last_name': 'Wilson',
            'phone': '567-890-1234',
            'role': 'client',
            'password': 'password123'
        },
        {
            'email': 'agent@test.com',
            'username': 'agent_in',
            'first_name': 'Agent',
            'last_name': 'Reception',
            'phone': '678-901-2345',
            'role': 'agent_in',
            'password': 'password123'
        },
        {
            'email': 'admin@test.com',
            'username': 'admin',
            'first_name': 'Admin',
            'last_name': 'System',
            'phone': '789-012-3456',
            'role': 'admin',
            'password': 'password123',
            'is_staff': True,
            'is_superuser': True
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        try:
            user = User.objects.create_user(
                email=user_data['email'],
                username=user_data['username'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone=user_data['phone'],
                role=user_data['role'],
                password=user_data['password'],
                is_staff=user_data.get('is_staff', False),
                is_superuser=user_data.get('is_superuser', False)
            )
            created_users.append(user)
            print(f"✓ Utilisateur créé: {user.email} ({user.get_role_display()}) - ID: {user.customer_id}")
        except Exception as e:
            print(f"✗ Erreur lors de la création de {user_data['email']}: {e}")
    
    print(f"\n{len(created_users)} utilisateurs créés avec succès!")
    
    # Afficher les clients pour tester la recherche
    clients = User.objects.filter(role='client')
    print(f"\nClients créés ({clients.count()}):")
    for client in clients:
        print(f"  - {client.first_name} {client.last_name} ({client.email}) - ID: {client.customer_id}")

if __name__ == "__main__":
    create_test_users()