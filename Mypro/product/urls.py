from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('add_product/', views.add_product, name='add_product'),
    path('edit_products/', views.edit_products, name='edit_products'),
    path('editproduct/<int:product_id>/', views.editproduct, name='editproduct'),
    path('delete_products/', views.delete_products, name='delete_products'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('logout/', views.logout_view, name='logout'),
    path('customer_profile/', views.customer_profile, name='customer_profile'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('view_orders/', views.view_orders, name='view_orders'),
    path('checkout/', views.checkout, name='checkout'),
    path('rate_product/<int:product_id>/', views.rate_product, name='rate_product'),
    path('view_orders_admin/', views.view_orders_admin, name='view_orders_admin'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('manage_orders/', views.manage_orders, name='manage_orders'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('view_reviews/', views.view_reviews, name='view_reviews'),
    path('filter_by_category/<str:category_name>/', views.filter_by_category, name='filter_by_category'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)