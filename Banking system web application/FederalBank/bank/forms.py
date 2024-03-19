from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, PasswordResetForm
from django.contrib.auth.models import User
from .models import Profile,Transaction
from phonenumber_field.formfields import PhoneNumberField
from datetime import date


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'username', "password1", "password2")

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('address', 'phone', 'company_name','birth_date')
        phone = PhoneNumberField()

    def clean_date_of_birth(self):
        error = False
        dob = self.cleaned_data['birth_date']
        today = date.today()
        if (dob.year + 18, dob.month, dob.day) > (today.year, today.month, today.day):
            error = True
        return error


class ResetPasswordFrom(forms.Form):
    password1 = forms.CharField()
    password2 = forms.CharField()

class ContractForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('contract_start_date', 'contract_end_date')

class TransactionForm(forms.Form):
    phone = PhoneNumberField()
    amount = forms.IntegerField()
    details = forms.CharField(required=False)

class TransactionIbanForm(forms.Form):
    iban = forms.CharField()
    amount = forms.IntegerField()
    details = forms.CharField(required=False)

class CodeForm(forms.Form):
    code = forms.CharField()

class DepositForm(forms.Form):
    number = forms.CharField()
    date = forms.CharField()
    cv = forms.CharField()
    name = forms.CharField()
    amount = forms.IntegerField()

class DateFilterForm(forms.Form):
    from_date = forms.DateTimeField()
    to_date = forms.DateTimeField()


class EditProfileForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        del self.fields['password']

    class Meta:
        model = User

        fields = (
            'email',
            'first_name',
            'last_name',
        )



GROUP_NAMES = (
    ('Administrator', 'Administrator'),
    ('SuportClient', 'SuportClient'),
    ('Client', 'Client')
)

class SimpleForm(forms.Form):
    choice = forms.ChoiceField(required=True, choices=GROUP_NAMES)