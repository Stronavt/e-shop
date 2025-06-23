from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.CartView.as_view(), name='cart_page'),
    path('shop/', views.ProductListView.as_view(), name='product-list'),
    path('shop/<slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('thank-you/', views.ThankYouView.as_view(), name='thanks'),
    path('orders/<pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('increase-quantity/<pk>/', views.IncreaseQuantityView.as_view(), name='increase-quantity'),
    path('decrease-quantity/<pk>/', views.DecreaseQuantityView.as_view(), name='decrease-quantity'),
    path('remove-item/<pk>/', views.RemoveItemView.as_view(), name='remove-item'), 
    path('payment/', views.PaymentView.as_view(),  name='payment'),
    path('confirm-order/', view=views.ConfirmOrderView.as_view(), name='confirm-order'),
    path('payment/stripe/', views.payment_process, name='payment-stripe'),    

]
app_name='cart'

