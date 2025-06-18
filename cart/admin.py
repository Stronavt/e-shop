from django.contrib import admin

from cart.models import Product, Order, OrderItem, Category, SizeVariation, ColorVariation , PromoCode, Address

#from ecom_project.cart.models import SizeVariation, ColorVariation , PromoCode, Address


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'price']



admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Category)
admin.site.register(SizeVariation)
admin.site.register(ColorVariation)
admin.site.register(PromoCode)
admin.site.register(Address)
