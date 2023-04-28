from django.urls import path
from .views import HomeView, Aboutview, CategoryListView, ProductListView, CustomerRegister, AddToCartView, UpdateUserView, PasswordChangeView, PanelView
from django.contrib.auth.views import LogoutView

from . import views

app_name = 'store'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', views.customer_login, name='login'),
    path('register/', CustomerRegister.as_view(), name='register'),
    path('verify/', views.verify_code , name='verify'),
    path('logout/', LogoutView.as_view(next_page='store:home'), name='logout'),
    path('about/', Aboutview.as_view(), name='about'),
    path('panel/', PanelView.as_view(), name='panel'),
    path('search/', views.search, name='search'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('panel/order/<int:order_number>', views.order_detail, name='order-deet'),
    path('panel/cancel_order/<int:order_number>', views.cancel_order, name='cancel-order'),
    path('edit_profile/', UpdateUserView.as_view(), name='edit_profile'),
    path('change_password/', PasswordChangeView.as_view() , name='change_password'),
    path('checkout/', views.checkout , name='checkout'),
    path('cart/add/<int:product_id>/', views.add_cart, name='add_to_cart'),
    path('cart/add/<int:product_id>/<int:variant_id>/', AddToCartView.as_view(), name='add_cart'),
    path('cart/remove/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('cart/remove_item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/', views.cart, name='cart'),
    path('category/', CategoryListView.as_view(), name='category'),
    path('get_price/', views.get_price, name='get_price'),
    path('category/product/', views.product_detail, name='product_detail'),
    path('category/<slug:categories_slug>/', ProductListView.as_view(), name='product_list_by_category'),
]
