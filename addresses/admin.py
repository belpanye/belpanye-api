from django.contrib import admin
from .models import Address, AddressService


class AddressServiceInline(admin.TabularInline):
    model = AddressService
    extra = 0
    fields = ['service_type', 'is_available', 'additional_info']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'type', 'city', 'country', 'is_active', 
        'is_default_warehouse', 'display_order'
    ]
    list_filter = ['type', 'country', 'is_active', 'is_default_warehouse']
    search_fields = ['name', 'city', 'address_line1']
    ordering = ['display_order', 'name']
    inlines = [AddressServiceInline]
    
    fieldsets = (
        ('🏢 Informations générales', {
            'fields': ('type', 'name', 'is_active', 'display_order')
        }),
        ('📍 Localisation', {
            'fields': (
                'country', 'city', 
                'address_line1', 'address_line2', 
                'postal_code'
            )
        }),
        ('📞 Contact', {
            'fields': ('phone', 'email', 'hours')
        }),
        ('⚙️ Configuration', {
            'fields': ('is_default_warehouse',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # S'assurer qu'il n'y a qu'un seul entrepôt par défaut
        if obj.is_default_warehouse and obj.type == 'warehouse':
            Address.objects.filter(
                type='warehouse', 
                is_default_warehouse=True
            ).exclude(pk=obj.pk).update(is_default_warehouse=False)
        
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('services')


@admin.register(AddressService)
class AddressServiceAdmin(admin.ModelAdmin):
    list_display = ['address', 'service_type', 'is_available']
    list_filter = ['service_type', 'is_available', 'address__type']
    search_fields = ['address__name', 'service_type']
