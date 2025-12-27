from .views import ItemDetailView, create_checkout_session, add_to_order, OrderDetailView,create_order_checkout_session, add_test_items
from django.urls import path


urlpatterns = [
    path('item/<int:pk>', ItemDetailView.as_view(), name='item-detail'),
    path('buy/<int:pk>', create_checkout_session, name='buy-item'),
    
    path('add_to_order/<int:item_id>', add_to_order, name='add_to_order'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order_detail'),
    path('buy_order/<int:pk>', create_order_checkout_session, name='buy_order'),
    
    
    path('testing_adding', add_test_items),
]