from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import ShippingRate, Shipment, Payment
from .serializers import (
    ShippingRateSerializer,
    ShipmentSerializer,
    ShipmentCreateSerializer,
    ShipmentUpdateSerializer,
    PaymentSerializer,
    PaymentCreateSerializer
)

class ShippingRateListView(generics.ListAPIView):
    queryset = ShippingRate.objects.filter(is_active=True)
    serializer_class = ShippingRateSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def calculate_shipping_cost(request):
    weight = request.data.get('weight')
    shipping_type = request.data.get('shipping_type')
    
    if not weight or not shipping_type:
        return Response(
            {'error': 'Poids et type d\'expédition requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        weight = float(weight)
        rate = ShippingRate.objects.filter(
            shipping_type=shipping_type,
            min_weight__lte=weight,
            max_weight__gte=weight,
            is_active=True
        ).first()
        
        if rate:
            shipping_cost = rate.price_per_kg * weight
            return Response({
                'shipping_cost': shipping_cost,
                'rate': ShippingRateSerializer(rate).data
            })
        else:
            return Response(
                {'error': 'Aucun tarif disponible pour ce poids'},
                status=status.HTTP_404_NOT_FOUND
            )
    except ValueError:
        return Response(
            {'error': 'Poids invalide'},
            status=status.HTTP_400_BAD_REQUEST
        )

class ShipmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Shipment.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ShipmentCreateSerializer
        return ShipmentSerializer

class ShipmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Shipment.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ShipmentUpdateSerializer
        return ShipmentSerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_payment(request, shipment_id):
    shipment = get_object_or_404(
        Shipment,
        id=shipment_id,
        user=request.user,
        status='pending'
    )
    
    serializer = PaymentCreateSerializer(
        data=request.data,
        context={'shipment': shipment}
    )
    
    if serializer.is_valid():
        payment = serializer.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def confirm_payment(request, payment_id):
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        shipment__user=request.user,
        status='pending'
    )
    
    transaction_id = request.data.get('transaction_id')
    if transaction_id:
        payment.transaction_id = transaction_id
        payment.status = 'completed'
        payment.completed_at = timezone.now()
        payment.save()
        
        shipment = payment.shipment
        shipment.status = 'paid'
        shipment.paid_at = timezone.now()
        shipment.save()
        
        return Response({
            'message': 'Paiement confirmé',
            'payment': PaymentSerializer(payment).data
        })
    
    return Response(
        {'error': 'ID de transaction requis'},
        status=status.HTTP_400_BAD_REQUEST
    )

class PaymentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        return Payment.objects.filter(shipment__user=self.request.user)

class PaymentDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        return Payment.objects.filter(shipment__user=self.request.user)

# Vues admin
class AdminShipmentListView(generics.ListAPIView):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminShipmentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentUpdateSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminShippingRateListCreateView(generics.ListCreateAPIView):
    queryset = ShippingRate.objects.all()
    serializer_class = ShippingRateSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminShippingRateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShippingRate.objects.all()
    serializer_class = ShippingRateSerializer
    permission_classes = [permissions.IsAdminUser]
