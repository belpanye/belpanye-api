from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Address
from .serializers import AddressSerializer, AddressWriteSerializer


class AddressListView(generics.ListAPIView):
    """
    Vue pour lister toutes les adresses actives
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(is_active=True).prefetch_related('services')


class WarehouseListView(generics.ListAPIView):
    """
    Vue pour lister uniquement les entrepôts
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(
            type='warehouse', 
            is_active=True
        ).prefetch_related('services')


class OfficeListView(generics.ListAPIView):
    """
    Vue pour lister uniquement les bureaux
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(
            type='office', 
            is_active=True
        ).prefetch_related('services')


class AddressCreateView(generics.CreateAPIView):
    """
    Vue pour créer une nouvelle adresse (admin seulement)
    """
    serializer_class = AddressWriteSerializer
    permission_classes = [IsAdminUser]
    queryset = Address.objects.all()


class AddressUpdateView(generics.UpdateAPIView):
    """
    Vue pour modifier une adresse (admin seulement)
    """
    serializer_class = AddressWriteSerializer
    permission_classes = [IsAdminUser]
    queryset = Address.objects.all()


class AddressDeleteView(generics.DestroyAPIView):
    """
    Vue pour supprimer une adresse (admin seulement)
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAdminUser]
    queryset = Address.objects.all()
