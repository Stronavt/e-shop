from . import views
from django.urls import path


urlpatterns = [
    path('', views.StaffPageView.as_view(), name='staff_page'),
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('create/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
    path('promo/', views.PromoListView.as_view(), name='promo-list'),
    path('promo/create/', views.PromoCreateView.as_view(), name='promo-create'),
    path('promo/<pk>/update/', views.PromoUpdateView.as_view(), name='promo-update'),
    path('promo/<pk>/delete/', views.PromoDeleteView.as_view(), name='promo-delete'),

]

app_name = 'staff'

