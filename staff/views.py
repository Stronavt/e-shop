from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views import generic



from cart.models import Order, Product, PromoCode
from staff.forms import ProductForm, PromoStaffForm
from staff.mixins import StaffMixins


class StaffPageView(LoginRequiredMixin, StaffMixins, generic.ListView):
    template_name = 'staff/staff.html'
    queryset = Order.objects.filter(ordered=False).order_by('-ordered_date')
    print('StaffPageView queryset: ', queryset)
    paginated_by = 20
    context_object_name = 'orders'


class ProductListView(LoginRequiredMixin, StaffMixins, generic.ListView):
    template_name = 'staff/product_list.html'
    queryset = Product.objects.all()
    paginate_by = 10
    context_object_name = 'products'


class ProductCreateView(LoginRequiredMixin, StaffMixins, generic.CreateView):
    template_name = 'staff/product_create.html'
    form_class = ProductForm

    def get_success_url(self):
        return reverse('staff:product-list')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, StaffMixins, generic.UpdateView):
    template_name = 'staff/product_create.html'
    form_class = ProductForm
    queryset = Product.objects.all()

    def get_success_url(self):
        return reverse('staff:product-list')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, StaffMixins, generic.DeleteView):
    template_name = 'staff/product_delete.html'
    queryset = Product.objects.all()

    def get_success_url(self):
        return reverse('staff:product-list')


class PromoListView(LoginRequiredMixin, StaffMixins, generic.ListView):
    template_name = 'staff/promo_list.html'
    queryset = PromoCode.objects.all()
    paginate_by = 10
    context_object_name = 'promocodes'


class PromoCreateView(LoginRequiredMixin, StaffMixins, generic.CreateView):
    template_name  = 'staff/promo_create.html'
    form_class = PromoStaffForm

    def get_success_url(self):
        return reverse('staff:promo-list')
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    

class PromoUpdateView(LoginRequiredMixin, StaffMixins, generic.UpdateView):
    template_name = 'staff/promo_create.html'
    form_class = PromoStaffForm
    queryset = PromoCode.objects.all()

    def get_success_url(self):
        return reverse('staff:promo-list')
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
class PromoDeleteView(LoginRequiredMixin, StaffMixins, generic.DeleteView):
    template_name = 'staff/promo_delete.html'
    queryset = PromoCode.objects.all()

    def get_success_url(self): 
        return reverse('staff:promo-list')       