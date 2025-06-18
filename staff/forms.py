
from django import forms
from cart.models import Product, PromoCode
from django_flatpickr.widgets import DateTimePickerInput


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'image', 'description', 'price', 'stock', 'available_sizes', 'available_colors', 'primary_categories','secondary_categories' ]


class PromoStaffForm(forms.ModelForm):

    class Meta:
        model = PromoCode       
        fields = ['code', 'discount_type', 'discount_value', 'start_date', 'expiry_date', 'minimum_order_amount'] 
        widgets = {
            'start_date': DateTimePickerInput(attrs={'class': 'form-control'}),
            'expiry_date': DateTimePickerInput(attrs={'class': 'form-control'}),
            }

        