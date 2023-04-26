from django.urls import path
from . import views

app_name = 'coupon'


urlpatterns = [
    path('wishlist/', views.WishListView.as_view(), name='wishlist'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove_coupon/', views.remove_coupon, name='remove_coupon'),
    path('remove_wishlist/<int:item_id>', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('add_cart_wishlist/<int:variant_id>', views.add_to_cart, name='add_cart_wishlist'),
    path('add_to_wishlist/<slug:product_slug>/<slug:size_slug>/', views.add_to_wishlist, name='add_to_wishlist'),
]