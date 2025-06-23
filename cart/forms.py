from datetime import timezone
from django import forms

from django import forms
from django.contrib.auth import get_user_model

from .models import Product, PromoCode, SizeVariation, ColorVariation, OrderItem, Address
User = get_user_model()


class CartForm(forms.ModelForm):
    size = forms.ModelChoiceField(queryset=SizeVariation.objects.none(), required=False)
    color = forms.ModelChoiceField(queryset=ColorVariation.objects.none(), required=False)


    class Meta:
        model = OrderItem
        fields = ( 'color', 'size')

    def __init__(self, *args, **kwargs):
        self.product_id = kwargs.pop('product_id', None)
        product = Product.objects.get(id=self.product_id)
        super().__init__(*args, **kwargs)
        

        if product:
            size_options = {
                'clothing': ['XS', 'S', 'M', 'L', 'XL'],
                'shoes': ['36', '36.5', '37', '37.5', '38', '38.5', '39', '39.5', '40', '40.5', '41', '41.5', '42']
            }

            category_name = product.primary_categories.name.lower() if product.primary_categories else None

            if category_name == 'accessories':
                self.fields['size'].required = False
                self.fields['color'].required = False

                self.fields['size'].queryset = SizeVariation.objects.all()
                self.fields['color'].queryset = ColorVariation.objects.all()

                self.fields['size'].initial = SizeVariation.objects.get(name='one size')
                self.fields['color'].initial = ColorVariation.objects.get(name='one color')

                self.fields['size'].widget.attrs['disabled'] = 'disabled'
                self.fields['color'].widget.attrs['disabled'] = 'disabled'
                
            elif category_name in size_options:
                self.fields['size'].queryset = product.available_sizes.filter(name__in=size_options[category_name])
                self.fields['color'].queryset = product.available_colors.all()

            if category_name != 'accessories':
                self.fields['size'].required = True
                self.fields['color'].required = True      

        
class AddressForm(forms.Form):

    shipping_country = forms.ChoiceField(choices=Address.DELIVERY_COUNTRIES)
    shipping_city = forms.CharField(required=False)
    shipping_postcode = forms.CharField(required=False)

    shipping_address_1 = forms.CharField(required=False)

    selected_shipping_address = forms.ModelChoiceField(queryset=Address.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)

        user = User.objects.get(id=user_id)
        shipping_address_queryset = Address.objects.filter(user=user)

        self.fields['selected_shipping_address'].queryset = shipping_address_queryset

    def clean(self):
        data = self.cleaned_data

        selected_shipping_address = data.get('selected_shipping_address', None)
        if selected_shipping_address is None:
            if not data.get('shipping_address_1', None):
                self.add_error(
                    "shipping_address_1",
                    "Please fill in this field"
                )
            if not data.get('shipping_postcode', None):
                self.add_error(
                    "shipping_postcode",
                    "Please fill in this field",
                )
            if not data.get('shipping_city', None):
                self.add_error("shipping_city", "Please fill in this field")



class PromoCodeForm(forms.Form):
    code = forms.CharField(max_length=50, label='Промокод')


    def __init__(self, *args, **kwargs):
        # передаем заказ в форму
        self.order = kwargs.pop('order', None)
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data.get('code')
        promo = PromoCode.objects.filter(code__iexact=code).first()
        if not promo or not promo.is_valid():
            raise forms.ValidationError("Промокод не найден или не действителен.")

        
        self.promo = promo  # Сохраняем для использования позже
        return code



class StripePaymentForm(forms.Form):
    selectedCard = forms.CharField()