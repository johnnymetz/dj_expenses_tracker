from django.forms import ModelForm, TextInput, NumberInput, DateInput, Select
from .models import Expense


class ExpenseForm(ModelForm):

    class Meta:
        model = Expense
        # fields = ['item', 'cost', 'date_purchased', 'category', 'subcategory']
        fields = '__all__'
        widgets = {
            'item': TextInput(attrs={'class': 'form-control', 'placeholder': 'Urban Plates'}),
            'cost': NumberInput(attrs={'class': 'form-control', 'placeholder': '12.00', 'min': '0'}),
            'date_purchased': DateInput(attrs={'class': 'form-control'}),
            'category': Select(attrs={'class': 'form-control'}),
            'subcategory': Select(attrs={'class': 'form-control'})
        }
