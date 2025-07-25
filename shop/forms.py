from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder':'Your name'}))
    email = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder':'Your email'}))
    message = forms.CharField(max_length=100, widget=forms.Textarea(attrs={'placeholder':'Your message'}))
