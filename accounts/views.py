from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.cache import cache
import hashlib
from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserUpdateSerializer
)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Compte créé avec succès'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Connexion réussie'
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except:
        pass
    logout(request)
    return Response({'message': 'Déconnexion réussie'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile_view(request):
    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_clients_view(request):
    """Recherche optimisée de clients pour les agents in"""
    # Vérifier que l'utilisateur est un agent in
    if request.user.role != 'agent_in':
        return Response(
            {'error': 'Seuls les agents de réception peuvent rechercher des clients'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    query = request.GET.get('q', '').strip()
    page = int(request.GET.get('page', 1))
    page_size = min(int(request.GET.get('page_size', 10)), 50)  # Max 50 résultats par page
    
    if not query or len(query) < 2:
        return Response({
            'results': [],
            'count': 0,
            'has_more': False,
            'page': page
        })
    
    # Générer une clé de cache basée sur la requête
    cache_key = f"client_search:{hashlib.md5(f'{query}:{page}:{page_size}'.encode()).hexdigest()}"
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return Response(cached_result)
    
    # Optimiser la requête avec select_related et préfiltrage
    base_queryset = User.objects.filter(role='client').select_related('profile')
    
    # Recherche intelligente : priorité aux correspondances exactes
    exact_matches = base_queryset.filter(
        Q(customer_id__iexact=query) |
        Q(email__iexact=query)
    )
    
    # Recherche partielle si pas de correspondance exacte
    if not exact_matches.exists():
        # Recherche sur tous les champs avec pondération intelligente
        search_query = (
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(customer_id__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query)
        )
        
        partial_matches = base_queryset.filter(search_query)
        
        # Ordonner par pertinence : d'abord les correspondances au début du nom
        partial_matches = partial_matches.extra(
            select={
                'name_match_priority': """
                    CASE 
                        WHEN first_name ILIKE %s THEN 1
                        WHEN last_name ILIKE %s THEN 1
                        WHEN customer_id ILIKE %s THEN 2
                        WHEN email ILIKE %s THEN 3
                        WHEN phone ILIKE %s THEN 4
                        ELSE 5
                    END
                """
            },
            select_params=[f'{query}%', f'{query}%', f'{query}%', f'{query}%', f'{query}%']
        ).order_by('name_match_priority', 'first_name', 'last_name')
    else:
        partial_matches = exact_matches
    
    # Ordonner par pertinence (correspondances exactes d'abord)
    clients_queryset = partial_matches.order_by('first_name', 'last_name')
    
    # Pagination
    paginator = Paginator(clients_queryset, page_size)
    
    try:
        clients_page = paginator.page(page)
    except:
        clients_page = paginator.page(1)
    
    # Sérialiser les résultats
    serializer = UserSerializer(clients_page.object_list, many=True)
    
    result = {
        'results': serializer.data,
        'count': paginator.count,
        'has_more': clients_page.has_next(),
        'page': clients_page.number,
        'total_pages': paginator.num_pages
    }
    
    # Mettre en cache pendant 5 minutes
    cache.set(cache_key, result, 300)
    
    return Response(result)
