from django import forms
from .models import ServiceChargePayments, TransformerLevyPayments, ChargesDefinition, PAY_STATUS
from ..structure.models import Houses
from ..residents.models import Residents


class Pay_Service_ChargeForm(forms.Form):
    resident = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ))

    payment_date = forms.DateField(
        input_formats=['%d-%m-%Y'],
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'id': 'datetimepicker12'
            }
        ))

    amount = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        ))

    payment_note = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control'
            }
        ))

    class meta:
        model = ServiceChargePayments
        fields = ('resident', 'payment_date', 'amount', 'payment_note')


class Pay_Transformer_LevyForm(forms.Form):
    resident = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'readonly': True
            }
        ))

    payment_date = forms.DateField(
        input_formats=['%d-%m-%Y'],
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'id': 'datetimepicker13'
            }
        ))

    amount = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        ))

    payment_note = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control'
            }
        ))

    class meta:
        model = TransformerLevyPayments
        fields = ('resident', 'payment_date', 'amount', 'payment_note')


class SearchForm(forms.Form):
    q1 = forms.ModelChoiceField(
        Houses.objects.all(),
        required=False,
        empty_label="__Select House To Search__",
        widget=forms.Select(
            attrs={
                'class': 'form-control form-select',
            }
        )
    )

    q2 = forms.ModelChoiceField(
        Residents.objects.all(),
        required=False,
        empty_label="__Select Resident To Search__",
        widget=forms.Select(
            attrs={
                'class': 'form-control form-select'

            }
        ))


class FilterForm(forms.Form):
    pass
