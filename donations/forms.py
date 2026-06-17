from django import forms
from .models import DonationRequest, Donation, Category

class DonationRequestForm(forms.ModelForm):
    class Meta:
        model = DonationRequest
        fields = ['title', 'category', 'description', 'quantity_needed', 'priority', 'deadline', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Request Title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Detailed description of the requirement...', 'rows': 4}),
            'quantity_needed': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity needed (e.g. 50, 100)'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_quantity_needed(self):
        qty = self.cleaned_data.get('quantity_needed')
        if qty is not None and qty <= 0:
            raise forms.ValidationError("Quantity needed must be greater than zero.")
        return qty

class ItemDonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['quantity_donated']
        widgets = {
            'quantity_donated': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity to donate', 'min': 1}),
        }

    def clean_quantity_donated(self):
        qty = self.cleaned_data.get('quantity_donated')
        if qty is not None and qty <= 0:
            raise forms.ValidationError("Donated quantity must be greater than zero.")
        return qty

class MoneyDonationForm(forms.ModelForm):
    card_number = forms.CharField(max_length=19, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXXX XXXX XXXX XXXX'}))
    card_expiry = forms.CharField(max_length=5, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'}))
    card_cvv = forms.CharField(max_length=4, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'CVV'}))

    class Meta:
        model = Donation
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Donation amount ($)', 'min': 1, 'step': '0.01'}),
        }

    def clean_amount(self):
        amt = self.cleaned_data.get('amount')
        if amt is not None and amt <= 0:
            raise forms.ValidationError("Donation amount must be greater than zero.")
        return amt
