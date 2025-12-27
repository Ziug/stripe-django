from django.contrib import admin
from .models import Item, Order

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'price']
    list_filter = ['name', 'description', 'price']
    search_fields = ['name', 'description']
    
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'total_sum')