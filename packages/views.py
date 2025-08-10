from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Package, PackageConsolidation
from .serializers import (
    PackageSerializer,
    PackageCreateSerializer,
    PackageUpdateSerializer,
    PackageRegistrationSerializer,
    PackageAnnouncementSerializer,
    PackageConsolidationSerializer,
    PackageConsolidationCreateSerializer
)

class PackageListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Package.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PackageCreateSerializer
        return PackageSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PackageDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Package.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PackageUpdateSerializer
        return PackageSerializer

class PackageConsolidationListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PackageConsolidation.objects.filter(user=self.request.user, is_active=True)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PackageConsolidationCreateSerializer
        return PackageConsolidationSerializer

class PackageConsolidationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PackageConsolidationSerializer
    
    def get_queryset(self):
        return PackageConsolidation.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        instance.packages.update(status='received')
        instance.is_active = False
        instance.save()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_package_to_consolidation(request, consolidation_id):
    consolidation = get_object_or_404(
        PackageConsolidation, 
        id=consolidation_id, 
        user=request.user, 
        is_active=True
    )
    
    package_id = request.data.get('package_id')
    if not package_id:
        return Response(
            {'error': 'package_id requis'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    package = get_object_or_404(
        Package, 
        id=package_id, 
        user=request.user, 
        status='received'
    )
    
    consolidation.packages.add(package)
    package.status = 'waiting'
    package.save()
    
    consolidation.calculate_totals()
    
    return Response({
        'message': 'Colis ajouté à la consolidation',
        'consolidation': PackageConsolidationSerializer(consolidation).data
    })

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_package_from_consolidation(request, consolidation_id, package_id):
    consolidation = get_object_or_404(
        PackageConsolidation, 
        id=consolidation_id, 
        user=request.user, 
        is_active=True
    )
    
    package = get_object_or_404(
        Package, 
        id=package_id, 
        user=request.user
    )
    
    if package in consolidation.packages.all():
        consolidation.packages.remove(package)
        package.status = 'received'
        package.save()
        
        consolidation.calculate_totals()
        
        if consolidation.packages.count() < 2:
            consolidation.packages.update(status='received')
            consolidation.is_active = False
            consolidation.save()
            return Response({
                'message': 'Consolidation supprimée (moins de 2 colis)'
            })
        
        return Response({
            'message': 'Colis retiré de la consolidation',
            'consolidation': PackageConsolidationSerializer(consolidation).data
        })
    
    return Response(
        {'error': 'Ce colis ne fait pas partie de cette consolidation'},
        status=status.HTTP_400_BAD_REQUEST
    )

# Vues pour les agents in - enregistrement de colis
class PackageRegistrationView(generics.CreateAPIView):
    """Vue pour que les agents in enregistrent des colis"""
    serializer_class = PackageRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Vérifier que l'utilisateur est un agent in
        if self.request.user.role != 'agent_in':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seuls les agents de réception peuvent enregistrer des colis.")
        
        serializer.save()


class AnnouncedPackagesListView(generics.ListAPIView):
    """Liste des colis annoncés par les clients (pour les agents in)"""
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Vérifier que l'utilisateur est un agent in
        if self.request.user.role != 'agent_in':
            return Package.objects.none()
        
        return Package.objects.filter(status='announced').order_by('-announced_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_announced_package(request, package_id):
    """Traiter un colis annoncé par un client (agent in)"""
    if request.user.role != 'agent_in':
        return Response(
            {'error': 'Seuls les agents de réception peuvent traiter les colis annoncés'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    package = get_object_or_404(Package, id=package_id, status='announced')
    
    # Mettre à jour le colis avec les nouvelles informations
    serializer = PackageRegistrationSerializer(
        instance=package, 
        data=request.data, 
        context={'request': request},
        partial=True
    )
    
    if serializer.is_valid():
        from django.utils import timezone
        
        # Mettre à jour le statut et l'agent
        package.status = 'received'
        package.received_at = timezone.now()
        package.agent_in = request.user
        
        # Mettre à jour les autres champs
        for field, value in serializer.validated_data.items():
            if field != 'client_email':  # Ignore client_email car déjà défini
                setattr(package, field, value)
        
        package.save()
        
        return Response({
            'message': 'Colis traité avec succès',
            'package': PackageSerializer(package).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Vue pour l'annonce de colis par les clients
class PackageAnnouncementView(generics.CreateAPIView):
    """Vue pour que les clients annoncent l'arrivée d'un colis"""
    serializer_class = PackageAnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Vérifier que l'utilisateur est un client
        if self.request.user.role != 'client':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seuls les clients peuvent annoncer des colis.")
        
        serializer.save()


# Vues pour les agents in - gestion de tous les colis
class AgentInPackageListView(generics.ListAPIView):
    """Vue pour que les agents in voient tous les colis"""
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Vérifier que l'utilisateur est un agent in
        if self.request.user.role != 'agent_in':
            return Package.objects.none()
        
        # Retourner tous les colis, triés par date de réception
        return Package.objects.all().select_related('user', 'agent_in').order_by('-received_at', '-announced_at')


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_package_status(request, package_id):
    """Mettre à jour le statut d'un colis (agent in)"""
    if request.user.role != 'agent_in':
        return Response(
            {'error': 'Seuls les agents de réception peuvent modifier le statut des colis'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    package = get_object_or_404(Package, id=package_id)
    
    new_status = request.data.get('status')
    if not new_status:
        return Response(
            {'error': 'Le champ status est requis'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier que le statut est valide
    valid_statuses = [choice[0] for choice in Package.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return Response(
            {'error': f'Statut invalide. Statuts valides: {valid_statuses}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Mettre à jour le statut
    old_status = package.status
    package.status = new_status
    
    # Mettre à jour les timestamps selon le statut
    from django.utils import timezone
    if new_status == 'received' and old_status != 'received':
        package.received_at = timezone.now()
        package.agent_in = request.user
    
    # Ajouter une note si fournie
    notes = request.data.get('notes', '')
    if notes:
        if package.notes:
            package.notes += f"\n[{timezone.now().strftime('%Y-%m-%d %H:%M')} - {request.user.get_full_name()}]: {notes}"
        else:
            package.notes = f"[{timezone.now().strftime('%Y-%m-%d %H:%M')} - {request.user.get_full_name()}]: {notes}"
    
    package.save()
    
    return Response({
        'message': f'Statut du colis mis à jour de "{old_status}" vers "{new_status}"',
        'package': PackageSerializer(package).data
    })


# Vues admin pour la gestion des colis
class AdminPackageListView(generics.ListAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminPackageDetailView(generics.RetrieveUpdateAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
