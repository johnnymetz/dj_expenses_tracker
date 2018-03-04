from .models import Expense
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


def expense_required(func):
    def wrap(request, *args, **kwargs):
        user_expenses = Expense.objects.all()
        print(user_expenses)
        if user_expenses:
            return func(request, *args, **kwargs)
        else:
            messages.info(request, 'Please add an expense to get started!')
            return redirect(reverse('expenses:add_expense'))
    return wrap
