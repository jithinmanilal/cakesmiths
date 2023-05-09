from django.urls import path
from .views import ProductList, CustomerList, ProductCreate, ProductUpdate, ProductDelete, AdminLogin
from .views import VariantList, VariantCreate, VariantUpdate, VariantDelete, CategoryList, CategoryCreate, CategoryUpdate, CategoryDelete
from .views import SizeList, SizeCreate, SizeUpdate, SizeDelete, OrderDetail, OrderUpdate, CouponList, CouponCreate, CouponUpdate, CouponDelete
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dash'),
    path('admin_login/', AdminLogin.as_view(), name='admin_login'),
    path('logout/', LogoutView.as_view(next_page='dashboard:admin_login'), name='logout'),
    path('variants/', VariantList.as_view(), name='variants'),
    path('order/', views.order_list, name='orders'),
    path('coupon/', CouponList.as_view(), name='coupons'),
    path('coupon-add/', CouponCreate.as_view(), name='coupon_add'),
    path('coupon-update/<int:pk>/', CouponUpdate.as_view(), name='coupon_update'),
    path('coupon-delete/<int:pk>/', CouponDelete.as_view(), name='coupon_delete'),
    path('order-detail/<int:order_number>/', OrderDetail.as_view(), name='order_detail'),
    path('order-update/<int:order_number>/', OrderUpdate.as_view(), name='order_update'),
    path('variant-add/', VariantCreate.as_view(), name='variant_add'),
    path('variant-update/<int:pk>/', VariantUpdate.as_view(), name='variant_update'),
    path('variant-delete/<int:pk>/', VariantDelete.as_view(), name='variant_delete'),
    path('categories/', CategoryList.as_view(), name='categories'),
    path('category-add/', CategoryCreate.as_view(), name='category_add'),
    path('category-update/<int:pk>/', CategoryUpdate.as_view(), name='category_update'),
    path('category-delete/<int:pk>/', CategoryDelete.as_view(), name='category_delete'),
    path('products/',ProductList.as_view(), name='products'),
    path('product-add/', ProductCreate.as_view(), name='product_add'),
    path('product-update/<int:pk>/', ProductUpdate.as_view(), name='product_update'),
    path('product-delete/<int:pk>/', ProductDelete.as_view(), name='product_delete'),
    path('sale-pdf/', views.Pdf.as_view(), name='sale_pdf'),
    path('sale-csv/', views.Csv.as_view(), name='sale_csv'),
    path('sizes/', SizeList.as_view(), name='sizes'),
    path('size-add/', SizeCreate.as_view(), name='size_add'),
    path('size-update/<int:pk>/', SizeUpdate.as_view(), name='size_update'),
    path('size-delete/<int:pk>/', SizeDelete.as_view(), name='size_delete'),
    path('customers/', CustomerList.as_view(), name='customer'),
    path('customer-status/<int:user_id>/', views.ToggleUserStatusView.as_view(), name='customer_status'),
]
