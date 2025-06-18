from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from cart.models import Order

from shop.forms import ContactForm


class HomePageView(generic.TemplateView):
    template_name = 'index.html'


class ProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'orders': Order.objects.filter(user=self.request.user, ordered=True)})
        return context


class ContactView(generic.FormView):
    template_name = 'contact.html'
    form_class = ContactForm

    def get_success_url(self):
        return reverse('contact')

    def form_valid(self, form):
        messages.info(self.request, 'Thanks for getting in touch.')
        name = form.cleaned_data.get('name')
        email = form.cleaned_data.get('email')
        message = form.cleaned_data.get('message')

        full_message = f"""
        Received message from {name} , {email}
        -------------------------


        {message}

        """
        send_mail(
            subject='Receiver contact from submission',
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.NOTIFY_EMAIL]  # или = [email]
        )
        return super().form_valid(form)
