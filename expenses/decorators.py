from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


def user_expense_required(func):
    def wrap(request, *args, **kwargs):
        query_list = request.user.expense_set.all()
        if query_list:
            return func(request, *args, **kwargs)
        else:
            messages.info(request, 'Please add an expense to get started!')
            return redirect(reverse('expenses:add_expense'))
    return wrap
