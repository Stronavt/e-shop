from datetime import datetime
from django.utils import timezone
from decimal import Decimal
from venv import logger

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from ecom_project import settings
import stripe

from .forms import CartForm, AddressForm, PromoCodeForm, StripePaymentForm
from .models import OrderItem, Payment, Product, Category, Address, Order, PromoCode, StripePayment
from .utils import get_or_set_order_session

import json
from django.contrib.auth.decorators import login_required
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.core.signing import Signer

#stripe.api_version = settings.STRIPE_API_VERSION

class ProductListView(generic.ListView):
    template_name = 'cart_templates/product_list.html'
    paginate_by = 6

    def get_queryset(self):
        queryset = Product.objects.all().order_by('-created')
        category = self.request.GET.get('category', None)

        if not category:
            return queryset
        return queryset.filter(
            Q(primary_categories__name=category) |
            Q(secondary_categories__name=category)
        ).distinct()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'categories': Category.objects.values('name')})
        return context


    
class ProductDetailView(generic.FormView):
    template_name = 'cart_templates/product_detail.html'
    form_class = CartForm

    def get_object(self):
        return get_object_or_404(Product, slug=self.kwargs['slug'])

    def get_success_url(self):
        return reverse('cart:cart_page')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product_id'] = self.get_object().id

        return kwargs

    def form_valid(self, form):
        order = get_or_set_order_session(self.request)
        product = self.get_object()

        item_filter = order.items.filter(product=product, color = form.cleaned_data['color'], size = form.cleaned_data['size'])

        if not item_filter.exists():
            new_item = form.save(commit=False)
            new_item.product = product
            new_item.order = order
            new_item.save()
        else:
            item = item_filter.first()
            item.quantity += int(form.cleaned_data['quantity'])
            item.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.get_object()
        return context


class IncreaseQuantityView(generic.View):
    @staticmethod
    def get(request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        if order_item.quantity < order_item.product.stock:
            order_item.quantity += 1
            order_item.save(update_fields=['quantity'])
        else:
            messages.info(request, 'Доступное количество товара достигнуто')  
         
        return redirect('cart:cart_page')
    

class DecreaseQuantityView(generic.View):
    @staticmethod
    def get(request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        if order_item.quantity <= 1:
            order_item.delete()
        else:
            order_item.quantity -= 1
            order_item.save(update_fields = ['quantity', ])
        return redirect('cart:cart_page')        


class RemoveItemView(generic.View):
    @staticmethod
    def get(request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        order_item.delete()
        return redirect('cart:cart_page')


class CartView(generic.View):
    template_name = 'cart_templates/cart.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['order'].promo_code = None
        context['order'].save()
        return render(request, self.template_name, context)
    
    def post(self, request):
        context = self.get_context_data()
        form = PromoCodeForm(request.POST, order=context['order'])

        if form.is_valid():
            promo_code = form.promo  # Полученный из формы промокод
            order = context['order']
            order.promo_code = promo_code
            order.save()
            context['discount'] = order.get_discount_amount()
            context['final_price'] = order.get_order_price_with_discount()
            context['promo_code_form'] = form
        else:
            context['promo_code_form'] = form
        return render(request, self.template_name, context)
    
    def get_context_data(self):
        order = get_or_set_order_session(self.request)

        return {
            "order": order,
            "order_items": order.items.all(),
            "promo_code_form": PromoCodeForm(order=order),
            "discount": order.get_discount_amount() or 0,
            "final_price": order.get_order_price_with_discount(),
        }            
        

    


class CheckoutView(generic.FormView):
    template_name = 'cart_templates/checkout.html'
    form_class = AddressForm

    def get_success_url(self):
        return reverse('cart:payment')

    def form_valid(self, form):
        order = get_or_set_order_session(self.request)

        selected_shipping_address = form.cleaned_data.get(
            'selected_shipping_address'
        )

        if selected_shipping_address:
            order.shipping_address = selected_shipping_address
        else:
            address = Address.objects.create(
                user=self.request.user,
                address_1=form.cleaned_data['shipping_address_1'],
                postcode=form.cleaned_data['shipping_postcode'],
                city=form.cleaned_data['shipping_city'],
            )
            order.shipping_address = address


        order.save()
        messages.info(self.request, "You have successfully added your addresses")
        return super(CheckoutView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CheckoutView, self).get_form_kwargs()
        if self.request.user.is_authenticated:
            try:
                user = self.request.user.__class__.objects.get(id=self.request.user.id, is_active=True)
                kwargs["user_id"] = user.id
            except self.request.user.__class__.DoesNotExist:
                logger.error(f"User  {self.request.user.id} not found in get_form_kwargs")
                kwargs["user_id"] = None  

        else:
            kwargs["user_id"] = None
        return kwargs


    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)
        context["order"] = get_or_set_order_session(self.request)
        return context


class PaymentView(generic.TemplateView):
    template_name: str = 'cart_templates/payment.html'

    def get_context_data(self, **kwargs):
        context = super(PaymentView, self).get_context_data(**kwargs)
        context['order'] = get_or_set_order_session(self.request)
        context['CALLBACK_URL'] = self.request.build_absolute_uri(
            location=reverse("cart:thanks")
        )
        
        return context




class ThankYouView(generic.TemplateView):
    template_name: str = 'cart_templates/thanks.html'


#страница заказа
class OrderDetailView(LoginRequiredMixin, generic.DetailView):
    template_name: str = 'order.html'
    queryset = Order.objects.all()
    context_object_name = 'order'


# для оплаты по PayPal
class ConfirmOrderView(generic.View):
    @staticmethod
    def post(request, *args, **kwargs):
        order = get_or_set_order_session(request)
        body = json.loads(request.body)

        Payment.objects.create(
            order=order,
            successful=True,
            raw_response=json.dumps(body),
            amount=float(body["purchase_units"][0]["amount"]["value"]),
            payment_method=Payment.PAYPAL_PAYMENT_METHOD,
        )

        order.ordered = True
        order.ordered_date = timezone.now()
        order.save(update_fields=['ordered', 'ordered_date', ])

        return JsonResponse({"data": "Success"})
    
    @staticmethod
    def get(request, *args, **kwargs):
        return JsonResponse({"data": "This endpoint only accepts POST requests."}, status=405)
    



@login_required
def payment_process(request):
    order_id = request.session.get('order_signed_id', None)

    if order_id is None:
        return redirect('cart:cart')
    signer = Signer()
    try:
        order_id = int(signer.unsign(order_id))
        order = get_object_or_404(Order, id=order_id, ordered=False)
    except (Signer.BadSignature, ValueError):
        logger.warning("Invalid signed_id in payment")
        return redirect('cart:cart')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(
                        reverse('cart:thanks'))

        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'line_items': []
        }

        order.ordered = True
        order.ordered_date = timezone.now()
        order.save(update_fields=['ordered', 'ordered_date', ])


        for item in order.items.all():
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item.order.get_total_order_price()* Decimal(100)),
                    'currency': 'rub',
                    'product_data': {
                        'name': item.product.title,
                    },
                },
                'quantity': item.quantity,
            })

        session = stripe.checkout.Session.create(**session_data)

        return redirect(session.url, code=303)

    else:
        return render(request, 'cart_templates/stripe_payment.html', locals())
