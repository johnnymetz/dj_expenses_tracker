from django.forms import ModelForm, TextInput, NumberInput, DateInput
from .models import Expense, Profile


class ExpenseForm(ModelForm):

    class Meta:
        model = Expense
        exclude = ['user']
        widgets = {
            'item': TextInput(attrs={'placeholder': 'Urban Plates'}),
            'cost': NumberInput(attrs={'placeholder': '12.00', 'min': '0'}),
            'date_purchased': DateInput(format='%m/%d/%Y')
        }


class ProfileForm(ModelForm):

    class Meta:
        model = Profile
        exclude = ['user']
        # help_texts = {
        #     'food_limit': 'Budget for eating out and grocery store items',
        #     'car_limit': 'Budget for gas and car maintenance',
        #     'entertainment_limit': 'Budget for partying, one-timers and gifts'
        # }

