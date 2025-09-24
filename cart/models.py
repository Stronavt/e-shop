from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class SizeVariation(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ColorVariation(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


def product_image_upload(instance, filename):
    now = timezone.now()
    slug = slugify(instance.title)
    return f'product_images/{now.year}/{now.month}/{now.day}/{slug}_{filename}'

class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    stock = models.IntegerField(default=0)
    active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=product_image_upload, default='product_images/default.png')
    available_sizes = models.ManyToManyField(SizeVariation, blank=True)
    available_colors = models.ManyToManyField(ColorVariation, blank=True)
    secondary_categories = models.ManyToManyField(to=Category, blank=True)
    price = models.PositiveIntegerField(default=0)
    primary_categories = models.ForeignKey(to=Category, on_delete=models.CASCADE, related_name='primary_products', blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(value=self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('cart:product-detail', kwargs={'slug':self.slug})

    def get_update_url(self):
        return reverse('staff:product-update', kwargs={'pk':self.pk})

    def get_delete_url(self):
        return reverse('staff:product-delete', kwargs={'pk':self.pk})

    def get_price(self):
        return self.price


    @property
    def in_stock(self):
        return self.stock > 0


class PromoCode(models.Model):
    CODE_TYPE_CHOICES = [
        ('fixed', 'Fixed amount'),
        ('percent', 'Percentage')
    ]
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=CODE_TYPE_CHOICES, default='fixed')
    discount_value = models.PositiveIntegerField(help_text='for fixed - amount in rubles, for percent - integer 1-100')
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    minimum_order_amount = models.PositiveIntegerField(default=0, help_text="In rubles")

    def is_valid(self):
        now = timezone.now()
        if not self.active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.expiry_date and now > self.expiry_date:
            return False
        return True

    def __str__(self):
        return f'{self.code} ({self.get_discount_display()})'

    def get_discount_display(self):
        return f'{self.discount_value}{"%" if self.discount_type == "percent" else "₽"}'


class Address(models.Model):
    DELIVERY_COUNTRIES = [
        ('ru', 'Russian'),
        ('ge', "Georgia"),
        ('de', 'Germany'),
        ('fr', 'France'),
        ('tr', 'Turkey')
    ]

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    country = models.CharField(max_length=50, choices=DELIVERY_COUNTRIES)
    city = models.CharField(max_length=50)
    postcode = models.CharField(max_length=10, validators=[
        RegexValidator(regex='^\d+$', message='Postcode must be numeric')])
    address_1 = models.CharField(max_length=150)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return ', '.join([self.address_1, self.city, self.country])


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(null=True, blank=True)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(to= Address, on_delete=models.SET_NULL, blank=True, null=True, related_name='shipping_address')
    promo_code = models.ForeignKey(to=PromoCode,
                                   on_delete=models.SET_NULL, blank=True, null=True, related_name='orders')

    def __str__(self):
        return self.reference_number

    @property
    def reference_number(self):
        return f'order - {self.pk} - {self.user}'

    def get_raw_total_order_price(self) -> int:
        total = sum(item.get_raw_total_item_price() for item in self.items.all())
        return total

    def get_discount_amount(self):
        if not self.promo_code or not self.promo_code.is_valid():
            return 0
        total = self.get_raw_total_order_price()

        if total < self.promo_code.minimum_order_amount:
            return 0
        if self.promo_code.discount_type == 'fixed':
            return min(self.promo_code.discount_value, total)
        
        elif self.promo_code.discount_type == 'percent':
            return total * self.promo_code.discount_value // 10


    def get_order_price_with_discount(self) -> str:
        total = self.get_raw_total_order_price()
        discount = self.get_discount_amount()


        if discount is None or discount == 0:
            return total
        else:   
            return max(total - discount, 0)

    def get_total_order_price(self):
        return self.get_order_price_with_discount()
    


class OrderItem(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.ForeignKey(to=SizeVariation, on_delete=models.CASCADE, null=True, blank=True)
    color = models.ForeignKey(to=ColorVariation, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(to=Order, related_name='items', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.quantity} x {self.product.title}'

    def get_raw_total_item_price(self) -> float:
        return self.quantity * self.product.price

    def get_total_item_price(self) -> str:
        return self.get_raw_total_item_price()
    



class Payment(models.Model):
    PAYPAL_PAYMENT_METHOD = 'PayPal'
    TBANK_PAYMENT_METHOD = 'T-Pay'
    PAYMENT_METHODS = (
        (PAYPAL_PAYMENT_METHOD, 'PayPal'),
        (TBANK_PAYMENT_METHOD, 'T-Pay')
    )
    

    amount = models.FloatField()
    raw_response = models.TextField()
    successful = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, related_name='payments')

    def __str__(self):
        return self.reference_number

    @property
    def reference_number(self):
        return f'{self.order}-{self.pk}'


class StripePayment(models.Model):
    amount = models.FloatField(default=0)
    successful = models.BooleanField(default=False)
    payment_intent_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(
        to=Order,
        on_delete=models.CASCADE,
        related_name='stripe_payments',
    )

    def __str__(self) -> str:
        return self.reference_number

    @property
    def reference_number(self):
        return f"STRIPE-payment-{self.order}-{self.pk}"        