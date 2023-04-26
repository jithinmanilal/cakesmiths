from django.urls import path
from . import views
from .views import AddAddress, ListAddress, EditAddress, DeleteAddress

app_name = 'orders'

urlpatterns = [
    path('place/', views.place_order, name='place_order'),
    path('payment/', views.payments, name='payment'),
    path('order_completed/', views.order_complete, name='order_complete'),
    path('order_pdf/<int:order_number>', views.OrderPdf.as_view(), name='order_pdf'),
    path('address/', ListAddress.as_view(), name='address'),
    path('address/add/', AddAddress.as_view(), name='add_address'),
    path('address/edit/<int:pk>', EditAddress.as_view(), name='edit_address'),
    path('address/delete/<int:pk>', DeleteAddress.as_view(), name='delete_address'),
]
