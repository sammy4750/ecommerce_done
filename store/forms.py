from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import authenticate
from django import forms
from django.contrib.auth.models import User
from .models import Customer, ShippingAddress


class Userlogin(forms.ModelForm):
    password = forms.CharField(label='Password',widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username','password')

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        if not authenticate(username=username,password=password):
            raise forms.ValidationError("Invalid Credentials")

class Register(UserCreationForm):

    class Meta:
        model = User
        fields = ('first_name','last_name','username','email','password1','password2')

class CustomerForm(forms.ModelForm):
    mobile = forms.IntegerField(label='mobile')

    class Meta:
        model = Customer
        fields = ("mobile",)

class AddressForm(forms.ModelForm):
    # address = forms.CharField(label='address1')

    class Meta:
        model = ShippingAddress
        fields = ("address1","address2","city","state","zipcode","country",)

class EditBasicProfile(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username","first_name","last_name","email",]

    # def save(self, user=None):
    #     user_profile = super(editbasicprofile, self).save(commit=False)
    #     if user:
    #         user_profile.user = user
    #     user_profile.save()
    #     return user_profile